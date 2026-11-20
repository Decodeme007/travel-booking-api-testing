import sys
import subprocess
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = REPORTS_DIR / "test_report.html"


def run_tests():
    """Execute pytest with HTML reporting and verbose console output."""
    print("=" * 70)
    print("   TRAVEL BOOKING API AUTOMATION & TESTING FRAMEWORK")
    print("=" * 70)
    print(f"Generating HTML report at: {REPORT_FILE}")
    print("Executing Pytest test suite...")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        f"--html={REPORT_FILE}",
        "--self-contained-html"
    ]

    result = subprocess.run(cmd)

    print("\n" + "=" * 70)
    if result.returncode == 0:
        print(">>> ALL API AUTOMATION TEST SCENARIOS PASSED SUCCESSFULLY! <<<")
    else:
        print(f">>> TEST SUITE FINISHED WITH EXIT CODE: {result.returncode} <<<")
    print(f"Report location: {REPORT_FILE.resolve()}")
    print("=" * 70)
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
