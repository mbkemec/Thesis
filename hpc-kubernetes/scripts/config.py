from pathlib import Path


LOCAL_WORKDIR = Path("/tmp/hpc_job")

BRIDGE_USER = "<bridge-user>"
BRIDGE_HOST = "<bridge-host>"

HPC_HOST = "<hpc-login-host>"

MINIO_ENDPOINT = "<s3-compatible-endpoint>"
MINIO_BUCKET = "<bucket-name>"

JOB_SCRIPT = "namd_cuda_minio.job"

NAMD_SIF = "<path-to-namd-cuda-apptainer-image>"

SLURM_PARTITION = "<gpu-partition>"

CPUS_PER_TASK = "64"
GPU_COUNT = "1"


DATASETS = {
    "apoa1": {
        "namd_config": "apoa1.namd",
    },
    "stmv": {
        "namd_config": "stmv.namd",
    },
}
