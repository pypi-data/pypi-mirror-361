# This file makes the tests directory a Python package


# ======================
# Update setup.py to include test dependencies
# ======================
# Add this to your setup.py file:

# In setup.py, add test dependencies:
extras_require = {
    "test": [
        "pytest>=6.0",
        "pytest-cov>=2.0",
        "pytest-mock>=3.0",
    ],
}
