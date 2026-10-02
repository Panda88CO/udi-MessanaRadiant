#!/usr/bin/env python3
"""
Test runner for udi-MessanaRadiant test suite.

Discovers and runs all unit tests in the tests/ directory.
Requires only Python standard library (no pip dependencies required).
"""

import os
import sys
import time
import unittest


def run_all_tests():
    """Discover and execute all test modules."""
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    print("=" * 70)
    print(" Running udi-MessanaRadiant Test Suite")
    print("=" * 70)

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time

    print("=" * 70)
    print(
        f" Tests: {result.testsRun} run | "
        f"{len(result.failures)} failed | "
        f"{len(result.errors)} errors | "
        f"Time: {duration:.3f}s"
    )
    print("=" * 70)

    if result.wasSuccessful():
        print(" ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("❌ TESTS FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
