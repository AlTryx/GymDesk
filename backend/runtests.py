import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_django_tests():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymdesk.settings')
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["core.tests.test_models"])

    return failures

def run_pytest():
    try:
        import pytest
        return pytest.main([
            'core/tests/',
            '--verbose',
            '--tb=short',
            '--cov=core',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    except ImportError:
        print("pytest not installed.")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--pytest':
        exit_code = run_pytest()
    else:
        exit_code = run_django_tests()

    sys.exit(exit_code)