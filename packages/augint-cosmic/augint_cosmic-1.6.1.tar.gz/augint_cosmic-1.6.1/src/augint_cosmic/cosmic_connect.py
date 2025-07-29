#!/usr/bin/env python3
"""
cosmic_connect: Open SSM tunnels (SSH, RDP, Squid) to AWS instances.
"""
from botocore.exceptions import ClientError

import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import click
from dotenv import load_dotenv
import boto3
import os
import sys
import subprocess
from collections import defaultdict


def get_instance_password(ec2_client, instance_id: str, key_path: str) -> str:
    """
    Fetches the encrypted Windows Administrator password for an EC2 instance
    and decrypts it using the given PEM key.

    Args:
        ec2_client: boto3 EC2 client
        instance_id: The EC2 instance ID
        key_path: Path to your private-key PEM (expanded/resolved)

    Returns:
        The plaintext Administrator password.

    Raises:
        RuntimeError: if no password data is yet available.
    """
    resp = ec2_client.get_password_data(InstanceId=instance_id)
    blob = resp.get("PasswordData", "")
    if not blob:
        raise RuntimeError(
            f"No password data yet for {instance_id}; try again in a minute."
        )

    # now decrypt
    return decrypt_password(blob, key_path)


def decrypt_password(encrypted_blob: str, key_path: str) -> str:
    """Decrypt an EC2 Windows password blob with the given private key PEM."""
    encrypted = base64.b64decode(encrypted_blob)
    with open(key_path, "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    decrypted = priv.decrypt(encrypted, padding=padding.PKCS1v15())
    return decrypted.decode("utf-8")


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
    """
    profile = ctx.obj.get("profile")
    cmd = ["aws"] + (["--profile", profile] if profile else []) + ["sso", "login"]
    click.echo("Running: " + " ".join(cmd))
    subprocess.run(cmd, check=True)


@cli.command()
@click.argument("cluster_token", type=str)
@click.option("--ssh-base-port", type=int, help="Starting port for SSH tunnels")
@click.option("--rdp-base-port", type=int, help="Starting port for RDP tunnels")
@click.option("--squid-base-port", type=int, help="Starting port for Squid tunnels")
@click.option("--launch-ssh", is_flag=True, help="Immediately open SSH session")
@click.option("--launch-rdp", is_flag=True, help="Immediately open RDP session")
@click.option(
    "--rdp-key",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="Path to your PEM private key for decrypting Windows Administrator password",
)
@click.option("--detach", is_flag=True, help="Fully background all tunnel processes")
@click.option(
    "--close",
    is_flag=True,
    help="Close existing SSM sessions for matching instances and exit",
)
@click.pass_context
def tunnel(
    ctx,
    cluster_token,
    ssh_base_port,
    rdp_base_port,
    squid_base_port,
    launch_ssh,
    launch_rdp,
    rdp_key,
    detach,
    close,
):
    """
    Open or close SSM tunnels to matching “dev” (SSH + Squid) and “dc1” (RDP) instances.

    Args:
        cluster_token (str):  Identifier after “dev.” or “dc1.” in the Name tag.
        ssh_base_port (int):  Local port to start SSH‐tunnel numbering at.
        rdp_base_port (int):  Local port to start RDP‐tunnel numbering at.
        squid_base_port (int): Local port to start Squid‐tunnel numbering at.
        launch_ssh (bool):    If True, immediately invoke SSH to localhost.
        launch_rdp (bool):    If True, immediately invoke RDP client to localhost.
        rdp_key (str):        Path to PEM key file to decrypt the Windows password (required if --launch-rdp).
        detach (bool):        If True, detach tunnels so the CLI returns immediately.
        close (bool):         If True, terminate active SSM sessions and exit.

    Returns:
        List[str]: The AWS CLI commands that were run.
    """
    profile = ctx.obj.get("profile")
    boto3_args = {"profile_name": profile} if profile else {}

    # discover matching instance IDs
    session = boto3.Session(**boto3_args)
    ec2 = session.client("ec2")
    resp = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {
                "Name": "tag:Name",
                "Values": [f"dev.{cluster_token}.*", f"dc1.{cluster_token}.*"],
            },
        ]
    )
    instances = {
        tag["Value"]: inst["InstanceId"]
        for res in resp.get("Reservations", [])
        for inst in res.get("Instances", [])
        for tag in inst.get("Tags", [])
        if tag["Key"] == "Name"
    }

    if not instances:
        click.echo(
            f"No instances matching dev.{cluster_token}.* or dc1.{cluster_token}.*"
        )
        return

    # --- CLOSE MODE ----------------------------------------------------------
    if close:
        ssm = session.client("ssm")
        for name, iid in instances.items():
            pages = ssm.get_paginator("describe_sessions").paginate(
                State="Active", Filters=[{"key": "Target", "value": iid}]
            )
            for page in pages:
                for sess in page.get("Sessions", []):
                    sid = sess["SessionId"]
                    try:
                        ssm.terminate_session(SessionId=sid)
                        click.echo(f"Terminated session {sid} ({name})")
                    except ClientError as e:
                        click.echo(f"Error terminating {sid}: {e}", err=True)
        return

    # --- OPEN MODE -----------------------------------------------------------
    sts = (
        ["aws"]
        + (["--profile", profile] if profile else [])
        + ["sts", "get-caller-identity"]
    )
    try:
        subprocess.run(
            sts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        click.echo("AWS creds expired/missing—running SSO login...", err=True)
        login(ctx)

    ssh_base = _get_base_port(ssh_base_port, "COSMIC_SSH_BASE_PORT", 2222)
    rdp_base = _get_base_port(rdp_base_port, "COSMIC_RDP_BASE_PORT", 2389)
    squid_base = _get_base_port(squid_base_port, "COSMIC_SQUID_BASE_PORT", 3128)

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

            if launch_rdp:
                # ensure they actually passed --rdp-key
                if not rdp_key:
                    click.echo(
                        "Error: --rdp-key is required when using --launch-rdp", err=True
                    )
                    sys.exit(1)

                # attempt to fetch & decrypt the Windows Administrator password
                try:
                    click.echo(f"[DEBUG] fetching password for {iid}…")
                    pwd = get_instance_password(ec2, iid, rdp_key)
                    click.echo("[DEBUG] successfully decrypted Administrator password")

                    # seed Windows credential store for this host:port
                    target = f"TERMSRV/localhost:{rdp_ctr}"
                    subprocess.run(
                        [
                            "cmdkey",
                            "/generic:" + target,
                            "/user:Administrator",
                            "/pass:" + pwd,
                        ],
                        check=True,
                        **popen_kwargs,
                    )
                    click.echo(f"[DEBUG] cmdkey stored credentials for {target}")
                except RuntimeError as e:
                    click.echo(f"Warning: {e}", err=True)
                except subprocess.CalledProcessError as e:
                    click.echo(
                        f"Warning: failed to seed creds via cmdkey: {e}", err=True
                    )

                # finally start the RDP client
                subprocess.Popen(["mstsc", f"/v:localhost:{rdp_ctr}"], **popen_kwargs)

            rdp_ctr += 1

    click.echo("\n".join(commands))
    return commands


if __name__ == "__main__":
    cli()
