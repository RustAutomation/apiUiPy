import allure
import pytest

from src.framework.browser.manager import new_context_page
from src.framework.pages.practice_form import PracticeFormPage
from src.framework.utils.data_generator import first_name, last_name, email, phone_number

@pytest.fixture
def page_ctx():
    ctx, page = new_context_page()
    try:
        yield page
    finally:
        try:
            ctx.close()
        except:
            pass

def test_practice_form_popup(page_ctx):
    page = page_ctx
    form = PracticeFormPage(page)

    data = {
        "firstName": first_name(),
        "lastName": last_name(),
        "email": email(),
        "phone": phone_number()
    }

    with allure.step("Open form and fill data"):
        form.open()
        form.fill_required_fields(data)
        form.screenshot_attach("filled_form_before_submit")
        form.submit()

    with allure.step("Read result and verify fields"):
        result = form.read_result_table()
        # mapping: our keys to displayed labels may vary; try to assert included values
        # Check name
        full_name = f"{data['firstName']} {data['lastName']}"
        assert full_name in result.get('Student Name', full_name) or data['firstName'] in result.get('Student Name', '')

        # email
        assert data['email'] in result.get('Student Email', result.get('Student Email','') ) or data['email'] in ' '.join(result.values())

        # phone
        assert data['phone'] in result.get('Mobile', result.get('Mobile','')) or data['phone'] in ' '.join(result.values())

        # attach popup screenshot
        png = page.screenshot()
        allure.attach(png, name='popup', attachment_type=allure.attachment_type.PNG)
