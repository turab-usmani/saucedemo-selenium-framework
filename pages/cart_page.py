"""Page Object representing the SauceDemo Shopping Cart page."""

from typing import List, Dict
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CartPage(BasePage):
    """Encapsulates locators and user interactions for the Cart page."""

    # --- Locators ---
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    CART_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item'], .cart_item")
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price'], .inventory_item_price")
    ITEM_QUANTITY = (By.CSS_SELECTOR, "[data-test='item-quantity'], .cart_quantity")
    CONTINUE_SHOPPING_BUTTON = (By.CSS_SELECTOR, "[data-test='continue-shopping'], #continue-shopping")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "[data-test='checkout'], #checkout")

    def is_loaded(self) -> bool:
        """Verify the cart page is loaded by checking page title visibility."""
        return self.is_element_displayed(self.PAGE_TITLE)

    def get_page_title(self) -> str:
        """Retrieve the cart page title text."""
        return self.get_text(self.PAGE_TITLE)

    def get_cart_item_names(self) -> List[str]:
        """Retrieve all item names currently in the cart."""
        elements = self.find_elements(self.ITEM_NAME)
        return [el.text.strip() for el in elements]

    def get_cart_items_details(self) -> List[Dict[str, str]]:
        """Retrieve details (name, price, quantity) for all items in the cart."""
        items = self.find_elements(self.CART_ITEMS)
        details = []
        for item in items:
            name = item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name").text.strip()
            price = item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-price'], .inventory_item_price").text.strip()
            qty = item.find_element(By.CSS_SELECTOR, "[data-test='item-quantity'], .cart_quantity").text.strip()
            details.append({"name": name, "price": price, "quantity": qty})
        return details

    def get_cart_count(self) -> int:
        """Return number of cart items displayed in the cart list."""
        return len(self.find_elements(self.CART_ITEMS))

    def _get_cart_item_row_by_name(self, item_name: str):
        """Internal helper to locate the cart item row matching the specified name."""
        items = self.find_elements(self.CART_ITEMS)
        for item in items:
            name_el = item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name")
            if name_el.text.strip().lower() == item_name.strip().lower():
                return item
        raise ValueError(f"Cart item '{item_name}' was not found in cart.")

    def remove_item_by_name(self, item_name: str) -> "CartPage":
        """Click the 'Remove' button for the specified cart item."""
        row = self._get_cart_item_row_by_name(item_name)
        button = row.find_element(By.TAG_NAME, "button")
        button.click()
        return self

    def click_continue_shopping(self) -> None:
        """Click 'Continue Shopping' to navigate back to the inventory page."""
        self.click(self.CONTINUE_SHOPPING_BUTTON)

    def click_checkout(self) -> None:
        """Click 'Checkout' to proceed to checkout step one."""
        btn = self.find_element(self.CHECKOUT_BUTTON)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            if "checkout-step-one" not in self.driver.current_url:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
