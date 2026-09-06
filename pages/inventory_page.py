"""Page Object representing the SauceDemo Products/Inventory page."""

from typing import List
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Encapsulates locators and user interactions for the product inventory catalog."""

    # --- Locators ---
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    INVENTORY_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item'], .inventory_item")
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price'], .inventory_item_price")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[data-test='product-sort-container'], .product_sort_container")
    ACTIVE_OPTION = (By.CSS_SELECTOR, "[data-test='active-option'], .active_option")
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link'], .shopping_cart_link")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge'], .shopping_cart_badge")
    BURGER_MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def is_loaded(self) -> bool:
        """Verify the inventory page is loaded by checking page title visibility."""
        return self.is_element_displayed(self.PAGE_TITLE)

    def get_page_title(self) -> str:
        """Retrieve the inventory page title text."""
        return self.get_text(self.PAGE_TITLE)

    def get_all_item_names(self) -> List[str]:
        """Return a list of all product names currently displayed on the catalog."""
        elements = self.find_elements(self.ITEM_NAME)
        return [el.text.strip() for el in elements]

    def get_all_item_prices(self) -> List[float]:
        """Return a list of all product prices parsed as floats."""
        elements = self.find_elements(self.ITEM_PRICE)
        prices = []
        for el in elements:
            # Strip currency symbol e.g., "$29.99" -> 29.99
            clean_price = el.text.strip().replace("$", "")
            prices.append(float(clean_price))
        return prices

    def select_sort_option(self, option_value: str) -> "InventoryPage":
        """Sort products using dropdown value: 'az', 'za', 'lohi', 'hilo'."""
        self.select_dropdown_by_value(self.SORT_DROPDOWN, option_value)
        return self

    def get_active_sort_option_text(self) -> str:
        """Return the visible text of the active sort option."""
        return self.get_text(self.ACTIVE_OPTION)

    def _get_item_card_by_name(self, item_name: str):
        """Internal helper to locate the parent product container matching the item name."""
        items = self.find_elements(self.INVENTORY_ITEMS)
        for item in items:
            name_el = item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name'], .inventory_item_name")
            if name_el.text.strip().lower() == item_name.strip().lower():
                return item
        raise ValueError(f"Product '{item_name}' was not found in the inventory list.")

    def add_item_to_cart_by_name(self, item_name: str) -> "InventoryPage":
        """Click the 'Add to cart' button for a specific product."""
        card = self._get_item_card_by_name(item_name)
        button = card.find_element(By.TAG_NAME, "button")
        button.click()
        return self

    def remove_item_from_inventory_by_name(self, item_name: str) -> "InventoryPage":
        """Click the 'Remove' button for a specific product."""
        card = self._get_item_card_by_name(item_name)
        button = card.find_element(By.TAG_NAME, "button")
        button.click()
        return self

    def get_item_button_text(self, item_name: str) -> str:
        """Return the current button text ('Add to cart' or 'Remove') for a given product."""
        card = self._get_item_card_by_name(item_name)
        button = card.find_element(By.TAG_NAME, "button")
        return button.text.strip()

    def get_cart_badge_count(self) -> int:
        """Retrieve the item count indicated on the shopping cart badge, or 0 if badge is absent."""
        if not self.is_element_displayed(self.CART_BADGE, timeout=1):
            return 0
        badge_text = self.get_text(self.CART_BADGE)
        return int(badge_text) if badge_text.isdigit() else 0

    def is_cart_badge_displayed(self) -> bool:
        """Check if the shopping cart counter badge is visible."""
        return self.is_element_displayed(self.CART_BADGE, timeout=1)

    def click_cart(self) -> None:
        """Navigate to the shopping cart page."""
        btn = self.find_element(self.CART_LINK)
        try:
            btn.click()
            if "cart.html" not in self.driver.current_url:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def logout(self) -> None:
        """Open the burger sidebar and click the logout option."""
        self.click(self.BURGER_MENU_BUTTON)
        self.click(self.LOGOUT_LINK)
