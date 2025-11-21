import allure
from playwright.sync_api import Page

class BasePage:

    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str):
        self.page.goto(url)
        self.remove_ads()

    def remove_ads(self):
        """Удаляет баннеры и iframe, которые могут закрывать элементы."""
        self.page.evaluate("""
            document.querySelectorAll('#fixedban, iframe').forEach(e => e.remove());
        """)

    def screenshot_attach(self, name: str):
        """Делает скрин и прикрепляет в Allure."""
        png = self.page.screenshot(full_page=True)
        allure.attach(png, name, allure.attachment_type.PNG)
        return png
