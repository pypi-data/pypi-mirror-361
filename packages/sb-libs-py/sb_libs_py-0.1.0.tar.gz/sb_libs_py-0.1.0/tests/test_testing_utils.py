"""Tests for testing utilities package."""

from pathlib import Path

from sb_libs.testing import (
    NamingValidator,
    UnittestToPytestMigrator,
    check_unittest_usage,
)


def test_test_naming_validator_creation() -> None:
    """Test that NamingValidator can be instantiated."""
    validator = NamingValidator()
    assert validator is not None
    assert hasattr(validator, "validate_file")
    assert hasattr(validator, "validate_directory")


def test_unittest_to_pytest_migrator_creation() -> None:
    """Test that UnittestToPytestMigrator can be instantiated."""
    migrator = UnittestToPytestMigrator(dry_run=True)
    assert migrator is not None
    assert migrator.dry_run is True
    assert hasattr(migrator, "migrate_file")


def test_check_unittest_usage_function() -> None:
    """Test that check_unittest_usage function is callable."""
    # Create a temporary test file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("import pytest\n\ndef test_example():\n    assert True\n")
        temp_path = Path(f.name)

    try:
        # Should return False for pytest-style test
        result = check_unittest_usage(temp_path)
        assert isinstance(result, bool)
    finally:
        temp_path.unlink()  # Clean up


def test_testing_package_imports() -> None:
    """Test that all expected utilities are importable."""
    from sb_libs.testing import (
        NamingValidator,
        UnittestToPytestMigrator,
        check_unittest_usage,
    )

    # All imports should succeed
    assert NamingValidator is not None
    assert UnittestToPytestMigrator is not None
    assert check_unittest_usage is not None
