import json
import os
import time

MAX_LOG_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def log_to_file(entry, chain: str, token: str):
    filename = f"~/.faucetbot/{chain.lower()}_{token.lower()}_log.jsonl"
    path = os.path.expanduser(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Rotate log file if too large
    if os.path.exists(path) and os.path.getsize(path) > MAX_LOG_SIZE_BYTES:
        timestamp = int(time.time())
        backup_path = f"{path}.{timestamp}.bak"
        os.rename(path, backup_path)
        print(f"[log rotate] Archived old log to {backup_path}")

    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")
