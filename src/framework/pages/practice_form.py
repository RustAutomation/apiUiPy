from playwright.sync_api import Page
from typing import Dict
from src.framework.utils.allure_helper import attach_screenshot

class PracticeFormPage:
    URL = "https://demoqa.com/automation-practice-form"

    def __init__(self, page: Page):
        self.page = page

    def open(self, timeout=60000):
        self.page.goto(self.URL, timeout=timeout)
        try:
            self.page.evaluate("() => { const el = document.querySelector('#fixedban'); if(el) el.remove(); }")
        except Exception:
            pass
        return self

    def fill_required_fields(self, data: Dict):
        self.page.fill("#firstName", data["firstName"])
        self.page.fill("#lastName", data["lastName"])
        self.page.fill("#userEmail", data["email"])
        labels = self.page.query_selector_all("label[for^='gender-radio']")
        if labels:
            for lbl in labels:
                try:
                    lbl.click()
                    break
                except:
                    continue
        self.page.fill("#userNumber", data["phone"])
        return self

    def submit(self):
        self.page.locator("#submit").scroll_into_view_if_needed()
        self.page.click("#submit")
        return self

    def read_result_table(self):
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
