#!/usr/bin/env python3
"""
Code Auto-Documenter - Main Entry Point

A CLI-based tool that uses AI to generate comprehensive documentation
for Python and JavaScript codebases.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import main

if __name__ == "__main__":
    main()
