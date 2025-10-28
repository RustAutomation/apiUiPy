#!/usr/bin/env bash
set -euo pipefail
# activate venv
source .venv/bin/activate
pytest "$@"
echo "If you have Allure CLI installed you can generate the report with:"
echo "  allure generate reports/allure-results -o reports/allure-report --clean"
echo "or open with allure serve:"
echo "  allure serve reports/allure-results"
