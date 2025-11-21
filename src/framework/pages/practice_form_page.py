import os
import random
from playwright.sync_api import Page
import allure


class PracticeFormPage:
    URL = "https://demoqa.com/automation-practice-form"

    SUBJECTS = ["Maths", "English", "Physics", "Chemistry", "Computer Science"]
    HOBBIES = [1, 2, 3]  # 1 = Sports, 2 = Reading, 3 = Music
    STATES = {
        "NCR": ["Delhi", "Gurgaon", "Noida"],
        "Uttar Pradesh": ["Agra", "Lucknow", "Merrut"],
        "Haryana": ["Karnal", "Panipat"],
        "Rajasthan": ["Jaipur", "Jaiselmer"]
    }

    def __init__(self, page: Page):
        self.page = page

    # -------------------------------------------------------------------------------------

    def open(self):
        self.page.goto(self.URL)
        # убрать баннеры
        self.page.evaluate("document.querySelectorAll('#fixedban, iframe').forEach(e => e.remove())")

    # -------------------------------------------------------------------------------------

    def fill_required_fields(self, data):
        self.page.fill("#firstName", data["firstName"])
        self.page.fill("#lastName", data["lastName"])
        self.page.fill("#userEmail", data["email"])

        # gender: случайный
        idx = random.randint(1, 3)
        self.page.click(f"label[for='gender-radio-{idx}']")

        self.page.fill("#userNumber", data["phone"])
        self.page.fill("#currentAddress", data["address"])

    # -------------------------------------------------------------------------------------

    def fill_subjects(self):
        subject = random.choice(self.SUBJECTS)
        self.page.fill("#subjectsInput", subject)
        self.page.keyboard.press("Enter")

    # -------------------------------------------------------------------------------------

    def fill_hobbies(self):
        hobby = random.choice(self.HOBBIES)
        self.page.click(f"label[for='hobbies-checkbox-{hobby}']")

    # -------------------------------------------------------------------------------------

    def upload_picture(self):
        """
        Картинку берём из expected скриншотов.
        Файл должен лежать по пути:
        tests/resources/screenshots/expected/picture.png
        """

        picture_path = "tests/resources/screenshots/expected/demoqa_home.png"

        if not os.path.exists(picture_path):
            raise FileNotFoundError(f"Test picture not found at: {os.path.abspath(picture_path)}")

        self.page.set_input_files("#uploadPicture", picture_path)

    # -------------------------------------------------------------------------------------

    def select_state_city(self):
        state = random.choice(list(self.STATES.keys()))
        city = random.choice(self.STATES[state])

        # Открываем и выбираем
        self.page.click("#state")
        self.page.click(f"div[id^='react-select'][id$='-option-0']")  # первый элемент списка

        self.page.click("#city")
        self.page.click(f"div[id^='react-select'][id$='-option-0']")

    # -------------------------------------------------------------------------------------

    def submit(self):
        self.page.click("#submit")

    # -------------------------------------------------------------------------------------

    def screenshot_attach(self, name: str):
        png = self.page.screenshot(full_page=True)
        allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)
