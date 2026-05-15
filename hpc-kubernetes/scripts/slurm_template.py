from config import (
    MINIO_ENDPOINT,
    MINIO_BUCKET,
    JOB_SCRIPT,
    NAMD_SIF,
    SLURM_PARTITION,
    CPUS_PER_TASK,
    GPU_COUNT,
)


def make_slurm_script(dataset: str, namd_config: str, hpc_workdir: str) -> str:
    return f"""#!/bin/bash
#SBATCH --job-name=namd_cuda_{dataset}
#SBATCH --partition={SLURM_PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={CPUS_PER_TASK}
#SBATCH --gres=gpu:{GPU_COUNT}
#SBATCH --time=00:30:00
#SBATCH --output=namd_cuda_%j.out
#SBATCH --error=namd_cuda_%j.err

set -uo pipefail

MINIO_ENDPOINT="{MINIO_ENDPOINT}"
MINIO_BUCKET="{MINIO_BUCKET}"
DATASET="{dataset}"
NAMD_CONFIG="{namd_config}"
NAMD_SIF="{NAMD_SIF}"
HPC_WORKDIR="{hpc_workdir}"

JOB_ID="${{SLURM_JOB_ID}}"
RUN_PREFIX="runs/${{JOB_ID}}"

LOCAL_BASE="${{TMPDIR:-/tmp}}/namd_cuda_${{JOB_ID}}"
INPUT_DIR="${{LOCAL_BASE}}/input"
OUTPUT_DIR="${{LOCAL_BASE}}/outputs"
LOG_DIR="${{LOCAL_BASE}}/logs"
META_DIR="${{LOCAL_BASE}}/metadata"

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR" "$LOG_DIR" "$META_DIR"

AWS_BIN="$(command -v aws || true)"

if [ -z "$AWS_BIN" ]; then
  if [ -x "$HOME/bin/aws" ]; then
    AWS_BIN="$HOME/bin/aws"
  elif [ -x "$HOME/aws-cli/v2/current/bin/aws" ]; then
    AWS_BIN="$HOME/aws-cli/v2/current/bin/aws"
  else
    echo "[ERROR] aws command not found" | tee "$LOG_DIR/aws_error.log"
    exit 1
  fi
fi

export AWS_CONFIG_FILE="$LOCAL_BASE/aws_config"
cat > "$AWS_CONFIG_FILE" << AWS_CONFIG_EOF
[default]
s3 =
    multipart_threshold = 5GB
    multipart_chunksize = 64MB
AWS_CONFIG_EOF

upload_results() {{
  EXIT_CODE="$?"

  echo "$EXIT_CODE" > "$META_DIR/exit_code.txt"

  cat > "$META_DIR/metadata.json" << META_EOF
{{
  "job_id": "${{JOB_ID}}",
  "job_name": "${{SLURM_JOB_NAME}}",
  "dataset": "${{DATASET}}",
  "node": "$(hostname)",
  "exit_code": "${{EXIT_CODE}}",
  "s3_input": "s3://${{MINIO_BUCKET}}/${{DATASET}}/",
  "s3_run_prefix": "s3://${{MINIO_BUCKET}}/${{RUN_PREFIX}}/"
}}
META_EOF

  echo "[JOB] Uploading logs, outputs and metadata to S3-compatible storage"
  "$AWS_BIN" --endpoint-url "$MINIO_ENDPOINT" s3 cp --recursive "$LOG_DIR/" "s3://$MINIO_BUCKET/$RUN_PREFIX/logs/" || true
  "$AWS_BIN" --endpoint-url "$MINIO_ENDPOINT" s3 cp --recursive "$OUTPUT_DIR/" "s3://$MINIO_BUCKET/$RUN_PREFIX/outputs/" || true
  "$AWS_BIN" --endpoint-url "$MINIO_ENDPOINT" s3 cp --recursive "$META_DIR/" "s3://$MINIO_BUCKET/$RUN_PREFIX/metadata/" || true

  rm -rf "$LOCAL_BASE" || true
  exit "$EXIT_CODE"
}}

trap upload_results EXIT

echo "[JOB] Running on: $(hostname)" | tee "$LOG_DIR/job.log"
date | tee -a "$LOG_DIR/job.log"

echo "[JOB] Loading temporary AWS/S3 credentials" | tee -a "$LOG_DIR/job.log"
source "$HPC_WORKDIR/sts_credentials.env"

echo "[JOB] Checking credential variables" | tee -a "$LOG_DIR/job.log"
echo "AWS_ACCESS_KEY_ID length: ${{#AWS_ACCESS_KEY_ID}}" | tee -a "$LOG_DIR/job.log"
echo "AWS_SESSION_TOKEN length: ${{#AWS_SESSION_TOKEN}}" | tee -a "$LOG_DIR/job.log"

echo "[JOB] Using AWS_BIN=$AWS_BIN" | tee -a "$LOG_DIR/job.log"
"$AWS_BIN" --version | tee "$LOG_DIR/aws_version.log"

echo "[JOB] Listing input bucket" | tee -a "$LOG_DIR/job.log"
"$AWS_BIN" --endpoint-url "$MINIO_ENDPOINT" s3 ls "s3://$MINIO_BUCKET/" | tee "$LOG_DIR/s3_ls.log"

echo "[JOB] Downloading dataset: s3://$MINIO_BUCKET/$DATASET/" | tee -a "$LOG_DIR/job.log"
"$AWS_BIN" --endpoint-url "$MINIO_ENDPOINT" s3 cp --recursive \\
  "s3://$MINIO_BUCKET/$DATASET/" \\
  "$INPUT_DIR/" | tee "$LOG_DIR/download.log"

echo "[JOB] Input files:" | tee -a "$LOG_DIR/job.log"
find "$INPUT_DIR" -maxdepth 2 -type f | sort | tee "$LOG_DIR/input_files.log"

echo "[JOB] Checking NAMD SIF" | tee -a "$LOG_DIR/job.log"
ls -lh "$NAMD_SIF" | tee "$LOG_DIR/namd_sif.log"

echo "[JOB] GPU info" | tee -a "$LOG_DIR/job.log"
nvidia-smi | tee "$LOG_DIR/nvidia_smi.log"

echo "[JOB] Starting NAMD CUDA run" | tee -a "$LOG_DIR/job.log"
cd "$INPUT_DIR"

env -u LD_PRELOAD apptainer run --nv "$NAMD_SIF" \\
  +p{CPUS_PER_TASK} +devices 0 "$NAMD_CONFIG" \\
  > "$LOG_DIR/namd.log" 2> "$LOG_DIR/namd.err"

echo "[JOB] NAMD finished successfully" | tee -a "$LOG_DIR/job.log"

echo "[JOB] Collecting output files" | tee -a "$LOG_DIR/job.log"

find "$INPUT_DIR" -maxdepth 1 -type f \\
  \\( -name "*.dcd" -o -name "*.coor" -o -name "*.vel" -o -name "*.xsc" -o -name "*.restart*" -o -name "*out*" -o -name "*.log" \\) \\
  -exec cp -v {{}} "$OUTPUT_DIR/" \\; | tee "$LOG_DIR/collect_outputs.log"

echo "[JOB] Done" | tee -a "$LOG_DIR/job.log"
date | tee -a "$LOG_DIR/job.log"
"""


