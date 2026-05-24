import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestBudgetGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure Company, Fiscal Year, Cost Center, and Accounts exist.
        """
        self.company = "_Test Indian Registered Company"
        self.fiscal_year = "2024-2025" # Ensure this exists in your system
        
        # 1. Ensure Fiscal Year exists
        if not frappe.db.exists("Fiscal Year", self.fiscal_year):
            frappe.get_doc({
                "doctype": "Fiscal Year",
                "year": self.fiscal_year,
                "year_start_date": "2024-04-01",
                "year_end_date": "2025-03-31"
            }).insert(ignore_permissions=True)

        # 2. Get a valid Cost Center for the company
        self.cost_center = frappe.db.get_value("Cost Center", {"company": self.company, "is_group": 0}, "name")
        
        # 3. Get an Expense Account for the budget table
        self.account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Expense", "is_group": 0}, "name")

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_budget_creation(self):
        """
        CASE 1: Verify successful creation of a Budget for a Cost Center.
        """
        budget = frappe.get_doc({
            "doctype": "Budget",
            "naming_series": "BUDGET-.YYYY.-",
            "budget_against": "Cost Center",
            "company": self.company,
            "cost_center": self.cost_center,
            "fiscal_year": self.fiscal_year,
            "accounts": [
                {
                    "account": self.account,
                    "budget_amount": 50000
                }
            ]
        })
        budget.insert()
        self.assertTrue(frappe.db.exists("Budget", budget.name))
        print(f"\n[Positive Test] SUCCESS! Budget {budget.name} created for {self.cost_center}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Negative Budget Amount
    # ---------------------------------------------------------
    def test_gap_1_negative_budget_amount(self):
        """
        GAP CHECK: Does the system allow a negative value in the Budget Amount field?
        Logically, a budget allocation cannot be negative.
        """
        budget = frappe.get_doc({
            "doctype": "Budget",
            "budget_against": "Cost Center",
            "company": self.company,
            "cost_center": self.cost_center,
            "fiscal_year": self.fiscal_year,
            "accounts": [
                {
                    "account": self.account,
                    "budget_amount": -10000 # INVALID DATA
                }
            ]
        })

        try:
            budget.insert()
            # If saved, it is a financial gap
            print("\n[GAP FOUND] System allowed a NEGATIVE Budget Amount!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative budget amount.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Duplicate Budget for Same Entity
    # ---------------------------------------------------------
    def test_gap_2_duplicate_budget_integrity(self):
        """
        GAP CHECK: Can we create two separate budgets for the SAME Cost Center 
        and SAME Fiscal Year? This leads to limit bypasses and confusion.
        """
        # Create first budget
        self.test_1_positive_budget_creation()

        # Try to create a second budget for the same setup
        duplicate = frappe.get_doc({
            "doctype": "Budget",
            "budget_against": "Cost Center",
            "company": self.company,
            "cost_center": self.cost_center,
            "fiscal_year": self.fiscal_year,
            "accounts": [{"account": self.account, "budget_amount": 20000}]
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE budgets for the same Cost Center and Fiscal Year!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate budget entries.")

    def tearDown(self):
        """
        Rollback database changes.
        """
        frappe.db.rollback()