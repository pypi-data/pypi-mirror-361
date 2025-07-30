import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kini.password_manager import PasswordManager, main

# Add the parent directory to the path so we can import kini
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestPasswordManager:
    """Test suite for PasswordManager class"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def pm(self, temp_dir):
        """Create a PasswordManager instance with temporary directory"""
        return PasswordManager(data_dir=temp_dir)

    def test_init(self, pm, temp_dir):
        """Test PasswordManager initialization"""
        assert pm.data_dir == Path(temp_dir)
        assert pm.data_dir.exists()
        assert pm.backup_dir.exists()
        assert pm.cipher is None
        assert pm.data == {"passwords": {}, "history": {}}

    def test_hash_password(self, pm):
        """Test password hashing"""
        password = "test_password"
        hash1 = pm._hash_password(password)
        hash2 = pm._hash_password(password)

        assert hash1 == hash2  # Same password should produce same hash
        assert len(hash1) == 64  # SHA-256 produces 64 character hex string
        assert hash1 != password  # Hash should be different from original

    def test_generate_key(self, pm):
        """Test key generation"""
        password = "test_password"
        salt = os.urandom(16)

        key1 = pm._generate_key(password, salt)
        key2 = pm._generate_key(password, salt)

        assert key1 == key2  # Same password and salt should produce same key
        assert len(key1) == 44  # Base64 encoded 32-byte key

    def test_load_or_create_salt(self, pm):
        """Test salt loading and creation"""
        # First call should create salt
        salt1 = pm._load_or_create_salt()
        assert len(salt1) == 16
        assert pm.salt_file.exists()

        # Second call should load existing salt
        salt2 = pm._load_or_create_salt()
        assert salt1 == salt2

    @patch("getpass.getpass")
    def test_setup_master_password(self, mock_getpass, pm):
        """Test master password setup"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]

        result = pm.setup_master_password()

        assert result is True
        assert pm.master_hash_file.exists()
        assert pm.cipher is not None
        assert pm.db_file.exists()

        # Test that setup returns False if already exists
        result2 = pm.setup_master_password()
        assert result2 is False

    @patch("getpass.getpass")
    def test_authenticate_new_user(self, mock_getpass, pm):
        """Test authentication for new user"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]

        result = pm.authenticate()

        assert result is True
        assert pm.cipher is not None

    @patch("getpass.getpass")
    def test_authenticate_existing_user(self, mock_getpass, pm):
        """Test authentication for existing user"""
        # Setup master password first
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Reset cipher to test authentication
        pm.cipher = None

        # Test correct password
        mock_getpass.side_effect = ["master_pass"]
        result = pm.authenticate()
        assert result is True

        # Reset cipher to test authentication again
        pm.cipher = None

        # Test incorrect password
        mock_getpass.side_effect = ["wrong_pass"]
        result = pm.authenticate()
        assert result is False

    @patch("getpass.getpass")
    def test_add_password(self, mock_getpass, pm):
        """Test adding passwords"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add first password
        pm.add_password("test_service", "test_user", "test_pass")

        assert "test_service" in pm.data["passwords"]
        entry = pm.data["passwords"]["test_service"]
        assert entry["username"] == "test_user"
        assert entry["password"] == "test_pass"
        assert "created_at" in entry
        assert "updated_at" in entry

    @patch("getpass.getpass")
    def test_add_password_with_history(self, mock_getpass, pm):
        """Test adding password creates history when updating"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add first password
        pm.add_password("test_service", "test_user", "old_pass")

        # Update password
        pm.add_password("test_service", "test_user", "new_pass")

        # Check current password
        assert pm.data["passwords"]["test_service"]["password"] == "new_pass"

        # Check history
        assert "test_service" in pm.data["history"]
        assert len(pm.data["history"]["test_service"]) == 1
        assert pm.data["history"]["test_service"][0]["password"] == "old_pass"

    @patch("getpass.getpass")
    def test_get_password(self, mock_getpass, pm, capsys):
        """Test retrieving passwords"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add password
        pm.add_password("test_service", "test_user", "test_pass")

        # Get password
        result = pm.get_password("test_service")

        assert result is not None
        assert result["username"] == "test_user"
        assert result["password"] == "test_pass"

        # Check output
        captured = capsys.readouterr()
        assert "test_service" in captured.out
        assert "test_user" in captured.out
        assert "test_pass" in captured.out

        # Test non-existent service
        result = pm.get_password("non_existent")
        assert result is None

    @patch("getpass.getpass")
    def test_search_passwords(self, mock_getpass, pm, capsys):
        """Test searching passwords"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add test passwords
        pm.add_password("gmail", "user1", "pass1")
        pm.add_password("github", "user2", "pass2")
        pm.add_password("google_drive", "user3", "pass3")

        # Test search with multiple matches
        with patch("builtins.input", return_value="1"):
            pm.search_passwords("g")
            captured = capsys.readouterr()
            assert "Found 3 match(es)" in captured.out

        # Test search with single match
        pm.search_passwords("mail")
        captured = capsys.readouterr()
        assert "gmail" in captured.out
        assert "user1" in captured.out

        # Test search with no matches
        pm.search_passwords("nonexistent")
        captured = capsys.readouterr()
        assert "No passwords found" in captured.out

    @patch("getpass.getpass")
    def test_list_passwords(self, mock_getpass, pm, capsys):
        """Test listing passwords"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Test empty list
        pm.list_passwords()
        captured = capsys.readouterr()
        assert "No passwords stored" in captured.out

        # Add passwords and test list
        pm.add_password("test1", "user1", "pass1")
        pm.add_password("test2", "user2", "pass2")

        pm.list_passwords()
        captured = capsys.readouterr()
        assert "2 total" in captured.out
        assert "test1" in captured.out
        assert "test2" in captured.out

    @patch("getpass.getpass")
    def test_show_history(self, mock_getpass, pm, capsys):
        """Test showing password history"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Test service with no history
        pm.show_history("nonexistent")
        captured = capsys.readouterr()
        assert "No password history found" in captured.out

        # Add password and update it to create history
        pm.add_password("test_service", "user", "old_pass")
        pm.add_password("test_service", "user", "new_pass")

        pm.show_history("test_service")
        captured = capsys.readouterr()
        assert "1 changes" in captured.out
        assert "old_pass" in captured.out

    @patch("getpass.getpass")
    def test_delete_password(self, mock_getpass, pm, capsys):
        """Test deleting passwords"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add password
        pm.add_password("test_service", "user", "pass")

        # Test cancellation
        with patch("builtins.input", return_value="n"):
            pm.delete_password("test_service")
            assert "test_service" in pm.data["passwords"]

        # Test deletion
        with patch("builtins.input", return_value="y"):
            pm.delete_password("test_service")
            assert "test_service" not in pm.data["passwords"]

        # Test non-existent service
        pm.delete_password("nonexistent")
        captured = capsys.readouterr()
        assert "No password found" in captured.out

    @patch("getpass.getpass")
    def test_create_backup(self, mock_getpass, pm, capsys):
        """Test creating backups"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add some data
        pm.add_password("test", "user", "pass")

        # Create backup
        pm.create_backup()

        # Check backup was created
        backups = list(pm.backup_dir.glob("passwords_backup_*.json"))
        assert len(backups) == 1

        captured = capsys.readouterr()
        assert "Backup created" in captured.out

    @patch("getpass.getpass")
    def test_list_backups(self, mock_getpass, pm, capsys):
        """Test listing backups"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Test no backups
        pm.list_backups()
        captured = capsys.readouterr()
        assert "No backups found" in captured.out

        # Create backup and test list
        pm.create_backup()
        pm.list_backups()
        captured = capsys.readouterr()
        assert "1 total" in captured.out
        assert "passwords_backup_" in captured.out

    @patch("getpass.getpass")
    def test_restore_backup(self, mock_getpass, pm, capsys):
        """Test restoring from backup"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add data and create backup
        pm.add_password("original", "user", "pass")
        pm.create_backup()

        # Get backup filename (should only contain 'original')
        backups = list(pm.backup_dir.glob("passwords_backup_*.json"))
        backup_name = backups[0].name

        # Modify data (add new service)
        pm.add_password("new_service", "user", "pass")

        # Verify both services exist before restore
        assert "original" in pm.data["passwords"]
        assert "new_service" in pm.data["passwords"]

        # Test restore cancellation
        with patch("builtins.input", return_value="n"):
            pm.restore_backup(backup_name)
            assert "new_service" in pm.data["passwords"]

        # Test restore - should restore to state with only 'original'
        with patch("builtins.input", return_value="y"):
            pm.restore_backup(backup_name)
            assert "new_service" not in pm.data["passwords"]
            assert "original" in pm.data["passwords"]

        # Test non-existent backup
        pm.restore_backup("nonexistent.json")
        captured = capsys.readouterr()
        assert "not found" in captured.out

    @patch("getpass.getpass")
    def test_encryption_decryption(self, mock_getpass, pm):
        """Test encryption and decryption"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        test_data = "sensitive_data"

        # Test encryption
        encrypted = pm._encrypt_data(test_data)
        assert encrypted != test_data

        # Test decryption
        decrypted = pm._decrypt_data(encrypted)
        assert decrypted == test_data

    @patch("getpass.getpass")
    def test_data_persistence(self, mock_getpass, pm):
        """Test data saving and loading"""
        mock_getpass.side_effect = ["master_pass", "master_pass"]
        pm.setup_master_password()

        # Add data
        pm.add_password("test", "user", "pass")

        # Create new instance and load data
        pm2 = PasswordManager(data_dir=str(pm.data_dir))
        mock_getpass.side_effect = ["master_pass"]
        pm2.authenticate()

        # Check data was loaded
        assert "test" in pm2.data["passwords"]
        assert pm2.data["passwords"]["test"]["username"] == "user"


