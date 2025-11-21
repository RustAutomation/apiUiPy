import os
from PIL import Image
import numpy as np
import allure


class VisualComparer:

    def compare(self, page, name: str, threshold: float = 2.0):
        baseline_path = f"tests/resources/screenshots/expected/{name}.png"
        actual_path = f"build/screenshots/actual/{name}_actual.png"
        diff_path = f"build/screenshots/diff/{name}_diff.png"

        os.makedirs(os.path.dirname(actual_path), exist_ok=True)
        os.makedirs(os.path.dirname(diff_path), exist_ok=True)

        page.screenshot(path=actual_path, full_page=True)

        if not os.path.exists(baseline_path):
            os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
            page.screenshot(path=baseline_path, full_page=True)
            allure.attach.file(baseline_path, "baseline created", allure.attachment_type.PNG)
            return

        diff_percent = self._compare_files(baseline_path, actual_path, diff_path)

        allure.attach.file(diff_path, "diff", allure.attachment_type.PNG)

        assert diff_percent < threshold, f"Difference {diff_percent:.2f}% >= {threshold}%"

    # ----------------------------------------------------------------------

    def _compare_files(self, baseline_path, actual_path, diff_path):
        baseline = Image.open(baseline_path).convert("RGBA")
        actual = Image.open(actual_path).convert("RGBA")

        w = min(baseline.width, actual.width)
        h = min(baseline.height, actual.height)

        baseline = baseline.crop((0, 0, w, h))
        actual = actual.crop((0, 0, w, h))

        base_arr = np.array(baseline)
        act_arr = np.array(actual)

        diff_mask = np.any(base_arr != act_arr, axis=-1)
        diff_pixels = np.sum(diff_mask)
        diff_percent = (diff_pixels / (w * h)) * 100.0

        # --- прозрачный красный overlay ---
        highlight = act_arr.copy()
        highlight[..., 3] = 0  # прозрачный слой

        red_transparent = np.array([255, 0, 0, 120])
        highlight[diff_mask] = red_transparent

        result = Image.alpha_composite(
            Image.fromarray(act_arr, "RGBA"),
            Image.fromarray(highlight, "RGBA")
        )

        os.makedirs(os.path.dirname(diff_path), exist_ok=True)
        result.save(diff_path)

        return diff_percent

    # ----------------------------------------------------------------------

    @staticmethod
    def compare_images(expected_path: str, actual_path: str, diff_path: str, threshold: float = 2.0):
        comparer = VisualComparer()
        diff_percent = comparer._compare_files(expected_path, actual_path, diff_path)
        assert diff_percent < threshold, f"Difference {diff_percent:.2f}% >= {threshold}%"
        return diff_percent
