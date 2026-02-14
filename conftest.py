import logging
import pytest

pytest_plugins = ["pytest_playwright"]

DEFAULT_TIMEOUT_MS = 10000
DEFAULT_VIEWPORT = {"width": 1920, "height": 1080}  # type: ignore

# Hide loggers during tests
def pytest_configure(config):
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

@pytest.fixture
def context(browser):
    context = browser.new_context(viewport=DEFAULT_VIEWPORT)  # type: ignore[arg-type]
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    yield page
    page.close()
