"""Page Object Model (POM) package for SauceDemo test automation."""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)

__all__ = [
    "BasePage",
    "LoginPage",
    "InventoryPage",
    "CartPage",
    "CheckoutStepOnePage",
    "CheckoutStepTwoPage",
    "CheckoutCompletePage",
]
