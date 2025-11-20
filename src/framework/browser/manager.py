import os
from playwright.sync_api import sync_playwright

HEADLESS = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")

_playwright = None
_browser = None


def start_browser():
    global _playwright, _browser
    if _playwright is None:
        _playwright = sync_playwright().start()
    if _browser is None:
        _browser = _playwright.chromium.launch(headless=HEADLESS)
    return _browser


def new_context_page():
    b = start_browser()
    context = b.new_context()
    page = context.new_page()
    return context, page


def stop_browser():
    global _playwright, _browser
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None
