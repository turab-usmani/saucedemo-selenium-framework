"""Tests for the multi-step SauceDemo Checkout flow.

Covers:
- End-to-end full checkout from item selection to order completion
- Data-driven field validation on checkout step one (missing first name, last name, postal code)
- Price calculation integrity check (Item total + Tax == Total) on step two
- Cancel button navigation on both Step 1 and Step 2
"""

import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)


@pytest.mark.checkout
@pytest.mark.smoke
def test_e2e_full_checkout_flow(logged_in_driver):
    """Happy path: complete end-to-end purchase flow and verify order confirmation."""
    item_name = "Sauce Labs Backpack"

    # Step 1: Add item and navigate to cart
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.add_item_to_cart_by_name(item_name)
    inventory_page.click_cart()

    # Step 2: Cart to Checkout Step One
    cart_page = CartPage(logged_in_driver)
    cart_page.click_checkout()

    # Step 3: Enter customer info on Step One
    step_one = CheckoutStepOnePage(logged_in_driver)
    assert step_one.is_loaded()
    assert step_one.get_page_title() == "Checkout: Your Information"
    step_one.fill_information(first_name="Jane", last_name="Doe", postal_code="90210")
    step_one.click_continue()

    # Step 4: Verify Step Two Overview
    step_two = CheckoutStepTwoPage(logged_in_driver)
    assert step_two.is_loaded()
    assert step_two.get_page_title() == "Checkout: Overview"
    assert item_name in step_two.get_cart_item_names()
    step_two.click_finish()

    # Step 5: Verify Order Completion
    complete_page = CheckoutCompletePage(logged_in_driver)
    assert complete_page.is_loaded()
    assert complete_page.get_page_title() == "Checkout: Complete!"
    assert complete_page.get_confirmation_header() == "Thank you for your order!"

    # Step 6: Back home navigation
    complete_page.click_back_home()
    inventory_page.wait_for_url_contains("inventory.html")
    assert inventory_page.is_loaded()
    assert "inventory.html" in inventory_page.get_current_url()


@pytest.mark.checkout
@pytest.mark.regression
@pytest.mark.parametrize(
    "first_name, last_name, postal_code, expected_error",
    [
        ("", "Doe", "12345", "Error: First Name is required"),
        ("Jane", "", "12345", "Error: Last Name is required"),
        ("Jane", "Doe", "", "Error: Postal Code is required"),
    ],
    ids=["missing_first_name", "missing_last_name", "missing_postal_code"],
)
def test_checkout_step_one_field_validation_parametrized(
    logged_in_driver, first_name, last_name, postal_code, expected_error
):
    """Data-driven test verifying validation error banners for missing checkout fields."""
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    cart_page.click_checkout()

    step_one = CheckoutStepOnePage(logged_in_driver)
    step_one.fill_information(first_name, last_name, postal_code)
    step_one.click_continue()

    assert step_one.is_error_displayed(), "Expected error message banner was not displayed"
    assert step_one.get_error_message() == expected_error


@pytest.mark.checkout
@pytest.mark.regression
def test_checkout_summary_price_calculations(logged_in_driver):
    """Verify that Subtotal, Tax, and Total calculations match precisely on Checkout Step Two."""
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")    # $29.99
    inventory_page.add_item_to_cart_by_name("Sauce Labs Bike Light")   # $9.99
    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    cart_page.click_checkout()

    step_one = CheckoutStepOnePage(logged_in_driver)
    assert step_one.is_loaded(), "Checkout Step One failed to load"
    step_one.fill_information("Jane", "Doe", "94043")
    step_one.click_continue()

    step_two = CheckoutStepTwoPage(logged_in_driver)
    assert step_two.is_loaded(), "Checkout Step Two failed to load"
    subtotal = step_two.get_item_subtotal()
    tax = step_two.get_tax_amount()
    total = step_two.get_total_amount()

    assert subtotal == 39.98, f"Expected subtotal 39.98, got {subtotal}"
    assert round(subtotal + tax, 2) == round(total, 2), (
        f"Sum of subtotal ({subtotal}) + tax ({tax}) does not equal total ({total})"
    )


@pytest.mark.checkout
@pytest.mark.regression
def test_checkout_cancel_navigation(logged_in_driver):
    """Verify cancel button behaviors on both Step One and Step Two."""
    inventory_page = InventoryPage(logged_in_driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.click_cart()

    cart_page = CartPage(logged_in_driver)
    cart_page.click_checkout()

    # Cancel on Step One returns to Cart
    step_one = CheckoutStepOnePage(logged_in_driver)
    assert step_one.is_loaded(), "Checkout Step One failed to load"
    step_one.click_cancel()
    cart_page.wait_for_url_contains("cart.html")
    assert cart_page.is_loaded(), "Canceling on Step One did not return to Cart"
    assert "cart.html" in cart_page.get_current_url()

    # Re-enter checkout and advance to Step Two
    cart_page.click_checkout()
    assert step_one.is_loaded(), "Checkout Step One failed to load on re-entry"
    step_one.fill_information("Jane", "Doe", "94043")
    step_one.click_continue()

    # Cancel on Step Two returns to Inventory catalog
    step_two = CheckoutStepTwoPage(logged_in_driver)
    assert step_two.is_loaded(), "Failed to load Checkout Step Two before canceling"
    step_two.click_cancel()
    inventory_page.wait_for_url_contains("inventory.html")
    assert inventory_page.is_loaded(), "Canceling on Step Two did not return to Inventory"
    assert "inventory.html" in inventory_page.get_current_url()
