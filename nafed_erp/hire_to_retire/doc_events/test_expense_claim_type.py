import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestExpenseClaimType(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure a Salary Component exists.
        """
        # 1. Create a dummy Salary Component for the mandatory link
        if not frappe.db.exists("Salary Component", "Travel Allowance"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "Travel Allowance",
                "type": "Earning"
            }).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_expense_type_creation(self):
        """
        CASE 1: Verify that a valid Expense Claim Type can be created.
        """
        type_name = "Business Travel Test"
        
        # Cleanup if exists
        if frappe.db.exists("Expense Claim Type", type_name):
            frappe.delete_doc("Expense Claim Type", type_name)

        expense_claim_type = frappe.get_doc({
            "doctype": "Expense Claim Type",
            "expense_type": type_name,              # Mandatory & Unique ID
            "custom_salary_component": "Travel Allowance", # Mandatory Link
            "description": "Verification of travel expenses.",
            "custom_expense_limit": 1,
            "custom_threshold_limit": "5000"
        })
        expense_claim_type.insert()
        
        # Assertion
        self.assertTrue(frappe.db.exists("Expense Claim Type", type_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {expense_claim_type.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_missing_salary_component_gap(self):
        """
        GAP CHECK: Testing if system allows saving without a Salary Component.
        As per JSON, custom_salary_component is mandatory.
        """
        type_name = "Missing Component Test"
        if frappe.db.exists("Expense Claim Type", type_name):
            frappe.delete_doc("Expense Claim Type", type_name)

        expense_claim_type = frappe.get_doc({
            "doctype": "Expense Claim Type",
            "expense_type": type_name,
            "custom_salary_component": "" # INVALID: Missing mandatory link
        })

        try:
            expense_claim_type.insert()
            print("\n[GAP FOUND] Expense Claim Type allowed WITHOUT a Salary Component!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record without Salary Component.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for master data.
        """
        numeric_name = "998877"
        if frappe.db.exists("Expense Claim Type", numeric_name):
            frappe.delete_doc("Expense Claim Type", numeric_name)

        expense_claim_type = frappe.get_doc({
            "doctype": "Expense Claim Type",
            "expense_type": numeric_name,
            "custom_salary_component": "Travel Allowance"
        })

        try:
            expense_claim_type.insert()
            print("[GAP FOUND] Expense Claim Type allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric master data name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()