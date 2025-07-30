#!/usr/bin/env python
"""
Helper script to run the database resilience tests.
Can run all tests or a specific test module.
"""

import argparse
import os
import subprocess
import sys

# Default test environment variables
ENV_DEFAULTS = {
    "TEST_DB_HOST": "localhost",
    "TEST_DB_PORT": "5432",
    "TEST_DB_USER": "postgres",
    "TEST_DB_PASS": "postgres",
    "TEST_DB_NAME": "test_db",
    "USE_DOCKER_DB": "false",
}

# Test modules available
TEST_MODULES = {
    "connection": "test_connection_resilience.py",
    "security": "test_security_features.py",
    "circuit_breaker": "test_circuit_breaker_rate_limiter.py",
    "load": "test_load_edge_cases.py",
    "all": None,  # Run all tests
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run database resilience tests")

    # Test module selection
    parser.add_argument(
        "--module",
        "-m",
        choices=list(TEST_MODULES.keys()),
        default="all",
        help="Test module to run (default: all)",
    )

    # Test database configuration
    parser.add_argument("--host", help="Test database host")
    parser.add_argument("--port", help="Test database port")
    parser.add_argument("--user", help="Test database user")
    parser.add_argument("--password", help="Test database password")
    parser.add_argument("--db", help="Test database name")

    # Docker control
    parser.add_argument("--docker", action="store_true", help="Launch PostgreSQL in Docker for testing")

    # Other pytest options
    parser.add_argument("--verbose", "-v", action="store_true", help="Run with verbose output")
    parser.add_argument("--debug", action="store_true", help="Show debug output from SQLAlchemy")

    return parser.parse_args()


def run_tests(module: str, env_vars: dict, verbose: bool, debug: bool) -> int:
    """Run the specified test module with pytest."""
    # Set up environment variables
    test_env = os.environ.copy()
    test_env.update(env_vars)

    # Get test file or directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if module == "all":
        test_target = script_dir
    else:
        test_file = TEST_MODULES[module]
        test_target = os.path.join(script_dir, test_file)

    # Build pytest command
    cmd = ["pytest", "-xvs" if verbose else "-x"]

    # Add debug flags if requested
    if debug:
        cmd.append("--log-cli-level=DEBUG")

    # Add the test target
    cmd.append(test_target)

    print(f"Running tests: {' '.join(cmd)}")
    print(f"Environment: {', '.join([f'{k}={v}' for k, v in env_vars.items()])}")

    # Run the tests
    result = subprocess.run(cmd, env=test_env)
    return result.returncode


def main() -> int:
    """Run the script."""
    args = parse_args()

    # Build environment variables
    env_vars = ENV_DEFAULTS.copy()

    # Override with command line arguments if provided
    if args.host:
        env_vars["TEST_DB_HOST"] = args.host
    if args.port:
        env_vars["TEST_DB_PORT"] = args.port
    if args.user:
        env_vars["TEST_DB_USER"] = args.user
    if args.password:
        env_vars["TEST_DB_PASS"] = args.password
    if args.db:
        env_vars["TEST_DB_NAME"] = args.db
    if args.docker:
        env_vars["USE_DOCKER_DB"] = "true"

    # Run the tests
    return run_tests(args.module, env_vars, args.verbose, args.debug)


if __name__ == "__main__":
    sys.exit(main())
