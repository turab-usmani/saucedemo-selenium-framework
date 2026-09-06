"""Tests for the SauceDemo Login functionality.

Covers:
- Valid login (happy path)
- Locked out user validation
- Empty fields validation
- Data-driven invalid credential combinations
"""

import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from config.config import Config


@pytest.mark.login
@pytest.mark.smoke
def test_successful_login(driver):
    """Verify that a valid user can successfully log in and is redirected to inventory."""
    login_page = LoginPage(driver)
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)

    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded(), "Inventory page failed to load after valid login"
    assert "inventory.html" in inventory_page.get_current_url(), "URL does not contain 'inventory.html'"
    assert inventory_page.get_page_title() == "Products", "Inventory title does not match 'Products'"


@pytest.mark.login
@pytest.mark.regression
def test_locked_out_user_error(driver):
    """Verify that attempting to log in with a locked out user displays the proper error."""
    login_page = LoginPage(driver)
    login_page.login(Config.LOCKED_OUT_USER, Config.PASSWORD)

    assert login_page.is_error_displayed(), "Expected error message banner was not displayed"
    error_text = login_page.get_error_message()
    assert "Sorry, this user has been locked out" in error_text, (
        f"Unexpected error message: '{error_text}'"
    )


@pytest.mark.login
@pytest.mark.regression
def test_empty_username_validation(driver):
    """Verify that submitting login with an empty username shows a required error."""
    login_page = LoginPage(driver)
    login_page.login("", Config.PASSWORD)

    assert login_page.is_error_displayed(), "Expected error message for empty username"
    assert "Username is required" in login_page.get_error_message()


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.parametrize(
    "username, password, expected_error_snippet",
    [
        (
            "standard_user",
            "wrong_password_123",
            "Username and password do not match any user in this service",
        ),
        (
            "unknown_invalid_user",
            "secret_sauce",
            "Username and password do not match any user in this service",
        ),
        (
            "standard_user",
            "",
            "Password is required",
        ),
    ],
    ids=["wrong_password", "unknown_user", "empty_password"],
)
def test_invalid_credentials_parametrized(driver, username, password, expected_error_snippet):
    """Data-driven test verifying validation messages for various invalid credential inputs."""
    login_page = LoginPage(driver)
    login_page.login(username, password)

    assert login_page.is_error_displayed(), f"Error message expected for user='{username}'"
    assert expected_error_snippet in login_page.get_error_message(), (
        f"Expected snippet '{expected_error_snippet}' not found in '{login_page.get_error_message()}'"
    )
