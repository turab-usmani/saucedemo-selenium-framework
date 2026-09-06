"""Tests for the SauceDemo Inventory/Product Catalog page.

Covers:
- Adding single item to cart and verifying UI button toggle and badge count
- Removing item directly from inventory view and badge decrement
- Adding multiple items to cart
- Data-driven verification of product sorting options (A-Z, Z-A, Price Low-High, Price High-Low)
"""

import pytest
from pages.inventory_page import InventoryPage


@pytest.mark.inventory
@pytest.mark.smoke
def test_add_single_item_updates_cart_badge(logged_in_driver):
    """Verify adding an item increments cart badge to 1 and changes button text to 'Remove'."""
    item_name = "Sauce Labs Backpack"
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.add_item_to_cart_by_name(item_name)

    assert inventory_page.get_cart_badge_count() == 1, "Cart badge count did not update to 1"
    assert inventory_page.get_item_button_text(item_name) == "Remove", "Button text did not change to 'Remove'"


@pytest.mark.inventory
@pytest.mark.regression
def test_remove_item_from_inventory(logged_in_driver):
    """Verify removing an added item removes the cart badge and resets button to 'Add to cart'."""
    item_name = "Sauce Labs Backpack"
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.add_item_to_cart_by_name(item_name)
    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.remove_item_from_inventory_by_name(item_name)

    assert not inventory_page.is_cart_badge_displayed(), "Cart badge should not be displayed after removing the item"
    assert inventory_page.get_item_button_text(item_name) == "Add to cart", "Button text did not reset to 'Add to cart'"


@pytest.mark.inventory
@pytest.mark.regression
def test_add_multiple_items_updates_badge(logged_in_driver):
    """Verify adding multiple distinct items correctly updates the cart badge count."""
    items_to_add = [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
    ]
    inventory_page = InventoryPage(logged_in_driver)

    for item in items_to_add:
        inventory_page.add_item_to_cart_by_name(item)

    assert inventory_page.get_cart_badge_count() == len(items_to_add), (
        f"Expected cart badge count {len(items_to_add)}, but got {inventory_page.get_cart_badge_count()}"
    )


@pytest.mark.inventory
@pytest.mark.regression
@pytest.mark.parametrize(
    "sort_option_value, check_type",
    [
        ("az", "name_asc"),
        ("za", "name_desc"),
        ("lohi", "price_asc"),
        ("hilo", "price_desc"),
    ],
    ids=["sort_name_az", "sort_name_za", "sort_price_low_high", "sort_price_high_low"],
)
def test_sorting_options_parametrized(logged_in_driver, sort_option_value, check_type):
    """Data-driven test verifying all 4 catalog sorting strategies."""
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.select_sort_option(sort_option_value)

    if check_type == "name_asc":
        names = inventory_page.get_all_item_names()
        assert names == sorted(names), "Products were not sorted alphabetically A-Z"
    elif check_type == "name_desc":
        names = inventory_page.get_all_item_names()
        assert names == sorted(names, reverse=True), "Products were not sorted alphabetically Z-A"
    elif check_type == "price_asc":
        prices = inventory_page.get_all_item_prices()
        assert prices == sorted(prices), "Products were not sorted by price ascending (low to high)"
    elif check_type == "price_desc":
        prices = inventory_page.get_all_item_prices()
        assert prices == sorted(prices, reverse=True), "Products were not sorted by price descending (high to low)"
