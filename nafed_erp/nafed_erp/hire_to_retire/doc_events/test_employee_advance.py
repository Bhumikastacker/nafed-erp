import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestEmployeeAdvance(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure an active Employee exists.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Create a dummy Employee for advance testing
        if not frappe.db.exists("Employee", {"first_name": "AdvanceUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-ADV-101",
                "first_name": "AdvanceUser",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "AdvanceUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_advance_creation(self):
        """
        CASE 1: Verify that a valid Employee Advance can be created.
        """
        advance = frappe.get_doc({
            "doctype": "Employee Advance",
            "naming_series": "HR-EAD-.YYYY.-", # Mandatory Series
            "employee": self.test_employee,      # Mandatory Link
            "posting_date": today(),             # Mandatory Date
            "company": self.company,             # Mandatory Link
            "purpose": "Official Trip to Mumbai", # Mandatory Text
            "advance_amount": 5000,              # Mandatory Currency
            "currency": "INR",                   # Mandatory Link
            "exchange_rate": 1.0                 # Mandatory Float
        })
        advance.insert()
        self.assertTrue(frappe.db.exists("Employee Advance", advance.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {advance.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_advance_amount_gap(self):
        """
        GAP CHECK: Testing if system allows a NEGATIVE advance amount.
        Logically, an advance payment cannot be negative.
        """
        advance = frappe.get_doc({
            "doctype": "Employee Advance",
            "employee": self.test_employee,
            "posting_date": today(),
            "company": self.company,
            "purpose": "Negative Amount Gap Test",
            "advance_amount": -1000, # INVALID DATA
            "currency": "INR",
            "exchange_rate": 1.0
        })

        try:
            advance.insert()
            print("\n[GAP FOUND] Employee Advance allowed NEGATIVE Advance Amount!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative advance amount.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_zero_advance_amount_gap(self):
        """
        GAP CHECK: Testing if system allows an advance amount of ZERO.
        """
        advance = frappe.get_doc({
            "doctype": "Employee Advance",
            "employee": self.test_employee,
            "posting_date": today(),
            "company": self.company,
            "purpose": "Zero Amount Gap Test",
            "advance_amount": 0, # INVALID DATA
            "currency": "INR",
            "exchange_rate": 1.0
        })

        try:
            advance.insert()
            print("[GAP FOUND] Employee Advance allowed ZERO Advance Amount!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked zero advance amount.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()