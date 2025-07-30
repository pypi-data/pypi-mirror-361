"""Command-line interface for testing utilities."""

import sys
from argparse import ArgumentParser


def main() -> int:
    """Main CLI entry point."""
    parser = ArgumentParser(prog="sb_libs.testing", description="Testing utilities for Python projects")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # detect-unittest command
    detect_parser = subparsers.add_parser("detect-unittest", help="Detect unittest usage in test files")
    detect_parser.add_argument("files", nargs="+", help="Test files to check")

    # validate-naming command
    validate_parser = subparsers.add_parser("validate-naming", help="Validate test naming conventions")
    validate_parser.add_argument("path", help="Path to test file or directory")
    validate_parser.add_argument("--detailed", action="store_true")
    validate_parser.add_argument("--fix", action="store_true")
    validate_parser.add_argument("--dry-run", action="store_true")

    # migrate-unittest command
    migrate_parser = subparsers.add_parser("migrate-unittest", help="Migrate unittest tests to pytest")
    migrate_parser.add_argument("path", help="Path to test file or directory")
    migrate_parser.add_argument("--dry-run", action="store_true")
    migrate_parser.add_argument("--pattern", default="test_*.py")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "detect-unittest":
        from .detect_unittest_usage import main as detect_main

        sys.argv = ["detect_unittest_usage"] + args.files
        detect_main()
        return 0

    elif args.command == "validate-naming":
        from .naming_validator import main as validate_main

        sys.argv = ["naming_validator", args.path]
        if args.detailed:
            sys.argv.append("--detailed")
        if args.fix:
            sys.argv.append("--fix")
        if args.dry_run:
            sys.argv.append("--dry-run")
        validate_main()
        return 0

    elif args.command == "migrate-unittest":
        from .unittest_to_pytest_migrator import main as migrate_main

        sys.argv = ["unittest_to_pytest_migrator", args.path]
        if args.dry_run:
            sys.argv.append("--dry-run")
        if args.pattern != "test_*.py":
            sys.argv.extend(["--pattern", args.pattern])
        migrate_main()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
