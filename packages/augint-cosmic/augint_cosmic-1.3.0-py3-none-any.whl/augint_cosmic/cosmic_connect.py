#!/usr/bin/env python3
"""
cosmic_connect: Open SSM tunnels (SSH, RDP, Squid) to AWS instances.
"""

import os
import sys
import subprocess
from collections import defaultdict

import click
from dotenv import load_dotenv
import boto3

# Load .env if present (project dir > cwd > home)
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=False)


def _get_base_port(cli_value: int, env_var: str, default: int) -> int:
    """
    Resolve a port‐base value in order:
      1) CLI flag if provided
      2) .env file or environment variable
      3) built‐in default
    """
    if cli_value is not None:
        return cli_value
    val = os.getenv(env_var)
    if val:
        try:
            return int(val)
        except ValueError:
            click.echo(f"Invalid {env_var}={val!r}, must be integer", err=True)
            sys.exit(1)
    return default


@click.group()
@click.option(
    "--profile",
    "-p",
    envvar="AWS_PROFILE",
    help="AWS CLI profile to use (env: AWS_PROFILE)",
)
@click.pass_context
def cli(ctx, profile):
    """
    Top‐level command for the Cosmic Connect toolkit.
    """
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile


@cli.command()
@click.pass_context
def ls(ctx):
    """
    List all running AWS instances with a 'Cluster' tag, formatted as a table.
    """
    session = boto3.Session(profile_name=ctx.obj.get("profile"))
    ec2 = session.client("ec2")
    paginator = ec2.get_paginator("describe_instances")

    # collect only tagged instances
    instances: list[dict] = []
    for page in paginator.paginate():
        for r in page["Reservations"]:
            for inst in r["Instances"]:
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                if "Cluster" in tags:
                    instances.append(
                        {
                            "Cluster": tags["Cluster"],
                            "Name": tags.get("Name", "N/A"),
                            "InstanceId": inst["InstanceId"],
                        }
                    )

    if not instances:
        click.echo("No instances found with 'Cluster' tag.")
        return

    # group by cluster
    clusters: dict[str, list[dict]] = defaultdict(list)
    for inst in instances:
        clusters[inst["Cluster"]].append(inst)

    # compute column widths
    hdrs = ["Cluster", "Name", "Instance ID"]
    w_cluster = max(len(hdrs[0]), *(len(c) for c in clusters))
    w_name = max(
        len(hdrs[1]), *(len(i["Name"]) for grp in clusters.values() for i in grp)
    )
    w_id = max(
        len(hdrs[2]), *(len(i["InstanceId"]) for grp in clusters.values() for i in grp)
    )

    # header and separator
    header = f"{hdrs[0]:<{w_cluster}} │ {hdrs[1]:<{w_name}} │ {hdrs[2]:<{w_id}}"
    sep_line = "─" * len(header)

    click.echo(header)
    click.echo(sep_line)

    # print each cluster block
    for cluster_name in sorted(clusters):
        for inst in clusters[cluster_name]:
            click.echo(
                f"{cluster_name:<{w_cluster}} │ "
                f"{inst['Name']:<{w_name}} │ "
                f"{inst['InstanceId']:<{w_id}}"
            )
        click.echo(sep_line)


@cli.command()
@click.pass_context
def login(ctx):
    """
    Perform an SSO login so that AWS credentials are cached.

    Relies on AWS_PROFILE / SSO configuration in your ~/.aws/config.
    """
    profile = ctx.obj.get("profile")
    cmd = ["aws"]
    if profile:
        cmd += ["--profile", profile]
    cmd += ["sso", "login"]
    click.echo("Running: " + " ".join(cmd))
    subprocess.run(cmd, check=True)


