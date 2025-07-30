from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

# Read test requirements (fallback if file doesn't exist)
try:
    with open("requirements-test.txt", "r", encoding="utf-8") as fh:
        test_requirements = [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    # Fallback test requirements for PyPI build
    test_requirements = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "coverage>=7.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "isort>=5.0.0",
        "mypy>=1.0.0",
        "pre-commit>=2.20.0",
    ]

setup(
    name="kini",
    version="1.0.0",
    author="Sagar Paul",
    author_email="paul.sagar@yahoo.com",
    description="A secure command-line password manager with encryption and backup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com//KB-perByte/kini",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "test": test_requirements,
        "dev": test_requirements,
    },
    entry_points={
        "console_scripts": [
            "kini=kini.__main__:main",
        ],
    },
    keywords="password manager security encryption cli kini",
    project_urls={
        "Bug Reports": "https://github.com/KB-perByte/kini/issues",
        "Source": "https://github.com/KB-perByte/kini",
    },
    # Test configuration
    test_suite="tests",
)
