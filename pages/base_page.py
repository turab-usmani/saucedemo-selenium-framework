"""Base Page class providing common web interaction wrappers and explicit wait helpers.

Architectural Note on Wait Strategy:
------------------------------------
In UI test automation, arbitrary `time.sleep()` statements cause brittle, flaky,
or unnecessarily sluggish test executions. Similarly, Selenium's implicit waits apply
a blanket polling timer that can mask asynchronous rendering issues or clash unpredictably
with explicit waits.

This framework strictly employs EXPLICIT WAITS (`WebDriverWait` paired with `expected_conditions`)
across all page objects. Explicit waits poll the DOM dynamically until the specific condition
(e.g., visibility, clickability, URL transformation) is satisfied, returning immediately upon
success or raising a descriptive `TimeoutException` after the timeout threshold.
"""

from typing import List, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import Config


class BasePage:
    """Base class for all Page Objects in the Page Object Model (POM)."""

    def __init__(self, driver: WebDriver, timeout: int = Config.DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, self.timeout)

    def _get_wait(self, timeout: int | None = None) -> WebDriverWait:
        """Helper to retrieve a WebDriverWait instance with custom or default timeout."""
        return WebDriverWait(self.driver, timeout if timeout is not None else self.timeout)

    def open_url(self, url: str) -> None:
        """Navigate to the specified URL."""
        self.driver.get(url)

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.driver.current_url

    def get_title(self) -> str:
        """Return the current document title."""
        return self.driver.title

    def find_element(self, locator: Tuple[str, str], timeout: int | None = None) -> WebElement:
        """Wait for an element to be visible on the DOM and return it.

        :param locator: Tuple of (By.<LOCATOR_TYPE>, "selector")
        :param timeout: Optional override for the default explicit wait timeout
        :return: Located WebElement
        """
        wait = self._get_wait(timeout)
        return wait.until(
            EC.visibility_of_element_located(locator),
            message=f"Element with locator {locator} was not visible within {timeout or self.timeout}s"
        )

    def find_element_present(self, locator: Tuple[str, str], timeout: int | None = None) -> WebElement:
        """Wait for an element to be present in the DOM (not necessarily visible) and return it."""
        wait = self._get_wait(timeout)
        return wait.until(
            EC.presence_of_element_located(locator),
            message=f"Element with locator {locator} was not present within {timeout or self.timeout}s"
        )

    def find_elements(self, locator: Tuple[str, str], timeout: int | None = None) -> List[WebElement]:
        """Wait for at least one element to be present in the DOM, then return all matching elements."""
        wait = self._get_wait(timeout)
        try:
            wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def click(self, locator: Tuple[str, str], timeout: int | None = None) -> None:
        """Wait for an element to be clickable and click it."""
        wait = self._get_wait(timeout)
        element = wait.until(
            EC.element_to_be_clickable(locator),
            message=f"Element with locator {locator} was not clickable within {timeout or self.timeout}s"
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()

    def type_text(
        self,
        locator: Tuple[str, str],
        text: str,
        clear_first: bool = True,
        timeout: int | None = None
    ) -> None:
        """Wait for an input element, optionally clear it, and enter text."""
        element = self.find_element(locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
        # Ensure React synthetic state receives text if browser dropped keystrokes
        if text and element.get_attribute("value") != text:
            self.driver.execute_script(
                """
                var el = arguments[0];
                var val = arguments[1];
                var lastVal = el.value;
                el.value = val;
                var tracker = el._valueTracker;
                if (tracker) {
                    tracker.setValue(lastVal);
                }
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                """,
                element,
                text
            )

    def get_text(self, locator: Tuple[str, str], timeout: int | None = None) -> str:
        """Wait for an element to be visible and return its stripped inner text."""
        return self.find_element(locator, timeout).text.strip()

    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int | None = None) -> str | None:
        """Retrieve an attribute value from the targeted element."""
        return self.find_element(locator, timeout).get_attribute(attribute)

    def is_element_displayed(self, locator: Tuple[str, str], timeout: int = 2) -> bool:
        """Check if an element is currently displayed without raising a TimeoutException."""
        try:
            wait = self._get_wait(timeout)
            return wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_url_contains(self, partial_url: str, timeout: int | None = None) -> bool:
        """Wait until the current URL contains the expected substring."""
        wait = self._get_wait(timeout)
        return bool(wait.until(
            EC.url_contains(partial_url),
            message=f"URL did not contain '{partial_url}' within {timeout or self.timeout}s"
        ))

    def select_dropdown_by_value(self, locator: Tuple[str, str], value: str, timeout: int | None = None) -> None:
        """Select an option in a <select> element by its 'value' attribute."""
        element = self.find_element(locator, timeout)
        select = Select(element)
        select.select_by_value(value)

    def select_dropdown_by_text(self, locator: Tuple[str, str], text: str, timeout: int | None = None) -> None:
        """Select an option in a <select> element by visible text."""
        element = self.find_element(locator, timeout)
        select = Select(element)
        select.select_by_visible_text(text)

    def get_selected_dropdown_text(self, locator: Tuple[str, str], timeout: int | None = None) -> str:
        """Return the visible text of the currently selected option in a <select> element."""
        element = self.find_element(locator, timeout)
        select = Select(element)
        return select.first_selected_option.text.strip()
