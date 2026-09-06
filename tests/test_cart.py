"""Tests for the SauceDemo Cart functionality.

Covers:
- Adding items to cart and verifying their presence and details in the Cart view
- Removing items directly from the cart
- Navigating back to the catalog via 'Continue Shopping'
"""

import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@pytest.mark.cart
@pytest.mark.smoke
def test_items_added_appear_in_cart(logged_in_driver):
    """Verify that items added from inventory appear accurately in the cart."""
    items_to_add = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
    inventory_page = InventoryPage(logged_in_driver)

    for item in items_to_add:
        inventory_page.add_item_to_cart_by_name(item)

    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    assert cart_page.is_loaded(), "Cart page failed to load"
    assert cart_page.get_page_title() == "Your Cart", "Cart page title does not match 'Your Cart'"

    cart_item_names = cart_page.get_cart_item_names()
    for item in items_to_add:
        assert item in cart_item_names, f"Item '{item}' was not found in the cart"

    assert cart_page.get_cart_count() == len(items_to_add)


@pytest.mark.cart
@pytest.mark.regression
def test_remove_item_from_cart(logged_in_driver):
    """Verify that removing an item from the cart updates the cart list correctly."""
    item_to_remove = "Sauce Labs Backpack"
    item_to_keep = "Sauce Labs Bike Light"

    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.add_item_to_cart_by_name(item_to_remove)
    inventory_page.add_item_to_cart_by_name(item_to_keep)
    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    assert cart_page.get_cart_count() == 2

    cart_page.remove_item_by_name(item_to_remove)

    updated_names = cart_page.get_cart_item_names()
    assert item_to_remove not in updated_names, f"Item '{item_to_remove}' was still present after removal"
    assert item_to_keep in updated_names, f"Item '{item_to_keep}' was unexpectedly removed"
    assert cart_page.get_cart_count() == 1


@pytest.mark.cart
@pytest.mark.regression
def test_continue_shopping_navigation(logged_in_driver):
    """Verify that clicking 'Continue Shopping' navigates back to the inventory page."""
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    cart_page.click_continue_shopping()

    assert inventory_page.is_loaded(), "Failed to return to Inventory page from Cart"
    assert "inventory.html" in inventory_page.get_current_url()
