#!/usr/bin/env python3
"""
Kini - Main entry point for the command-line interface
"""

import sys

from .password_manager import main

if __name__ == "__main__":
    sys.exit(main())
