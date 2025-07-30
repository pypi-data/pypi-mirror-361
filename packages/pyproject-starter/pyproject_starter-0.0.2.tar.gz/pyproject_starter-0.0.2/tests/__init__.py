"""Test suite for pyproject_starter

This module contains all tests for the pyproject_starter package.
Tests are organized by functionality and follow pytest conventions.
"""

# Test configuration and utilities
import sys
from pathlib import Path

# Add src directory to Python path for testing
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Test constants
TEST_DATA_DIR = Path(__file__).parent / "data"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
FIXTURES_DIR.mkdir(exist_ok=True)
