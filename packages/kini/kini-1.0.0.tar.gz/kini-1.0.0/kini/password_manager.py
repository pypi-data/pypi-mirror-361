#!/usr/bin/env python3
"""
Secure Password Manager - Kini
A command-line password manager with encryption, hashing, backup, and search.
"""

import argparse
import base64
import getpass
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .mascot import show_mascot, welcome_message


class PasswordManager:
    def __init__(self, data_dir="~/.kini"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(exist_ok=True)

        self.db_file = self.data_dir / "passwords.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.master_hash_file = self.data_dir / "master.hash"
        self.salt_file = self.data_dir / "salt.key"

        self.cipher = None
        self.data = {"passwords": {}, "history": {}}

    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _hash_password(self, password: str) -> str:
        """Create SHA-256 hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet"""
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def _load_or_create_salt(self) -> bytes:
        """Load existing salt or create new one"""
        if self.salt_file.exists():
            with open(self.salt_file, "rb") as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, "wb") as f:
                f.write(salt)
            return salt

    def setup_master_password(self) -> bool:
        """Setup master password for first time use"""
        if self.master_hash_file.exists():
            return False

        print(welcome_message())
        print(
            "Please create a master password "
            "(this will be used to access all your passwords)"
        )

        while True:
            password = getpass.getpass("Master Password: ")
            confirm = getpass.getpass("Confirm Master Password: ")

            if password == confirm:
                break
            print("Passwords don't match. Please try again.")

        # Hash and store master password
        master_hash = self._hash_password(password)
        with open(self.master_hash_file, "w") as f:
            f.write(master_hash)

        # Setup encryption
        salt = self._load_or_create_salt()
        key = self._generate_key(password, salt)
        self.cipher = Fernet(key)

        # Initialize empty database
        self._save_data()

        print("Master password set successfully!")
        return True

    def authenticate(self) -> bool:
        """Authenticate user with master password"""
        if not self.master_hash_file.exists():
            return self.setup_master_password()

        # Load stored master password hash
        with open(self.master_hash_file, "r") as f:
            stored_hash = f.read().strip()

        # Get password from user
        password = getpass.getpass("Master Password: ")

        # Verify password
        if self._hash_password(password) != stored_hash:
            print("Invalid master password!")
            return False

        # Setup encryption
        salt = self._load_or_create_salt()
        key = self._generate_key(password, salt)
        self.cipher = Fernet(key)

        # Load existing data
        self._load_data()

        return True

    def _load_data(self):
        """Load and decrypt password database"""
        if self.db_file.exists():
            try:
                with open(self.db_file, "r") as f:
                    encrypted_data = f.read()

                if encrypted_data.strip():
                    decrypted_data = self._decrypt_data(encrypted_data)
                    self.data = json.loads(decrypted_data)
                else:
                    self.data = {"passwords": {}, "history": {}}
            except Exception as e:
                print(f"Error loading data: {e}")
                self.data = {"passwords": {}, "history": {}}
        else:
            self.data = {"passwords": {}, "history": {}}

    def _save_data(self):
        """Encrypt and save password database"""
        try:
            json_data = json.dumps(self.data, indent=2)
            encrypted_data = self._encrypt_data(json_data)

            with open(self.db_file, "w") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_password(self, service: str, username: str, password: str):
        """Add new password entry"""
        timestamp = datetime.now().isoformat()

        # Check if service already exists
        if service in self.data["passwords"]:
            # Move current password to history
            if service not in self.data["history"]:
                self.data["history"][service] = []

            old_entry = self.data["passwords"][service].copy()
            old_entry["changed_at"] = timestamp
            self.data["history"][service].append(old_entry)

        # Add new password
        self.data["passwords"][service] = {
            "username": username,
            "password": password,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        self._save_data()
        print(f"Password for '{service}' added successfully!")

    def get_password(self, service: str):
        """Retrieve password for a service"""
        if service not in self.data["passwords"]:
            print(f"No password found for '{service}'")
            return None

        entry = self.data["passwords"][service]
        print(f"\nService: {service}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")
        print(f"Created: {entry['created_at']}")
        print(f"Updated: {entry['updated_at']}")

        return entry

    def search_passwords(self, query: str):
        """Search passwords by service name"""
        matches = []
        query_lower = query.lower()

        for service in self.data["passwords"]:
            if query_lower in service.lower():
                matches.append(service)

        if not matches:
            print(f"No passwords found matching '{query}'")
            return

        print(f"\nFound {len(matches)} match(es) for '{query}':")
        for i, service in enumerate(matches, 1):
            print(f"{i}. {service}")

        if len(matches) == 1:
            print(f"\nShowing password for '{matches[0]}':")
            self.get_password(matches[0])
        else:
            choice = input(
                "\nEnter number to view password (or press Enter to cancel): "
            )
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                selected_service = matches[int(choice) - 1]
                self.get_password(selected_service)

    def list_passwords(self):
        """List all stored passwords"""
        if not self.data["passwords"]:
            print("No passwords stored yet.")
            return

        print(f"\nStored passwords ({len(self.data['passwords'])} total):")
        for i, service in enumerate(sorted(self.data["passwords"].keys()), 1):
            entry = self.data["passwords"][service]
            print(
                f"{i}. {service} ({entry['username']}) - Updated: {entry['updated_at']}"
            )

    def show_history(self, service: str):
        """Show password history for a service"""
        if service not in self.data["history"]:
            print(f"No password history found for '{service}'")
            return

        history = self.data["history"][service]
        print(f"\nPassword history for '{service}' ({len(history)} changes):")

        for i, entry in enumerate(reversed(history), 1):
            print(f"\n{i}. Changed at: {entry['changed_at']}")
            print(f"   Username: {entry['username']}")
            print(f"   Password: {entry['password']}")
            print(f"   Originally created: {entry['created_at']}")

    def delete_password(self, service: str):
        """Delete a password entry"""
        if service not in self.data["passwords"]:
            print(f"No password found for '{service}'")
            return

        confirm = input(
            f"Are you sure you want to delete password for '{service}'? (y/N): "
        )
        if confirm.lower() == "y":
            del self.data["passwords"][service]
            # Also remove from history
            if service in self.data["history"]:
                del self.data["history"][service]

            self._save_data()
            print(f"Password for '{service}' deleted successfully!")
        else:
            print("Deletion cancelled.")

    def create_backup(self):
        """Create backup of password database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_file = self.backup_dir / f"passwords_backup_{timestamp}.json"

        try:
            shutil.copy2(self.db_file, backup_file)
            print(f"Backup created: {backup_file}")
        except Exception as e:
            print(f"Error creating backup: {e}")

    def list_backups(self):
        """List available backups"""
        backups = list(self.backup_dir.glob("passwords_backup_*.json"))

        if not backups:
            print("No backups found.")
            return

        print(f"\nAvailable backups ({len(backups)} total):")
        for i, backup in enumerate(sorted(backups), 1):
            timestamp = backup.stem.split("_", 2)[2]
            try:
                # Try new format with microseconds first
                formatted_time = datetime.strptime(
                    timestamp, "%Y%m%d_%H%M%S_%f"
                ).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fall back to old format without microseconds
                formatted_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            print(f"{i}. {backup.name} - {formatted_time}")

    def restore_backup(self, backup_name: str):
        """Restore from backup"""
        backup_file = self.backup_dir / backup_name

        if not backup_file.exists():
            print(f"Backup file '{backup_name}' not found.")
            return

        confirm = input(
            f"Are you sure you want to restore from '{backup_name}'? "
            "This will overwrite current data. (y/N): "
        )
        if confirm.lower() == "y":
            try:
                # Create backup of current data first
                self.create_backup()

                # Restore from backup
                shutil.copy2(backup_file, self.db_file)
                self._load_data()

                print(f"Successfully restored from backup: {backup_name}")
            except Exception as e:
                print(f"Error restoring backup: {e}")
        else:
            print("Restore cancelled.")


def main():
    """Main entry point for Kini"""
    parser = argparse.ArgumentParser(
        description="Kini - Secure Password Manager", prog="kini"
    )
    parser.add_argument(
        "command",
        help="Command to execute",
        choices=[
            "add",
            "get",
            "search",
            "list",
            "history",
            "delete",
            "backup",
            "restore",
        ],
    )
    parser.add_argument("--service", "-s", help="Service name")
    parser.add_argument("--username", "-u", help="Username")
    parser.add_argument("--password", "-p", help="Password")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--backup-file", "-b", help="Backup file name")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"Kini 1.0.0\n{show_mascot('mini')}",
    )

    args = parser.parse_args()

    # Initialize password manager
    pm = PasswordManager()

    # Authenticate user
    if not pm.authenticate():
        print("Authentication failed!")
        return 1

    # Execute command
    try:
        if args.command == "add":
            if not args.service:
                args.service = input("Service name: ")
            if not args.username:
                args.username = input("Username: ")
            if not args.password:
                args.password = getpass.getpass("Password: ")

            pm.add_password(args.service, args.username, args.password)

        elif args.command == "get":
            if not args.service:
                args.service = input("Service name: ")
            pm.get_password(args.service)

        elif args.command == "search":
            if not args.query:
                args.query = input("Search query: ")
            pm.search_passwords(args.query)

        elif args.command == "list":
            pm.list_passwords()

        elif args.command == "history":
            if not args.service:
                args.service = input("Service name: ")
            pm.show_history(args.service)

        elif args.command == "delete":
            if not args.service:
                args.service = input("Service name: ")
            pm.delete_password(args.service)

        elif args.command == "backup":
            if args.backup_file == "list":
                pm.list_backups()
            else:
                pm.create_backup()

        elif args.command == "restore":
            if not args.backup_file:
                pm.list_backups()
                args.backup_file = input("Enter backup filename: ")
            pm.restore_backup(args.backup_file)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
