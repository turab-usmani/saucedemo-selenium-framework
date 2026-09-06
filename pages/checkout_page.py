"""Page Objects representing the multi-step Checkout flow."""

import re
from typing import List
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CheckoutStepOnePage(BasePage):
    """Encapsulates locators and interactions for Step 1: Customer Information."""

    # --- Locators ---
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE_INPUT = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "[data-test='continue']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-test='cancel']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def is_loaded(self) -> bool:
        """Check if Step 1 is loaded."""
        return self.wait_for_url_contains("checkout-step-one") and self.is_element_displayed(self.CONTINUE_BUTTON)

    def get_page_title(self) -> str:
        """Retrieve page title."""
        return self.get_text(self.PAGE_TITLE)

    def enter_first_name(self, first_name: str) -> "CheckoutStepOnePage":
        """Type first name."""
        self.type_text(self.FIRST_NAME_INPUT, first_name)
        return self

    def enter_last_name(self, last_name: str) -> "CheckoutStepOnePage":
        """Type last name."""
        self.type_text(self.LAST_NAME_INPUT, last_name)
        return self

    def enter_postal_code(self, postal_code: str) -> "CheckoutStepOnePage":
        """Type postal/zip code."""
        self.type_text(self.POSTAL_CODE_INPUT, postal_code)
        return self

    def fill_information(self, first_name: str = "", last_name: str = "", postal_code: str = "") -> "CheckoutStepOnePage":
        """Convenience method to fill all customer information fields."""
        self.find_element(self.FIRST_NAME_INPUT)
        if first_name:
            self.enter_first_name(first_name)
        if last_name:
            self.enter_last_name(last_name)
        if postal_code:
            self.enter_postal_code(postal_code)
        return self

    def click_continue(self) -> None:
        """Click Continue button to advance to Step 2."""
        btn = self.find_element(self.CONTINUE_BUTTON)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            if "checkout-step-two" not in self.driver.current_url and not self.is_error_displayed():
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def click_cancel(self) -> None:
        """Click Cancel button to return to Cart."""
        self.click(self.CANCEL_BUTTON)

    def get_error_message(self) -> str:
        """Retrieve the validation error message text."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.is_element_displayed(self.ERROR_MESSAGE)


class CheckoutStepTwoPage(BasePage):
    """Encapsulates locators and interactions for Step 2: Overview & Pricing."""

    # --- Locators ---
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    CART_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item'], .cart_item")
    SUBTOTAL_LABEL = (By.CSS_SELECTOR, "[data-test='subtotal-label'], .summary_subtotal_label")
    TAX_LABEL = (By.CSS_SELECTOR, "[data-test='tax-label'], .summary_tax_label")
    TOTAL_LABEL = (By.CSS_SELECTOR, "[data-test='total-label'], .summary_total_label")
    FINISH_BUTTON = (By.CSS_SELECTOR, "[data-test='finish'], #finish")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-test='cancel'], #cancel")

    def is_loaded(self) -> bool:
        """Check if Step 2 is loaded."""
        return self.wait_for_url_contains("checkout-step-two") and self.is_element_displayed(self.FINISH_BUTTON)

    def get_page_title(self) -> str:
        """Retrieve page title."""
        return self.get_text(self.PAGE_TITLE)

    def _extract_dollar_amount(self, locator) -> float:
        """Helper to extract decimal dollar amounts from summary text."""
        text = self.get_text(locator)
        match = re.search(r"\$([0-9]+\.[0-9]{2})", text)
        if match:
            return float(match.group(1))
        raise ValueError(f"Could not extract dollar amount from label text: '{text}'")

    def get_item_subtotal(self) -> float:
        """Extract numeric item subtotal from 'Item total: $XX.XX'."""
        self.wait_for_url_contains("checkout-step-two")
        return self._extract_dollar_amount(self.SUBTOTAL_LABEL)

    def get_tax_amount(self) -> float:
        """Extract numeric tax from 'Tax: $X.XX'."""
        return self._extract_dollar_amount(self.TAX_LABEL)

    def get_total_amount(self) -> float:
        """Extract numeric total from 'Total: $XX.XX'."""
        return self._extract_dollar_amount(self.TOTAL_LABEL)

    def get_cart_item_names(self) -> List[str]:
        """Retrieve product names listed in the overview."""
        elements = self.find_elements((By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name"))
        return [el.text.strip() for el in elements]

    def click_finish(self) -> None:
        """Click Finish to finalize purchase order."""
        btn = self.find_element(self.FINISH_BUTTON)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            # If standard click didn't navigate immediately, trigger via JS
            if "checkout-complete" not in self.driver.current_url:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def click_cancel(self) -> None:
        """Click Cancel to return to inventory catalog."""
        btn = self.find_element(self.CANCEL_BUTTON)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            if "inventory" not in self.driver.current_url:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)


class CheckoutCompletePage(BasePage):
    """Encapsulates locators and interactions for the final Checkout Complete page."""

    # --- Locators ---
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    COMPLETE_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header'], .complete-header")
    COMPLETE_TEXT = (By.CSS_SELECTOR, "[data-test='complete-text'], .complete-text")
    BACK_HOME_BUTTON = (By.CSS_SELECTOR, "[data-test='back-to-products'], #back-to-products")

    def is_loaded(self) -> bool:
        """Check if Complete confirmation page is displayed."""
        return self.wait_for_url_contains("checkout-complete") and self.is_element_displayed(self.COMPLETE_HEADER)

    def get_page_title(self) -> str:
        """Retrieve page title."""
        return self.get_text(self.PAGE_TITLE)

    def get_confirmation_header(self) -> str:
        """Retrieve confirmation header text (e.g., 'Thank you for your order!')."""
        return self.get_text(self.COMPLETE_HEADER)

    def get_confirmation_text(self) -> str:
        """Retrieve confirmation description text."""
        return self.get_text(self.COMPLETE_TEXT)

    def click_back_home(self) -> None:
        """Click 'Back Home' button to return to the inventory catalog."""
        btn = self.find_element(self.BACK_HOME_BUTTON)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            if "inventory" not in self.driver.current_url:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
