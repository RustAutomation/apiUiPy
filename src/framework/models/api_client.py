import requests
import allure
import json


class ApiClient:
    def __init__(self, base_url: str, token: str = None):
        """
        Базовый API-клиент.
        :param base_url: базовый URL API
        :param token: Bearer-токен (опционально)
        """
        self.base_url = base_url
        self.session = requests.Session()

        # Добавляем заголовок авторизации, если передан токен
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

        # Общие заголовки
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    @allure.step("Отправляем {method} запрос на {endpoint}")
    def request(self, method: str, endpoint: str, **kwargs):
        """Универсальный метод для выполнения HTTP-запросов с логированием."""
        url = f"{self.base_url}{endpoint}"

        # Логируем запрос
        allure.attach(
            json.dumps({
                "method": method,
                "url": url,
                "headers": {**self.session.headers, **kwargs.get("headers", {})},
                "params": kwargs.get("params", {}),
                "body": kwargs.get("json", kwargs.get("data", {}))
            }, indent=2, ensure_ascii=False),
            name="Request",
            attachment_type=allure.attachment_type.JSON
        )

        # Отправляем запрос
        response = self.session.request(method, url, **kwargs)

        # Логируем ответ
        try:
            body = response.json()
        except ValueError:
            body = response.text

        allure.attach(
            json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body
            }, indent=2, ensure_ascii=False),
            name="Response",
            attachment_type=allure.attachment_type.JSON
        )

        return response