@cli.command()
@click.argument("cluster_token", type=str)
@click.option("--ssh-base-port", type=int, help="Starting port for SSH tunnels")
@click.option("--rdp-base-port", type=int, help="Starting port for RDP tunnels")
@click.option("--squid-base-port", type=int, help="Starting port for Squid tunnels")
@click.option("--launch-ssh", is_flag=True, help="Immediately open SSH session")
@click.option("--launch-rdp", is_flag=True, help="Immediately open RDP session")
@click.option("--detach", is_flag=True, help="Fully background all tunnel processes")
@click.pass_context
def tunnel(
    ctx,
    cluster_token,
    ssh_base_port,
    rdp_base_port,
    squid_base_port,
    launch_ssh,
    launch_rdp,
    detach,
):
    """
    Open SSM tunnels to matching “dev” (SSH + Squid) and “dc1” (RDP) instances.

    Args:
        cluster_token (str):  Identifier after “dev.” or “dc1.” in the Name tag.
        ssh_base_port (int):  Local port to start SSH‐tunnel numbering at.
        rdp_base_port (int):  Local port to start RDP‐tunnel numbering at.
        squid_base_port (int): Local port to start Squid‐tunnel numbering at.
        launch_ssh (bool):    If True, immediately invoke SSH to localhost.
        launch_rdp (bool):    If True, immediately invoke RDP client to localhost.
        detach (bool):        If True, detach tunnels so the CLI returns immediately.

    Returns:
        List[str]: The AWS CLI start-session commands that were run.
    """
    profile = ctx.obj.get("profile")

    # 1) Ensure valid credentials (or prompt login on failure)
    sts_cmd = ["aws"]
    if profile:
        sts_cmd += ["--profile", profile]
    sts_cmd += ["sts", "get-caller-identity"]
    try:
        subprocess.run(
            sts_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        click.echo("AWS credentials missing/expired – running SSO login...", err=True)
        login(ctx)

    # 2) Resolve base ports
    ssh_base = _get_base_port(ssh_base_port, "COSMIC_SSH_BASE_PORT", 2222)
    rdp_base = _get_base_port(rdp_base_port, "COSMIC_RDP_BASE_PORT", 2389)
    squid_base = _get_base_port(squid_base_port, "COSMIC_SQUID_BASE_PORT", 3128)

    # 3) Discover matching instances
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    ec2 = session.client("ec2")
    filters = [
        {"Name": "instance-state-name", "Values": ["running"]},
        {
            "Name": "tag:Name",
            "Values": [f"dev.{cluster_token}.*", f"dc1.{cluster_token}.*"],
        },
    ]
    resp = ec2.describe_instances(Filters=filters)
    instances: dict[str, str] = {
        tag["Value"]: inst["InstanceId"]
        for res in resp.get("Reservations", [])
        for inst in res.get("Instances", [])
        for tag in inst.get("Tags", [])
        if tag["Key"] == "Name"
    }

    if not instances:
        click.echo(
            f"No instances found matching dev.{cluster_token}.* or dc1.{cluster_token}.*"
        )
        return

    # 4) Prepare detach kwargs if requested
    popen_kwargs = {}
    if detach:
        popen_kwargs.update(
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.DETACHED_PROCESS
        else:
            popen_kwargs["start_new_session"] = True

    # 5) Open tunnels
    ssh_ctr = ssh_base
    rdp_ctr = rdp_base
    squid_ctr = squid_base
    commands: list[str] = []

    for name, iid in sorted(instances.items()):
        if name.startswith("dev."):
            # SSH tunnel
            cmd_ssh = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={ssh_ctr},portNumber=22",
            ]
            commands.append(" ".join(cmd_ssh))
            subprocess.Popen(cmd_ssh, **popen_kwargs)
            if launch_ssh:
                subprocess.Popen(
                    [os.getenv("SSH", "ssh"), f"-p{ssh_ctr}", "ec2-user@localhost"],
                    **popen_kwargs,
                )
            ssh_ctr += 1

            # Squid tunnel
            cmd_squid = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={squid_ctr},portNumber=3128",
            ]
            commands.append(" ".join(cmd_squid))
            subprocess.Popen(cmd_squid, **popen_kwargs)
            squid_ctr += 1

        elif name.startswith("dc1."):
            # RDP tunnel
            cmd_rdp = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={rdp_ctr},portNumber=3389",
            ]
            commands.append(" ".join(cmd_rdp))
            subprocess.Popen(cmd_rdp, **popen_kwargs)
            if launch_rdp:
                subprocess.Popen(["mstsc", f"/v:localhost:{rdp_ctr}"], **popen_kwargs)
            rdp_ctr += 1

    # 6) Echo all commands for audit or copy/paste
    click.echo("\n".join(commands))
    return commands


if __name__ == "__main__":
    cli()
