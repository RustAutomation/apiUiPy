#!/usr/bin/env bash
set -euo pipefail

# === Настройки ===
PYTHON=${PYTHON:-python3.14}    # если у вас другой исполняемый python, измените здесь
VENV_DIR=.venv
PROJECT_ROOT=$(pwd)

echo "== Разворачиваем Python Playwright framework =="
echo "Используем python: ${PYTHON}"
echo ""

# Проверяем python
if ! command -v "${PYTHON}" >/dev/null 2>&1; then
  echo "ERROR: ${PYTHON} не найден. Установите Python 3.14 и убедитесь, что он доступен как ${PYTHON}."
  exit 1
fi

# Создаём виртуальное окружение
echo "-> Создаём виртуальное окружение ${VENV_DIR}"
"${PYTHON}" -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Обновляем pip
pip install --upgrade pip setuptools wheel

# Устанавливаем зависимости
echo "-> Устанавливаем зависимости (playwright, pytest, faker, allure-pytest, xdist, requests, pillow, opencv-python)"
pip install "pytest>=7.0" pytest-xdist allure-pytest playwright faker requests pillow opencv-python-headless==4.8.0.74 numpy

# Устанавливаем playwright browsers
echo "-> Устанавливаем браузеры Playwright"
python -m playwright install

# Создаём структуру каталогов
echo "-> Создаём структуру каталогов"
mkdir -p src/framework/{browser,pages,utils}
mkdir -p tests
mkdir -p src/test/resources/screenshots/expected
mkdir -p build/screenshots/actual
mkdir -p reports/allure-results

# === Файлы фреймворка ===

echo "-> Создаём framework/browser/manager.py"
cat > src/framework/browser/manager.py <<'PY' 
from playwright.sync_api import sync_playwright
import os

_playwright = None
_browser = None

def start_browser(headless: bool = False):
    global _playwright, _browser
    if _playwright is None:
        _playwright = sync_playwright().start()
    if _browser is None:
        _browser = _playwright.chromium.launch(headless=headless)
    return _browser

def new_context_page(headless: bool = False):
    """
    Возвращаем новый context + page - полезно для параллельных запусков.
    """
    b = start_browser(headless)
    context = b.new_context()
    page = context.new_page()
    return context, page

def stop_browser():
    global _playwright, _browser
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None
PY

echo "-> Создаём framework/utils/data_generator.py"
cat > src/framework/utils/data_generator.py <<'PY'
from faker import Faker
faker = Faker()

def first_name():
    return faker.first_name()

def last_name():
    return faker.last_name()

def email():
    return faker.email()

def phone_number():
    # 10-digit like in the demo form
    return ''.join([str(faker.random_digit_not_null()) for _ in range(10)])
PY

echo "-> Создаём framework/utils/visual_compare.py"
cat > src/framework/utils/visual_compare.py <<'PY'
from PIL import Image, ImageChops
import numpy as np

def compare_images_percent(path_a, path_b, path_diff=None):
    a = Image.open(path_a).convert('RGB')
    b = Image.open(path_b).convert('RGB')

    if a.size != b.size:
        # resize b to a size (or vice-versa) - here resize b
        b = b.resize(a.size)

    diff = ImageChops.difference(a, b)
    if path_diff:
        diff.save(path_diff)

    # Calculate percent difference
    diff_arr = np.asarray(diff)
    nonzero = np.count_nonzero(diff_arr)
    total = diff_arr.size
    percent = (nonzero / total) * 100.0
    return percent
PY

echo "-> Создаём framework/utils/allure_helper.py"
cat > src/framework/utils/allure_helper.py <<'PY'
import allure
from allure_commons.types import AttachmentType

def attach_screenshot(name, bytes_img):
    allure.attach(bytes_img, name=name, attachment_type=AttachmentType.PNG)

def attach_text(name, text):
    allure.attach(text, name=name, attachment_type=AttachmentType.TEXT)
PY

echo "-> Создаём framework/pages/practice_form.py"
cat > src/framework/pages/practice_form.py <<'PY'
from framework.utils.allure_helper import attach_screenshot
from playwright.sync_api import Page
from typing import Dict
import time

class PracticeFormPage:
    URL = "https://demoqa.com/automation-practice-form"

    def __init__(self, page: Page):
        self.page = page

    def open(self, timeout=60000):
        # load page (waiting until network idle is default in Playwright)
        self.page.goto(self.URL, timeout=timeout)
        # close ad banners if present
        try:
            # demoqa often shows fixed footer or ads we can hide
            self.page.evaluate("() => { const el = document.querySelector('#fixedban'); if(el) el.remove(); }")
        except Exception:
            pass
        return self

    def fill_required_fields(self, data: Dict):
        # first & last name
        self.page.fill("#firstName", data["firstName"])
        self.page.fill("#lastName", data["lastName"])
        # email
        self.page.fill("#userEmail", data["email"])
        # choose gender - try clicking first radio label
        # choose randomly: label[for^='gender-radio']
        labels = self.page.query_selector_all("label[for^='gender-radio']")
        if labels:
            # choose any that is visible
            for lbl in labels:
                try:
                    lbl.click()
                    break
                except:
                    continue
        # phone
        self.page.fill("#userNumber", data["phone"])
        return self

    def submit(self):
        # click submit - sometimes requires scrolling
        self.page.locator("#submit").scroll_into_view_if_needed()
        self.page.click("#submit")
        return self

    def read_result_table(self):
        # read modal result table into dict {label: value}
        self.page.wait_for_selector(".modal-content", timeout=5000)
        rows = self.page.query_selector_all(".modal-content tbody tr")
        result = {}
        for r in rows:
            cols = r.query_selector_all("td")
            if len(cols) >= 2:
                k = cols[0].inner_text().strip()
                v = cols[1].inner_text().strip()
                result[k] = v
        return result

    def screenshot_attach(self, name):
        png = self.page.screenshot()
        attach_screenshot(name, png)
