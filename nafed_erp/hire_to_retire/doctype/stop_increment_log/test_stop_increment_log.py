# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestStopIncrementLog(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError, MandatoryError

class TestStopIncrementLogGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup test prerequisites: Ensure Company and Employee exist.
        The Employee must be created with all NAFED mandatory custom fields.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "STOP-INC-999"

        # 1. Create Employee with all mandatory fields to avoid Setup Errors
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Stop",
                "last_name": "Tester",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "company": self.company,
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.insert(ignore_permissions=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_no}, "name")

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_stop_log_creation(self):
        """
        CASE 1: Verify successful creation of a Stop Increment Log with valid data.
        """
        doc = frappe.get_doc({
            "doctype": "Stop Increment Log",
            "company": self.company,
            "employee": self.employee,
            "effective_date": today(),
            "increment_year": 2026,
            "increment_month": "July",
            "reason": "Disciplinary action pending final review."
        })
        doc.insert()
        self.assertTrue(frappe.db.exists("Stop Increment Log", doc.name))
        print(f"\n[Positive Test] SUCCESS! Stop Increment Log Created: {doc.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Empty Reason Bypass
    # ---------------------------------------------------------
    def test_gap_1_empty_reason_check(self):
        """
        GAP CHECK: Verify if the system allows saving without a 'Reason'.
        Stopping an increment is a sensitive HR action and must require a justification.
        """
        doc = frappe.get_doc({
            "doctype": "Stop Increment Log",
            "company": self.company,
            "employee": self.employee,
            "effective_date": today(),
            "increment_year": 2026,
            "increment_month": "January",
            "reason": "" # INVALID: Should be mandatory
        })

        try:
            doc.insert()
            # If saved without reason, it's a documentation gap
            if not doc.reason:
                print("\n[GAP FOUND] System allowed stopping an increment without a REASON!")
        except (MandatoryError, ValidationError):
            print("\n[SUCCESS] System correctly blocked record without a Reason.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Future Effective Date Logic
    # ---------------------------------------------------------
    def test_gap_2_future_effective_date(self):
        """
        GAP CHECK: Verify if the system allows an 'Effective Date' in the far future.
        """
        future_date = add_days(today(), 365) # 1 year later
        doc = frappe.get_doc({
            "doctype": "Stop Increment Log",
            "company": self.company,
            "employee": self.employee,
            "effective_date": future_date, # INVALID
            "increment_year": 2026,
            "increment_month": "July",
            "reason": "Future date testing."
        })

        try:
            doc.insert()
            print(f"\n[GAP FOUND] System allowed a FUTURE Effective Date ({future_date})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly restricted future effective dates.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Impossible Increment Year
    # ---------------------------------------------------------
    def test_gap_3_invalid_increment_year(self):
        """
        GAP CHECK: Verify if the system allows an unrealistic 'Increment Year' (e.g., 2099).
        """
        doc = frappe.get_doc({
            "doctype": "Stop Increment Log",
            "company": self.company,
            "employee": self.employee,
            "increment_year": 2099, # INVALID
            "increment_month": "July",
            "reason": "Year limit test."
        })

        try:
            doc.insert()
            print(f"\n[GAP FOUND] System allowed an unrealistic Increment Year ({doc.increment_year})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly validated the year range.")

    def tearDown(self):
        """
        Cleanup database.
        """
        frappe.db.rollback()