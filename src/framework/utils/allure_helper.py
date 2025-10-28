import allure
from allure_commons.types import AttachmentType
import json


def attach_screenshot(name, bytes_img):
    allure.attach(bytes_img, name=name, attachment_type=AttachmentType.PNG)


def attach_text(name, text):
    allure.attach(text, name=name, attachment_type=AttachmentType.TEXT)


def attach_json(name, data):
    try:
        allure.attach(json.dumps(data, indent=2, ensure_ascii=False),
                      name=name, attachment_type=AttachmentType.JSON)
    except Exception:
        attach_text(name, str(data))
