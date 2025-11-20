import os
import allure
from src.framework.browser.manager import new_context_page
from src.framework.utils.visual_compare import VisualComparer
from src.framework.utils.wait_until import wait_until


HEADLESS = False if (
    ("HEADLESS" not in os.environ) or os.environ.get("HEADLESS") in ["0", "false", "False"]
) else True


visual = VisualComparer()   # ← единственный объект на весь тест


@allure.title("Visual regression test: DemoQA homepage")
def test_visual_demoqa_homepage():
    ctx, page = new_context_page(headless=HEADLESS)

    try:
        with allure.step("Открываем страницу DemoQA"):
            page.goto("https://demoqa.com", timeout=60000)

            wait_until(
                lambda: page.evaluate("document.readyState") == "complete",
                timeout=15,
            )

        with allure.step("Проверяем визуальное соответствие страницы"):
            visual.compare(page, "demoqa_home")

    finally:
        ctx.close()