def make_remote_script(
    hpc_workdir: str,
    cred_b64: str,
    dataset: str,
    namd_config: str,
) -> str:
    slurm_script = make_slurm_script(dataset, namd_config, hpc_workdir)

    return f"""set -euo pipefail

echo "[HPC login] Connected successfully"
hostname
whoami
pwd

echo "[HPC login] Creating working directory"
mkdir -p "{hpc_workdir}"
cd "{hpc_workdir}"

echo "[HPC login] Writing temporary STS credentials file"
echo "{cred_b64}" | base64 -d > sts_credentials.env
chmod 600 sts_credentials.env

echo "[HPC login] Checking credentials file"
ls -lh sts_credentials.env

echo "[HPC login] Writing Slurm job script"

cat > "{JOB_SCRIPT}" << 'SLURM_EOF'
{slurm_script}
SLURM_EOF

echo "[HPC login] Submitting job"
JOB_ID="$(sbatch --parsable "{JOB_SCRIPT}")"

echo "[HPC login] Job submitted: ${{JOB_ID}}"
echo "[HPC login] Waiting for job to finish..."

while squeue -h -j "$JOB_ID" | grep -q "$JOB_ID"; do
  sleep 10
done

sleep 3

echo "[HPC login] Job finished. Uploading login-node Slurm stdout/stderr to S3-compatible storage."

source ./sts_credentials.env

AWS_BIN="$(command -v aws || true)"
if [ -z "$AWS_BIN" ]; then
  if [ -x "$HOME/bin/aws" ]; then
    AWS_BIN="$HOME/bin/aws"
  elif [ -x "$HOME/aws-cli/v2/current/bin/aws" ]; then
    AWS_BIN="$HOME/aws-cli/v2/current/bin/aws"
  else
    echo "[HPC login ERROR] aws command not found"
    exit 1
  fi
fi

RUN_PREFIX="runs/${{JOB_ID}}"

if [ -f "namd_cuda_${{JOB_ID}}.out" ]; then
  "$AWS_BIN" --endpoint-url "{MINIO_ENDPOINT}" s3 cp \\
    "namd_cuda_${{JOB_ID}}.out" \\
    "s3://{MINIO_BUCKET}/${{RUN_PREFIX}}/login_logs/namd_cuda_${{JOB_ID}}.out" || true
fi

if [ -f "namd_cuda_${{JOB_ID}}.err" ]; then
  "$AWS_BIN" --endpoint-url "{MINIO_ENDPOINT}" s3 cp \\
    "namd_cuda_${{JOB_ID}}.err" \\
    "s3://{MINIO_BUCKET}/${{RUN_PREFIX}}/login_logs/namd_cuda_${{JOB_ID}}.err" || true
fi

echo
echo "======================================"
echo " Job completed"
echo " Job ID: ${{JOB_ID}}"
echo
echo " S3 output path:"
echo " s3://{MINIO_BUCKET}/runs/${{JOB_ID}}/"
echo
echo " Local Slurm files:"
echo " {hpc_workdir}/namd_cuda_${{JOB_ID}}.out"
echo " {hpc_workdir}/namd_cuda_${{JOB_ID}}.err"
echo "======================================"
"""
