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

1️⃣ удаляет старый отчёт,
2️⃣ запускает все автотесты с Allure,
3️⃣ и открывает отчёт в браузере автоматически:
pytest -v --alluredir=build/allure-results
allure serve build/allure-results
или
rm -rf reports/allure-results reports/allure-report && pytest || true && allure serve reports/allure-results

