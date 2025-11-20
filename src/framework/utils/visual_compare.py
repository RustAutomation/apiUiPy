import os
import allure
from shutil import copyfile
from PIL import Image, ImageChops, ImageDraw


class VisualComparer:
    def __init__(self,
                 baseline_dir="tests/resources/screenshots/expected",
                 actual_dir="build/screenshots/actual",
                 diff_dir="build/screenshots/diff",
                 threshold_percent=2.0):
        self.baseline_dir = baseline_dir
        self.actual_dir = actual_dir
        self.diff_dir = diff_dir
        self.threshold = threshold_percent

        os.makedirs(self.baseline_dir, exist_ok=True)
        os.makedirs(self.actual_dir, exist_ok=True)
        os.makedirs(self.diff_dir, exist_ok=True)

    def _create_diff_overlay(self, baseline_path, actual_path, diff_path, alpha=120):
        """Создаёт diff с красным прозрачным overlay."""
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

    def compare(self, page, name: str):
        """
        Полный цикл: снимает screenshot → создаёт baseline если нет → сравнивает → генерит diff.
        """

        actual_path = f"{self.actual_dir}/{name}.png"
        baseline_path = f"{self.baseline_dir}/{name}.png"
        diff_path = f"{self.diff_dir}/{name}_diff.png"

        with allure.step("Создаём фактический скриншот"):
            page.screenshot(path=actual_path, full_page=True)
            allure.attach.file(actual_path, name="Actual screenshot",
                               attachment_type=allure.attachment_type.PNG)

        # ---- Baseline creation ----
        if not os.path.exists(baseline_path):
            with allure.step("Baseline отсутствует — создаём"):
                copyfile(actual_path, baseline_path)
                allure.attach.file(baseline_path, name="Baseline created",
                                   attachment_type=allure.attachment_type.PNG)
                return

        # ---- Comparison ----
        with allure.step("Сравнение baseline и фактического изображения"):
            percent = self._create_diff_overlay(baseline_path, actual_path, diff_path)
            allure.attach.file(diff_path, name="Diff overlay",
                               attachment_type=allure.attachment_type.PNG)

            assert percent < self.threshold, \
                f"Difference {percent:.2f}% ≥ threshold {self.threshold}%"
