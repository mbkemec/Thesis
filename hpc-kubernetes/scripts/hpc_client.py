import os
import subprocess
import sys
import time

from config import BRIDGE_USER, BRIDGE_HOST, HPC_HOST


def run_remote_script(
    *,
    hpc_user: str,
    remote_script: str,
    max_attempts: int = 3,
    retry_sleep_seconds: int = 10,
) -> None:
    """
    Execute a remote script on the HPC login node through a bridge host.
    """

    ssh_cmd = [
        "ssh",
        "-A",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=20",
        "-o",
        "ServerAliveInterval=15",
        "-o",
        "ServerAliveCountMax=3",
        "-J",
        f"{BRIDGE_USER}@{BRIDGE_HOST}",
        f"{hpc_user}@{HPC_HOST}",
        "bash -s",
    ]

    for attempt in range(1, max_attempts + 1):
        print(
            f"[MASTER VM] Connecting to HPC login node "
            f"(attempt {attempt}/{max_attempts})"
        )

        process = subprocess.run(
            ssh_cmd,
            input=remote_script,
            text=True,
            check=False,
            env=os.environ.copy(),
        )

        if process.returncode == 0:
            print("[MASTER VM] Remote workflow completed successfully")
            return

        print(
            f"[WARNING] Remote workflow failed "
            f"(exit code: {process.returncode})"
        )

        if attempt < max_attempts:
            print(
                f"[MASTER VM] Retrying in "
                f"{retry_sleep_seconds} seconds..."
            )
            time.sleep(retry_sleep_seconds)

    print("[ERROR] Remote workflow failed after all retry attempts")
    sys.exit(process.returncode)
