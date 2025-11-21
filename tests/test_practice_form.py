from src.framework.utils.data_generator import first_name, last_name, email, phone_number, address
from src.framework.pages.practice_form_page import PracticeFormPage
from src.framework.utils.visual_compare import VisualComparer
from src.framework.utils.wait_until import wait_until
import allure

visual = VisualComparer()

def test_practice_form(page):
    form = PracticeFormPage(page)

    data = {
        "firstName": first_name(),
        "lastName": last_name(),
        "email": email(),
        "phone": phone_number(),
        "address": address()
    }

    with allure.step("Open form and fill data"):
        form.open()
        form.fill_required_fields(data)
        form.fill_subjects()
        form.fill_hobbies()
        form.upload_picture()
        form.select_state_city()

        form.screenshot_attach("filled_form_before_submit")

    with allure.step("Submit form"):
        form.submit()
        form.screenshot_attach("after_submit")

    with allure.step("Visual regression check: result modal/table"):
        wait_until(
            lambda: page.evaluate("document.readyState") == "complete",
            timeout=15,
        )

        visual.compare(page, "practice_form_result")
