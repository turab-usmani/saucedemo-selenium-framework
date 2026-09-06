# SauceDemo Selenium UI Test Automation Framework

[![UI Automation Tests](https://github.com/username/selenium-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/username/selenium-framework/actions/workflows/tests.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Selenium Version](https://img.shields.io/badge/selenium-4.20%2B-green)
![pytest](https://img.shields.io/badge/pytest-8.0%2B-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A clean, modular UI test automation framework built in Python using **Selenium WebDriver** and **pytest**, targeting the e-commerce demo application [SauceDemo (Swag Labs)](https://www.saucedemo.com/). This repository serves as a portfolio project showcasing modern Software Development Engineer in Test (SDET) best practices: maintainable Page Object Model (POM) architecture, deterministic explicit waits, data-driven test design, automatic failure screenshot capture, HTML test reporting, and automated continuous integration via GitHub Actions.

---

## 🏛️ Architecture & Design Decisions

```
selenium-framework/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI workflow (headless execution & artifacts)
├── config/
│   ├── __init__.py
│   └── config.py              # Centralized environment & app settings (URL, timeouts, accounts)
├── pages/
│   ├── __init__.py            # Clean exports for all page objects
│   ├── base_page.py           # Reusable Selenium interaction wrappers with explicit waits
│   ├── login_page.py          # Login screen locators & actions
│   ├── inventory_page.py      # Product catalog, sorting, and item card actions
│   ├── cart_page.py           # Shopping cart contents and navigation
│   └── checkout_page.py       # Multi-step checkout (Info, Overview, Confirmation)
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Fixtures (browser setup/teardown), CLI options, screenshot hook
│   ├── test_login.py          # Positive, negative, locked-out, and parametrized login tests
│   ├── test_inventory.py      # Catalog item additions, removals, and 4-way sorting tests
│   ├── test_cart.py           # Cart verification, item deletion, and shopping continuation
│   └── test_checkout.py       # E2E purchase flow, input validation, and price calculation checks
├── .env.example               # Template for environment configuration
├── .gitignore                 # Excludes venv, cache, reports, and screenshots
├── pytest.ini                 # Pytest defaults, testpaths, markers, and HTML report flags
├── requirements.txt           # Production test dependencies
└── README.md                  # Comprehensive framework documentation
```

### Why Page Object Model (POM)?
- **Separation of Concerns**: Page objects encapsulate web element locators and UI actions (`click()`, `type_text()`), while test files contain the business workflows and verification assertions.
- **Maintainability**: If a button ID or DOM structure updates on SauceDemo, only the corresponding page object requires maintenance, leaving the test scripts untouched.
- **No Assertions in Page Objects**: Consistent with industry standards, page objects return UI state (strings, lists, counts, or booleans) or perform navigation, giving tests complete ownership over test assertions and error messages.

### Why Explicit Waits (Zero Arbitrary `time.sleep()`)?
- Hardcoded `time.sleep()` statements either waste CPU cycles and prolong build times when conservative, or cause flaky tests when network latency spikes.
- This framework utilizes **`WebDriverWait` combined with `expected_conditions`** encapsulated within `BasePage`. Actions poll the DOM intelligently until elements are clickable, visible, or present, failing fast with descriptive exceptions if a threshold is exceeded.

---

## 🚀 What This Project Demonstrates

| Competency | Implementation in Framework |
|---|---|
| **Page Object Model (POM)** | Modular `BasePage`, `LoginPage`, `InventoryPage`, `CartPage`, `CheckoutStepOnePage`, `CheckoutStepTwoPage`, `CheckoutCompletePage`. |
| **Data-Driven Testing (DDT)** | `@pytest.mark.parametrize` for credential matrices, missing checkout fields, and product sorting algorithms (A-Z, Z-A, Price Low-High, Price High-Low). |
| **Dynamic Wait Strategy** | Dynamic DOM polling via `WebDriverWait` and `expected_conditions` across all actions. No arbitrary `time.sleep()`. |
| **Failure Screenshot Capture** | Pytest hook (`pytest_runtest_makereport`) intercepts test failures, captures browser screenshots into `screenshots/`, and embeds them into the HTML report. |
| **Pre-authenticated Fixtures** | Pytest fixture `logged_in_driver` encapsulates repeated login sequences to keep test suites DRY and focused. |
| **Configurable Execution** | Dynamic switching between Chrome / Edge and Headed / Headless execution via CLI flags or `.env`. |
| **Reporting & CI/CD** | Self-contained HTML reporting via `pytest-html` and automated GitHub Actions workflow archiving reports. |

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.11+** installed
- **Google Chrome** (or Microsoft Edge) installed

### 1. Clone the repository
```bash
git clone https://github.com/username/selenium-framework.git
cd selenium-framework
```

### 2. Create and activate virtual environment
**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Optional) Configure environment variables
Copy `.env.example` to `.env` if you wish to customize defaults:
```bash
cp .env.example .env
```

---

## 🧪 Running Tests Locally

### Run all tests in headless mode (default for CI)
```bash
pytest --headless
```

### Run tests in headed mode (opens visible browser window)
```bash
pytest --headed
```

### Run tests targeting a specific browser (e.g. Edge)
```bash
pytest --browser=edge --headless
```

### Run specific test suites using Pytest Markers
```bash
# Run smoke tests only
pytest -m smoke --headless

# Run regression tests only
pytest -m regression --headless

# Run only login tests
pytest -m login --headless

# Run only checkout tests
pytest -m checkout --headless
```

### Run a specific test file
```bash
pytest tests/test_checkout.py --headless
```

---

## 📊 Viewing Test Reports & Failure Screenshots

After running the tests, an HTML execution report is generated automatically at:
```
reports/report.html
```

### Opening the report
- **Windows**:
  ```powershell
  Start-Process reports/report.html
  ```
- **macOS**:
  ```bash
  open reports/report.html
  ```
- **Linux**:
  ```bash
  xdg-open reports/report.html
  ```

### Failure Screenshot Capture
Whenever an assertion or step fails:
1. A timestamped screenshot is captured automatically in `screenshots/` (e.g., `test_e2e_full_checkout_flow_20260906_120000.png`).
2. The screenshot is embedded directly into `reports/report.html` adjacent to the failed test log for immediate visual debugging.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The repository includes a production-ready CI pipeline configured in `.github/workflows/tests.yml`:
- **Trigger**: Every `push` and `pull_request` targeting the `main` branch.
- **Environment**: Ubuntu Linux with Python 3.11 and headless Google Chrome.
- **Execution**: Runs the entire test suite.
- **Artifacts**: Automatically uploads `reports/` and `screenshots/` with a 14-day retention window, allowing reviewers to inspect test runs directly from GitHub Actions summaries.

---

## 📝 Test Case Coverage Summary

The suite contains **15 test cases** spanning essential user workflows:

1. **Authentication (`test_login.py`)**:
   - `test_successful_login`: Valid credentials redirect to product catalog.
   - `test_locked_out_user_error`: System lock validation message.
   - `test_empty_username_validation`: Blank username error validation.
   - `test_invalid_credentials_parametrized`: Data-driven test covering invalid passwords, non-existent users, and missing passwords.
2. **Product Catalog (`test_inventory.py`)**:
   - `test_add_single_item_updates_cart_badge`: Badge count increments to 1, button text toggles to "Remove".
   - `test_remove_item_from_inventory`: Badge resets and button text returns to "Add to cart".
   - `test_add_multiple_items_updates_badge`: Badge count reflects multi-item selections.
   - `test_sorting_options_parametrized`: Data-driven test validating A-Z, Z-A, Price Low-High, and Price High-Low sorting.
3. **Cart Management (`test_cart.py`)**:
   - `test_items_added_appear_in_cart`: Verification of item names and prices in cart.
   - `test_remove_item_from_cart`: Single item removal and badge update from within cart view.
   - `test_continue_shopping_navigation`: Smooth navigation back to inventory catalog.
4. **Checkout & E2E Purchase (`test_checkout.py`)**:
   - `test_e2e_full_checkout_flow`: Full E2E purchase flow from catalog to "Thank you for your order!" confirmation.
   - `test_checkout_step_one_field_validation_parametrized`: Data-driven test verifying First Name, Last Name, and Postal Code validations.
   - `test_checkout_summary_price_calculations`: Verification of Subtotal, Tax, and Grand Total mathematical accuracy.
   - `test_checkout_cancel_navigation`: Cancellation verification on both Step 1 (returns to cart) and Step 2 (returns to inventory).
