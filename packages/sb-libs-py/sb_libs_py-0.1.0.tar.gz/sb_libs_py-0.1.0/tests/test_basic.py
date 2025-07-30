"""Basic tests for sb_libs package."""

import sb_libs


def test_version() -> None:
    """Test that version is available."""
    assert hasattr(sb_libs, "__version__")
    assert isinstance(sb_libs.__version__, str)
