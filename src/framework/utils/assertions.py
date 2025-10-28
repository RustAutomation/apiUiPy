import allure
import json


def assert_status_code(response, *expected_codes):
    """
    Проверяет, что статус-код входит в список допустимых.
    """
    status_code = response.status_code
    expected_str = ", ".join(map(str, expected_codes))

    if status_code not in expected_codes:
        allure.attach(
            response.text,
            name=f"Response body ({status_code})",
            attachment_type=allure.attachment_type.JSON
        )
        raise AssertionError(
            f"❌ Ожидался статус {expected_str}, но получен {status_code}\n"
            f"URL: {response.url}\n"
            f"Ответ: {response.text}"
        )

    allure.attach(
        f"✅ Статус {status_code} соответствует ожидаемому ({expected_str})",
        name="Status check",
        attachment_type=allure.attachment_type.TEXT
    )


def assert_json_field(response, field_path, expected_value):
    """
    Проверяет, что значение по указанному полю JSON совпадает с ожидаемым.
    Пример field_path: "data.id" → проверит response.json()["data"]["id"].
    """
    with allure.step(f"Проверяем поле '{field_path}' в JSON ответе"):
        try:
            data = response.json()
        except json.JSONDecodeError:
            allure.attach(response.text, "Response body", allure.attachment_type.TEXT)
            raise AssertionError("Ответ не является валидным JSON")

        keys = field_path.split(".")
        actual = data
        for key in keys:
            if key not in actual:
                allure.attach(json.dumps(data, indent=2, ensure_ascii=False), "Full JSON", allure.attachment_type.JSON)
                raise AssertionError(f"Поле '{field_path}' отсутствует в ответе")
            actual = actual[key]

        if actual != expected_value:
            allure.attach(json.dumps(data, indent=2, ensure_ascii=False), "Full JSON", allure.attachment_type.JSON)
            raise AssertionError(f"❌ Поле '{field_path}' = {actual}, ожидалось {expected_value}")

        allure.attach(
            f"✅ Поле '{field_path}' = {actual} соответствует ожидаемому {expected_value}",
            name="JSON field check",
            attachment_type=allure.attachment_type.TEXT
        )


def assert_json_contains(response, expected_fields):
    """
    Проверяет, что в JSON-ответе присутствуют указанные поля верхнего уровня.
    expected_fields: list[str]
    """
    with allure.step(f"Проверяем наличие полей {expected_fields} в JSON ответе"):
        try:
            data = response.json()
        except json.JSONDecodeError:
            allure.attach(response.text, "Response body", allure.attachment_type.TEXT)
            raise AssertionError("Ответ не является валидным JSON")

        missing = [f for f in expected_fields if f not in data]
        if missing:
            allure.attach(json.dumps(data, indent=2, ensure_ascii=False), "Full JSON", allure.attachment_type.JSON)
            raise AssertionError(f"❌ В ответе отсутствуют поля: {missing}")

        allure.attach(
            f"✅ Все поля {expected_fields} присутствуют в JSON ответе",
            name="JSON contains check",
            attachment_type=allure.attachment_type.TEXT
        )


def assert_response_time(response, max_ms):
    """
    Проверяет, что время ответа не превышает max_ms миллисекунд.
    """
    with allure.step(f"Проверяем время ответа ≤ {max_ms} мс"):
        elapsed_ms = response.elapsed.total_seconds() * 1000
        if elapsed_ms > max_ms:
            allure.attach(
                f"{elapsed_ms:.2f} ms",
                name="Response time",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"❌ Время ответа {elapsed_ms:.2f} мс превышает {max_ms} мс")

        allure.attach(
            f"✅ Время ответа {elapsed_ms:.2f} мс ≤ {max_ms} мс",
            name="Response time check",
            attachment_type=allure.attachment_type.TEXT
        )
