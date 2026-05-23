import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestBranchPaymentRequest(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Branch Payment Request.
        """
        self.head_office = "_Test Indian Registered Company"
        self.branch_name = "_Test Branch Company"
        
        # 1. Ensure a separate Branch Company exists to satisfy the "Cannot be same" validation
        if not frappe.db.exists("Company", self.branch_name):
            frappe.get_doc({
                "doctype": "Company", 
                "company_name": self.branch_name,
                "default_currency": "INR",
                "country": "India"
            }).insert(ignore_permissions=True)

        # 2. Ensure Division exists (Keeping the typo fix 'divsion_name' from previous run)
        if not frappe.db.exists("Division", "Finance"):
            frappe.get_doc({
                "doctype": "Division", 
                "divsion_name": "Finance" 
            }).insert(ignore_permissions=True)

        # 3. Ensure Mode of Payment exists
        if not frappe.db.exists("Mode of Payment", "Cash"):
            frappe.get_doc({
                "doctype": "Mode of Payment", 
                "mode_of_payment": "Cash"
            }).insert()

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_request_creation(self):
        """
        CASE 1: Verify successful creation when Head Office and Branch are DIFFERENT.
        """
        request = frappe.get_doc({
            "doctype": "Branch Payment Request",
            "naming_series": "ACC-PRB-.YYYY.-",
            "division": "Finance",
            "head_office": self.head_office,
            "branch": self.branch_name, # DIFFERENT FROM HEAD OFFICE
            "payment_request_type": "Outward",
            "transaction_date": today(),
            "mode_of_payment": "Cash",
            "transcation_type": "Approval Requisition",
            "grand_total": 5000,
            "email_to": "finance.test@example.com"
        })
        request.insert()
        self.assertTrue(frappe.db.exists("Branch Payment Request", request.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {request.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_negative_amount_gap(self):
        """
        GAP CHECK: Testing if system allows negative payment amounts.
        """
        request = frappe.get_doc({
            "doctype": "Branch Payment Request",
            "naming_series": "ACC-PRB-.YYYY.-",
            "division": "Finance",
            "head_office": self.head_office,
            "branch": self.branch_name,
            "transaction_date": today(),
            "mode_of_payment": "Cash",
            "transcation_type": "Approval Requisition",
            "grand_total": -1000, # INVALID DATA
            "email_to": "gap.test@example.com"
        })

        # This test ensures the system HAS a validation for negative amounts.
        # If the insert succeeds without error, the test fails (indicating a security GAP).
        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed NEGATIVE amount!"):
            request.insert()

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_3_future_date_gap(self):
        """
        GAP CHECK: Testing if system allows future transaction dates.
        """
        future_date = add_days(today(), 30)
        request = frappe.get_doc({
            "doctype": "Branch Payment Request",
            "naming_series": "ACC-PRB-.YYYY.-",
            "division": "Finance",
            "head_office": self.head_office,
            "branch": self.branch_name,
            "transaction_date": future_date, # INVALID: Future Date
            "mode_of_payment": "Cash",
            "transcation_type": "Approval Requisition",
            "grand_total": 2000,
            "email_to": "future.test@example.com"
        })

        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed FUTURE transaction date!"):
            request.insert()

    def tearDown(self):
        """
        Rollback database changes.
        """
        frappe.db.rollback()