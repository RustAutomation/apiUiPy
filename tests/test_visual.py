import allure
from src.framework.browser.manager import new_context_page
from src.framework.utils.visual_compare import VisualComparer
from src.framework.utils.wait_until import wait_until

visual = VisualComparer()

@allure.title("Visual regression test: DemoQA homepage")
def test_visual_demoqa_homepage():
    ctx, page = new_context_page()

    try:
        page.goto("https://demoqa.com", timeout=60000)

        wait_until(
            lambda: page.evaluate("document.readyState") == "complete",
            timeout=15,
        )

        visual.compare(page, "demoqa_home")

    finally:
        ctx.close()
