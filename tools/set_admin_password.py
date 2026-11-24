"""CLI utility to configure the administrator credentials and password hash in .env.

Usage:
    python tools/set_admin_password.py
"""

import sys
import getpass
import secrets
from pathlib import Path
from typing import Optional
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_PATH = BASE_DIR / ".env"


def update_env_file(
    username: str,
    password_hash: str,
    env_path: Optional[Path] = None,
) -> None:
    """Updates or sets ADMIN_USERNAME and ADMIN_PASSWORD_HASH in .env.

    Ensures SECRET_KEY is present and non-empty.
    Preserves all existing comments, formatting, and other configuration lines intact.
    """
    target_path = env_path or DEFAULT_ENV_PATH
    lines = []
    if target_path.exists():
        lines = target_path.read_text(encoding="utf-8").splitlines()

    username_updated = False
    hash_updated = False
    secret_key_present = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("ADMIN_USERNAME="):
            new_lines.append(f"ADMIN_USERNAME={username}")
            username_updated = True
        elif stripped.startswith("ADMIN_PASSWORD_HASH="):
            new_lines.append(f"ADMIN_PASSWORD_HASH='{password_hash}'")
            hash_updated = True
        elif stripped.startswith("ADMIN_PASSWORD="):
            # Replace legacy plaintext ADMIN_PASSWORD line with ADMIN_PASSWORD_HASH
            if not hash_updated:
                new_lines.append(f"ADMIN_PASSWORD_HASH='{password_hash}'")
                hash_updated = True
        elif stripped.startswith("SECRET_KEY="):
            parts = line.split("=", 1)
            secret_val = parts[1].strip().strip("'\"") if len(parts) > 1 else ""
            if not secret_val:
                new_lines.append(f"SECRET_KEY={secrets.token_hex(32)}")
            else:
                new_lines.append(line)
            secret_key_present = True
        else:
            new_lines.append(line)

    if not secret_key_present:
        new_lines.append(f"SECRET_KEY={secrets.token_hex(32)}")

    if not username_updated:
        new_lines.append(f"ADMIN_USERNAME={username}")

    if not hash_updated:
        new_lines.append(f"ADMIN_PASSWORD_HASH='{password_hash}'")

    target_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main() -> None:
    """Interactive entry point for setting admin credentials."""
    try:
        username_input = input("Enter admin username [admin]: ").strip()
        username = username_input or "admin"

        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if len(password) < 8:
            print("Error: Password must be at least 8 characters long.", file=sys.stderr)
            sys.exit(1)

        if password != confirm_password:
            print("Error: Passwords do not match.", file=sys.stderr)
            sys.exit(1)

        password_hash = generate_password_hash(password)
        update_env_file(username, password_hash)

        print("Admin password saved. Restart the app.")
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
