# Kini - Secure Password Manager

( Your secrets are safe )

A secure command-line password manager with encryption, hashing, backup, and search capabilities.

## Features

- **Secure Encryption**: Uses AES-256 encryption (Fernet) for all stored data
- **Master Password**: Single password protects all your passwords
- **Password History**: Track password changes with timestamps
- **Search Functionality**: Find passwords quickly by service name
- **Backup & Restore**: Create and restore from encrypted backups
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI (to be published)

```bash
pip install kini
```

### From Source

```bash
git clone https://github.com/yourusername/kini.git
cd kini
pip install -e .
```

## Usage

### First Time Setup

```bash
kini list
# This will prompt you to create a master password
```

### Adding Passwords

```bash
# Interactive mode
kini add

# Command line mode
kini add -s "gmail" -u "user@gmail.com" -p "mypassword"
```

### Retrieving Passwords

```bash
# Get specific password
kini get -s "gmail"

# Search for passwords
kini search -q "mail"

# List all passwords
kini list
```

### Password History

```bash
# View password history for a service
kini history -s "gmail"
```

### Backup & Restore

```bash
# Create backup
kini backup

# List backups
kini backup list

# Restore from backup
kini restore -b "passwords_backup_20240101_120000.json"
```

### Other Commands

```bash
# Delete a password
kini delete -s "gmail"

# Show version
kini --version
```

## Security

- All passwords are encrypted using AES-256 (Fernet)
- Master password is hashed using SHA-256
- Key derivation uses PBKDF2 with 100,000 iterations
- Unique salt for each installation
- Data stored locally in `~/.kini/`

## Data Location

- **Linux/macOS**: `~/.kini/`
- **Windows**: `%USERPROFILE%\.kini\`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development and Testing

### Installing Development Dependencies

```bash
# Install with development dependencies
pip install -e .[dev]

# Or install test dependencies only
pip install -r requirements-test.txt
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=kini --cov-report=term-missing --cov-report=html

# Using make commands
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make install-dev   # Install dev dependencies
```

### Using Tox for Multi-Version Testing

```bash
# Install tox
pip install tox

# Run tests across all Python versions
tox

# Run specific environments
tox -e py311        # Test Python 3.11
tox -e lint         # Run linting
tox -e coverage     # Run coverage report
```

### Test Structure

- `tests/test_password_manager.py` - Main test suite
- `tests/conftest.py` - Test configuration and fixtures
- `pytest.ini` - Pytest configuration
- `tox.ini` - Tox configuration for multi-version testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `make test`
6. Submit a pull request

## Security Considerations

- Never share your master password
- Regularly create backups
- Store backups in a secure location
- Use strong, unique passwords for your services
