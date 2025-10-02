#!/usr/bin/env python
"""
Test runner for Phase 4: Comprehensive unit tests.

This script runs all unit tests for the AREA automation system:
- Serializer tests
- API view tests
- Integration tests
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'area_project.settings')

def main():
    """Run all unit tests for the automations app."""
    print("🧪 Running Phase 4: Unit Tests for AREA Automation System")
    print("=" * 60)

    try:
        django.setup()
        print("✅ Django setup successful")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return 1

    # Get Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)

    # Define test modules to run
    test_modules = [
        'automations.tests.test_serializers',
        'automations.tests.test_views',
    ]

    print(f"📋 Running tests for modules: {', '.join(test_modules)}")
    print("-" * 60)

    # Run tests
    failures = test_runner.run_tests(test_modules)

    print("-" * 60)
    if failures:
        print(f"❌ {failures} test(s) failed")
        return 1
    else:
        print("🎉 All tests passed!")
        return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)