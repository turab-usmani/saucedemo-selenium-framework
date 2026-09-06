"""Page Object representing the SauceDemo Login page."""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import Config


class LoginPage(BasePage):
    """Encapsulates locators and user interactions for the Login page."""

    # --- Locators ---
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    LOGIN_CONTAINER = (By.CLASS_NAME, "login_wrapper")

    def __init__(self, driver):
        super().__init__(driver)
        self.url = Config.BASE_URL

    def navigate(self) -> "LoginPage":
        """Navigate to the login page."""
        self.open_url(self.url)
        return self

    def is_loaded(self) -> bool:
        """Check if the login page is loaded by checking visibility of the login button."""
        return self.is_element_displayed(self.LOGIN_BUTTON)

    def enter_username(self, username: str) -> "LoginPage":
        """Type username into the username field."""
        self.type_text(self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Type password into the password field."""
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> None:
        """Click the login button."""
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str) -> None:
        """Convenience action method to fill credentials and submit login."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        """Retrieve the text of the login error banner."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        """Check if an error banner is visible."""
        return self.is_element_displayed(self.ERROR_MESSAGE)
