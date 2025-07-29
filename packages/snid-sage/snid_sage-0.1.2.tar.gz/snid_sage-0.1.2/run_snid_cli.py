#!/usr/bin/env python3
"""
Simple script to run SNID SAGE CLI commands.

This script provides an easier way to run SNID SAGE CLI commands
without having to use the long python -c syntax.

Usage:
    python run_snid_cli.py --help
    python run_snid_cli.py identify data/sn2003jo.dat templates/ --verbose
    python run_snid_cli.py template list templates/
"""

import sys
from snid_sage.interfaces.cli.main import main

if __name__ == "__main__":
    sys.exit(main()) 