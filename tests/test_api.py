import allure
from src.framework.models.api_client import ApiClient
from src.framework.models.user_request import UserRequest
from src.framework.utils.assertions import (
    assert_status_code,
    assert_json_field,
    assert_json_contains,
    assert_response_time
)

# Для публичного API токен не нужен
BASE_URL = "https://reqres.in/api"
client = ApiClient(BASE_URL)

# Для реального API можно использовать:
# client = ApiClient("https://your-api.com/api", token="your_token_here")


@allure.title("GET /users?page=2")
def test_get_users():
    with allure.step("Получаем список пользователей"):
        resp = client.request("GET", "/users", params={"page": 2})
        assert resp.status_code == 200
        assert "data" in resp.json()


@allure.title("POST /users")
def test_create_user():
    with allure.step("Создаём нового пользователя"):
        payload = UserRequest(name="Rustam", job="QA Engineer")
        resp = client.request("POST", "/users", json=payload.to_dict())
        assert_status_code(resp, 201)
        assert resp.json()["name"] == "Rustam"


@allure.title("PUT /users/2")
def test_update_user_put():
    with allure.step("Обновляем пользователя (PUT)"):
        payload = UserRequest(name="Rustam", job="Lead QA")
        resp = client.request("PUT", "/users/2", json=payload.to_dict())
        assert_status_code(resp, 200)


@allure.title("PATCH /users/2")
def test_update_user_patch():
    with allure.step("Обновляем пользователя (PATCH)"):
        payload = {"job": "Automation Architect"}
        resp = client.request("PATCH", "/users/2", json=payload)
        assert_status_code(resp, 200)


@allure.title("DELETE /users/2")
def test_delete_user():
    with allure.step("Удаляем пользователя"):
        resp = client.request("DELETE", "/users/2")
        assert_status_code(resp, 200, 204)
