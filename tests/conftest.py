"""Pytest configuration and shared fixtures for SauceDemo UI automation.

Handles WebDriver initialization, teardown, CLI configuration options,
pre-authenticated session fixtures, and failure screenshot capture.
"""

import os
import datetime
from pathlib import Path
from typing import Generator
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.config import Config
from pages.login_page import LoginPage


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default=Config.BROWSER,
        help="Target browser: chrome or edge (defaults to config or env)",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed (visible) mode (overrides default headless)",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Force headless mode",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Pytest hook to capture test execution status and attach failure screenshots to reports."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    # Capture screenshot if test execution call failed
    if report.when == "call" and report.failed:
        driver = getattr(item, "_driver", None)
        if driver:
            screenshots_dir = Path(__file__).resolve().parent.parent / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in item.name)
            screenshot_filename = f"{clean_name}_{timestamp}.png"
            screenshot_filepath = screenshots_dir / screenshot_filename

            try:
                driver.save_screenshot(str(screenshot_filepath))
                # If pytest-html is active, attach screenshot to the HTML report
                try:
                    import pytest_html
                    extra_img = pytest_html.extras.image(str(screenshot_filepath))
                    extras = getattr(report, "extras", None)
                    if extras is not None and isinstance(extras, list):
                        extras.append(extra_img)
                    else:
                        report.extras = [extra_img]
                except (ImportError, Exception):
                    pass
            except Exception as e:
                print(f"\n[Warning] Failed to capture failure screenshot: {e}")


@pytest.fixture(scope="function")
def driver(request: pytest.FixtureRequest) -> Generator[webdriver.Remote, None, None]:
    """Initialize and manage WebDriver instance lifecycle per test function.

    Setup:
      - Determines browser type and execution mode (headless vs headed)
      - Configures standard viewport and performance flags
      - Navigates to base URL
    Teardown:
      - Quits the driver cleanly
    """
    browser_name = request.config.getoption("--browser").lower()
    force_headed = request.config.getoption("--headed")
    force_headless = request.config.getoption("--headless")

    if force_headed:
        is_headless = False
    elif force_headless:
        is_headless = True
    else:
        is_headless = Config.HEADLESS

    # Instantiate chosen browser driver
    if browser_name == "edge":
        options = EdgeOptions()
        if is_headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        try:
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver_instance = webdriver.Edge(service=service, options=options)
        except Exception:
            # Fallback to native Selenium Manager
            driver_instance = webdriver.Edge(options=options)

    else:  # Default to Chrome
        options = ChromeOptions()
        if is_headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver_instance = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback to native Selenium Manager (built-in to Selenium 4.10+)
            driver_instance = webdriver.Chrome(options=options)

    # Attach driver instance to pytest node so screenshot hook can access it
    request.node._driver = driver_instance

    driver_instance.set_page_load_timeout(30)
    driver_instance.maximize_window()
    driver_instance.get(Config.BASE_URL)

    yield driver_instance

    # Teardown
    try:
        driver_instance.quit()
    except Exception:
        pass


@pytest.fixture(scope="function")
def logged_in_driver(driver: webdriver.Remote) -> webdriver.Remote:
    """Pre-authenticated fixture that logs into SauceDemo as standard_user.

    Yields driver positioned directly on the Inventory/Products page,
    reducing boilerplate for catalog, cart, and checkout tests.
    """
    login_page = LoginPage(driver)
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)
    return driver
