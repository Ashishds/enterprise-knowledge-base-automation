"""
Secrets Seeding Script (Phase 1.12).

Reads a local .env file and seeds secrets to AWS Secrets Manager under
ekba/<env>/<secret_name>.

STRICT SECURITY RULE (CLAUDE.md §3 Rule 2):
"NEVER delete an AWS Secrets Manager secret. Not with delete-secret, not with
--force-delete-without-recovery, not via Terraform destroy, not 'temporarily'."

This script implements ONLY create_secret and put_secret_value operations.
It contains NO delete path.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


def parse_env_file(env_path: Path) -> dict[str, str]:
    """Parse key-value pairs from a .env file."""
    secrets = {}
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found at {env_path}")

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and val:
                secrets[key] = val
    return secrets


def seed_secrets(env_name: str, env_file_path: str) -> None:
    """Seed secrets from env file into AWS Secrets Manager."""
    secrets = parse_env_file(Path(env_file_path))
    raw_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1") or "us-east-1"
    region = raw_region.strip().replace("\r", "").replace("\n", "")
    client = boto3.client("secretsmanager", region_name=region)

    print(f"[*] Seeding {len(secrets)} secrets for environment '{env_name}' in region '{region}'...")


    for key, value in secrets.items():
        secret_id = f"ekba/{env_name}/{key.lower()}"
        try:
            client.create_secret(
                Name=secret_id,
                SecretString=value,
                Tags=[
                    {"Key": "Project", "Value": "ekba"},
                    {"Key": "Environment", "Value": env_name},
                ],
            )
            print(f"  [+] Created secret: {secret_id}")
        except client.exceptions.ResourceExistsException:
            client.put_secret_value(
                SecretId=secret_id,
                SecretString=value,
            )
            print(f"  [*] Updated secret value: {secret_id}")
        except ClientError as err:
            print(f"  [!] Failed to seed secret {secret_id}: {err}")


if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    path = sys.argv[2] if len(sys.argv) > 2 else "backend/.env"
    seed_secrets(env, path)
