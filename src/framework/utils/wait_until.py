import time
from typing import Callable, Any


def wait_until(
    condition: Callable[[], Any],
    timeout: float = 5.0,
    interval: float = 0.1,
    fail_message: str = "Condition was not met in time"
) -> Any:
    """
    Waits until `condition()` returns truthy value or timeout is reached.

    :param condition: Function returning True when condition is met.
    :param timeout: Max wait time in seconds.
    :param interval: Polling interval in seconds.
    :param fail_message: Message for exception on timeout.
    :return: Value returned by condition() if successful.
    :raises TimeoutError: If condition was not met in time.
    """
    end = time.time() + timeout

    last_value = None

    while time.time() < end:
        last_value = condition()
        if last_value:
            return last_value
        time.sleep(interval)

    raise TimeoutError(f"{fail_message}. Last returned value: {last_value}")