PY

# === tests ===

echo "-> Создаём tests/test_api.py"
cat > tests/test_api.py <<'PY'
import requests
import allure

def test_get_user_reqres():
    url = "https://reqres.in/api/users/2"
    with allure.step(f"GET {url}"):
        r = requests.get(url, timeout=15)
        assert r.status_code == 200, f"Status {r.status_code}"
        assert "Janet" in r.text or "Janet Weaver" in r.text
PY

echo "-> Создаём tests/test_practice_form.py"
cat > tests/test_practice_form.py <<'PY'
import pytest
import allure
from framework.browser.manager import new_context_page, stop_browser
from framework.pages.practice_form import PracticeFormPage
from framework.utils.data_generator import first_name, last_name, email, phone_number

HEADLESS = False if (("HEADLESS" not in __import__('os').environ) or __import__('os').environ.get('HEADLESS') in ["0","false","False"]) else True

@pytest.fixture
def page_ctx():
    ctx, page = new_context_page(headless=HEADLESS)
    try:
        yield page
    finally:
        try:
            ctx.close()
        except:
            pass

def test_practice_form_popup(page_ctx):
    page = page_ctx
    form = PracticeFormPage(page)

    data = {
        "firstName": first_name(),
        "lastName": last_name(),
        "email": email(),
        "phone": phone_number()
    }

    with allure.step("Open form and fill data"):
        form.open()
        form.fill_required_fields(data)
        form.screenshot_attach("filled_form_before_submit")
        form.submit()

    with allure.step("Read result and verify fields"):
        result = form.read_result_table()
        # mapping: our keys to displayed labels may vary; try to assert included values
        # Check name
        full_name = f\"{data['firstName']} {data['lastName']}\"
        assert full_name in result.get('Student Name', full_name) or data['firstName'] in result.get('Student Name', '')

        # email
        assert data['email'] in result.get('Student Email', result.get('Student Email','') ) or data['email'] in ' '.join(result.values())

        # phone
        assert data['phone'] in result.get('Mobile', result.get('Mobile','')) or data['phone'] in ' '.join(result.values())

        # attach popup screenshot
        png = page.screenshot()
        allure.attach(png, name='popup', attachment_type=allure.attachment_type.PNG)
PY

echo "-> Создаём tests/test_visual.py"
cat > tests/test_visual.py <<'PY'
import os
import allure
from framework.browser.manager import new_context_page
from framework.utils.visual_compare import compare_images_percent

HEADLESS = False if (("HEADLESS" not in __import__('os').environ) or __import__('os').environ.get('HEADLESS') in ["0","false","False"]) else True

def test_visual_demoqa_homepage():
    ctx, page = new_context_page(headless=HEADLESS)
    try:
        page.goto("https://demoqa.com", timeout=60000)
        actual_path = "build/screenshots/actual/homepage_actual.png"
        os.makedirs(os.path.dirname(actual_path), exist_ok=True)
        page.screenshot(path=actual_path, full_page=True)
        allure.attach.file(actual_path, name="actual_home", attachment_type=allure.attachment_type.PNG)

        baseline = "src/test/resources/screenshots/expected/demoqa_home.png"
        if not os.path.exists(baseline):
            # if no baseline - create it
            os.makedirs(os.path.dirname(baseline), exist_ok=True)
            from shutil import copyfile
            copyfile(actual_path, baseline)
            allure.attach.file(baseline, name="baseline_created", attachment_type=allure.attachment_type.PNG)
            return

        diff_path = "build/screenshots/actual/homepage_diff.png"
        percent = compare_images_percent(baseline, actual_path, diff_path)
        allure.attach.file(diff_path, name="diff", attachment_type=allure.attachment_type.PNG)
        assert percent < 2.0, f"Difference percentage {percent}% >= 2%"
    finally:
        try:
            ctx.close()
        except:
            pass
PY

# === pytest.ini ===
echo "-> Создаём pytest.ini"
cat > pytest.ini <<'PY'
[pytest]
addopts = -ra -q --alluredir=reports/allure-results -n auto
testpaths = tests
PY

# === helper scripts ===
echo "-> Создаём run_tests.sh (запуск тестов и генерация отчёта если установлен allure)"
cat > run_tests.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
# activate venv
source .venv/bin/activate
pytest "$@"
echo "If you have Allure CLI installed you can generate the report with:"
echo "  allure generate reports/allure-results -o reports/allure-report --clean"
echo "or open with allure serve:"
echo "  allure serve reports/allure-results"
SH
chmod +x run_tests.sh

# README
cat > README.md <<'MD'
# DemoQA Python Playwright Framework (auto-generated)

## Требования
- Python 3.14 доступный как \`python3.14\` (или исправьте переменную PYTHON в setup script)
- bash shell (Linux / macOS). Для Windows используйте WSL или вручную адаптируйте команды.
- Рекомендуется установить [Allure CLI](https://docs.qameta.io/allure/) для генерации HTML-отчёта:
  - macOS: `brew install allure` (или `brew install allure2`)
  - Windows: `choco install allure` или скачайте из релизов

## Быстрая установка (скрипт делает всё за вас)
```bash
chmod +x setup_python_framework.sh
./setup_python_framework.sh
