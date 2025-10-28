import time


class AwaitilityTimeoutError(Exception):
    """Выбрасывается, если условие не выполнено за отведённое время."""
    pass


def wait_until(condition, timeout: float = 10, interval: float = 0.5, message: str = None):
    """
    Аналог Awaitility (Java) — ожидает выполнения условия.

    Args:
        condition: функция без аргументов, возвращающая bool (True, если условие выполнено)
        timeout: максимальное время ожидания (в секундах)
        interval: интервал между проверками (в секундах)
        message: сообщение для исключения при таймауте

    Raises:
        AwaitilityTimeoutError: если условие не выполнено за время timeout
    """
    start_time = time.time()
    while True:
        try:
            if condition():
                return True
        except Exception:
            # Игнорируем ошибки проверки (например, элемент не найден)
            pass
        if time.time() - start_time > timeout:
            raise AwaitilityTimeoutError(
                message or f"Condition not met within {timeout} seconds"
            )
        time.sleep(interval)
