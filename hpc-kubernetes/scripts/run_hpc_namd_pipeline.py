#!/usr/bin/env python3

import base64
import os
import shutil
import subprocess
import sys
from pathlib import Path

from config import (
    LOCAL_WORKDIR,
    DATASETS,
)

from slurm_template import make_remote_script
from hpc_client import run_remote_script


def run(cmd, *, shell=False, cwd=None, check=True, capture=False):
    printable = cmd if isinstance(cmd, str) else " ".join(cmd)
    print(f"[CMD] {printable}")

    return subprocess.run(
        cmd,
        shell=shell,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
        env=os.environ.copy(),
    )


def require_file(path: Path, message: str):
    if not path.exists():
        print(f"[ERROR] {message}: {path}")
        sys.exit(1)

    if path.is_file() and path.stat().st_size == 0:
        print(f"[ERROR] File is empty: {path}")
        sys.exit(1)


def setup_oidc_agent():
    print("[MASTER VM] Starting/using oidc-agent")

    result = run(
        ["oidc-agent-service", "use"],
        capture=True,
    )

    oidc_output = result.stdout

    for part in oidc_output.replace(";", "\n").splitlines():
        part = part.strip()

        if part.startswith("export "):
            part = part.replace("export ", "", 1).strip()

        if part.startswith("OIDC_SOCK="):
            value = part.split("=", 1)[1].strip().strip('"').strip("'")
            os.environ["OIDC_SOCK"] = value

        if part.startswith("OIDCD_PID="):
            value = part.split("=", 1)[1].strip().strip('"').strip("'")
            os.environ["OIDCD_PID"] = value

    if "OIDC_SOCK" not in os.environ:
        print("[ERROR] Could not parse OIDC_SOCK from oidc-agent-service output")
        print("----- oidc-agent-service output -----")
        print(oidc_output)
        print("-------------------------------------")
        sys.exit(1)

    print(f"[MASTER VM] OIDC_SOCK={os.environ['OIDC_SOCK']}")


def main():
    original_ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK", "")

    script_dir = Path(__file__).resolve().parent

    sts_script = script_dir / "login_sts.py"
    generated_env_file = script_dir / "sts_credentials.env"
    aws_env_file = LOCAL_WORKDIR / "sts_credentials.env"

    LOCAL_WORKDIR.mkdir(parents=True, exist_ok=True)

    print("======================================")
    print(" OIDC / S3 / HPC / NAMD CUDA workflow")
    print(" Modular Python implementation")
    print("======================================")

    oidc_shortname = input("Insert your oidc-agent shortname: ").strip()
    hpc_user = input("Insert your HPC username: ").strip()
    dataset = input("Dataset to run (apoa1/stmv): ").strip()

    if dataset not in DATASETS:
        print(f"[ERROR] Unsupported dataset: {dataset}")
        print(f"Allowed values: {', '.join(DATASETS.keys())}")
        sys.exit(1)

    namd_config = DATASETS[dataset]["namd_config"]

    hpc_workdir = input(
        "Insert remote HPC working directory: "
    ).strip()

    if not hpc_workdir:
        print("[ERROR] HPC working directory cannot be empty")
        sys.exit(1)

    print(f"[MASTER VM] Using HPC_WORKDIR={hpc_workdir}")

    setup_oidc_agent()

    print("[MASTER VM] Loading OIDC account")
    run(["oidc-add", oidc_shortname])

    print("[MASTER VM] Testing OIDC token")
    run(["oidc-token", oidc_shortname], capture=True)

    print("[MASTER VM] Getting temporary S3 credentials")

    require_file(sts_script, "STS script not found")

    run(
        ["python3", str(sts_script), "--oidc", oidc_shortname],
        cwd=script_dir,
    )

    require_file(
        generated_env_file,
        "Credential generation failed",
    )

    if aws_env_file.exists():
        aws_env_file.unlink()

    shutil.move(str(generated_env_file), str(aws_env_file))

    require_file(
        aws_env_file,
        "Credentials file is invalid",
    )

    print(f"[MASTER VM] Credentials saved in: {aws_env_file}")

    print("[MASTER VM] Restoring SSH agent socket")

    if original_ssh_auth_sock:
        os.environ["SSH_AUTH_SOCK"] = original_ssh_auth_sock

    print("[MASTER VM] Checking SSH agent keys")
    run(["ssh-add", "-l"], check=False)

    print("[MASTER VM] Encoding credentials")

    cred_b64 = base64.b64encode(
        aws_env_file.read_bytes()
    ).decode("utf-8")

    remote_script = make_remote_script(
        hpc_workdir=hpc_workdir,
        cred_b64=cred_b64,
        dataset=dataset,
        namd_config=namd_config,
    )

    run_remote_script(
        hpc_user=hpc_user,
        remote_script=remote_script,
    )

    print("[MASTER VM] Workflow completed successfully")


if __name__ == "__main__":
    main()
