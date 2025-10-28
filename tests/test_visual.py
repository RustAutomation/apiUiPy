import os
import allure
import time
from PIL import Image, ImageChops, ImageDraw
from shutil import copyfile
from src.framework.browser.manager import new_context_page


HEADLESS = False if (
    ("HEADLESS" not in os.environ) or os.environ.get("HEADLESS") in ["0", "false", "False"]
) else True


def wait_until(condition_fn, timeout=10, interval=0.5, message="Условие не выполнено"):
    """Awaitility-стиль ожидания."""
    start = time.time()
    attempt = 0
    while time.time() - start < timeout:
        attempt += 1
        try:
            if condition_fn():
                return
        except Exception:
            pass
        time.sleep(interval)
    raise TimeoutError(f"{message} за {timeout} секунд (попыток: {attempt})")


def create_diff_overlay(baseline_path, actual_path, diff_path, alpha=128):
    """Создаёт diff с прозрачным красным наложением на всю страницу."""
    base = Image.open(baseline_path).convert("RGBA")
    actual = Image.open(actual_path).convert("RGBA")

    diff = ImageChops.difference(base, actual)
    bbox = diff.getbbox()

    if not bbox:
        actual.save(diff_path)
        return 0.0

    diff_pixels = sum(1 for pixel in diff.getdata() if pixel != (0, 0, 0, 0))
    total_pixels = diff.width * diff.height
    percent = (diff_pixels / total_pixels) * 100

    red_overlay = Image.new("RGBA", actual.size, (255, 0, 0, 0))
    draw = ImageDraw.Draw(red_overlay)
    for x in range(diff.width):
        for y in range(diff.height):
            if diff.getpixel((x, y)) != (0, 0, 0, 0):
                draw.point((x, y), fill=(255, 0, 0, alpha))

    combined = Image.alpha_composite(actual, red_overlay)
    combined.save(diff_path)
    return percent


@allure.title("Visual regression test: DemoQA homepage")
def test_visual_demoqa_homepage():
    ctx, page = new_context_page(headless=HEADLESS)

    try:
        with allure.step("Открываем страницу DemoQA"):
            page.goto("https://demoqa.com", timeout=60000)

            # Awaitility-style ожидание загрузки страницы
            wait_until(
                lambda: page.evaluate("document.readyState") == "complete",
                timeout=15,
                message="Страница DemoQA не загрузилась полностью"
            )

            wait_until(
                lambda: page.query_selector("div.home-banner, div.category-cards") is not None,
                timeout=10,
                message="Ключевые элементы DemoQA не появились"
            )

        with allure.step("Создаём скриншот фактического состояния"):
            actual_path = "build/screenshots/actual/homepage_actual.png"
            os.makedirs(os.path.dirname(actual_path), exist_ok=True)
            page.screenshot(path=actual_path, full_page=True)
            allure.attach.file(actual_path, name="Actual screenshot", attachment_type=allure.attachment_type.PNG)

        baseline = "src/test/resources/screenshots/expected/demoqa_home.png"

        if not os.path.exists(baseline):
            with allure.step("Создаём baseline (если отсутствует)"):
                os.makedirs(os.path.dirname(baseline), exist_ok=True)
                copyfile(actual_path, baseline)
                allure.attach.file(baseline, name="Baseline created", attachment_type=allure.attachment_type.PNG)
                return

        with allure.step("Сравниваем baseline и фактическое изображение"):
            diff_path = "build/screenshots/actual/homepage_diff.png"
            percent = create_diff_overlay(baseline, actual_path, diff_path)
            allure.attach.file(diff_path, name="Diff overlay", attachment_type=allure.attachment_type.PNG)
            assert percent < 2.0, f"Difference percentage {percent:.2f}% >= 2%"

    finally:
        with allure.step("Закрываем браузерный контекст"):
            try:
                ctx.close()
            except Exception:
                pass