class TestMainFunction:
    """Test suite for main function"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("sys.argv", ["kini", "list"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_list_command(self, mock_pm_class, mock_getpass):
        """Test main function with list command"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 0
        mock_pm.authenticate.assert_called_once()
        mock_pm.list_passwords.assert_called_once()

    @patch("sys.argv", ["kini", "add", "-s", "test", "-u", "user", "-p", "pass"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_add_command(self, mock_pm_class, mock_getpass):
        """Test main function with add command"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 0
        mock_pm.add_password.assert_called_once_with("test", "user", "pass")

    @patch("sys.argv", ["kini", "get", "-s", "test"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_get_command(self, mock_pm_class, mock_getpass):
        """Test main function with get command"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 0
        mock_pm.get_password.assert_called_once_with("test")

    @patch("sys.argv", ["kini", "search", "-q", "query"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_search_command(self, mock_pm_class, mock_getpass):
        """Test main function with search command"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 0
        mock_pm.search_passwords.assert_called_once_with("query")

    @patch("sys.argv", ["kini", "backup"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_backup_command(self, mock_pm_class, mock_getpass):
        """Test main function with backup command"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 0
        mock_pm.create_backup.assert_called_once()

    @patch("sys.argv", ["kini", "list"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_authentication_failure(self, mock_pm_class, mock_getpass):
        """Test main function with authentication failure"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = False
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 1
        mock_pm.authenticate.assert_called_once()

    @patch("sys.argv", ["kini", "list"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_keyboard_interrupt(self, mock_pm_class, mock_getpass):
        """Test main function with keyboard interrupt"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm.list_passwords.side_effect = KeyboardInterrupt()
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 1

    @patch("sys.argv", ["kini", "list"])
    @patch("getpass.getpass")
    @patch("kini.password_manager.PasswordManager")
    def test_main_exception(self, mock_pm_class, mock_getpass):
        """Test main function with general exception"""
        mock_pm = MagicMock()
        mock_pm.authenticate.return_value = True
        mock_pm.list_passwords.side_effect = Exception("Test error")
        mock_pm_class.return_value = mock_pm

        result = main()

        assert result == 1
