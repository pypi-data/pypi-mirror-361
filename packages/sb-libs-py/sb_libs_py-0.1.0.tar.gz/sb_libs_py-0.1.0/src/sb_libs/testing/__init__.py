"""Testing utilities for Python projects.

This package provides tools for test management, validation, and migration:

- detect_unittest_usage: Pre-commit hook to detect unittest usage
- naming_validator: Validates test naming conventions
- unittest_to_pytest_migrator: Migrates unittest tests to pytest format
"""

from .detect_unittest_usage import check_unittest_usage
from .naming_validator import NamingValidator
from .unittest_to_pytest_migrator import UnittestToPytestMigrator

__all__ = [
    "check_unittest_usage",
    "NamingValidator",
    "UnittestToPytestMigrator",
]
