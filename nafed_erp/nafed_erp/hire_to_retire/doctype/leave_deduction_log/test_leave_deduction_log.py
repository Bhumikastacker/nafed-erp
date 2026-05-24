# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# # import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLeaveDeductionLog(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, today
from frappe import ValidationError

class TestLeaveDeductionLog(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee and Leave Type.
        """
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Casual Leave"

        # 1. Ensure Leave Type exists
        if not frappe.db.exists("Leave Type", self.leave_type):
            frappe.get_doc({"doctype": "Leave Type", "leave_type_name": self.leave_type}).insert()

        # 2. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "DeductUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-DED-001",
                "first_name": "DeductUser",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "DeductUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_deduction_log_creation(self):
        """
        CASE 1: Verify successful creation of a valid Leave Deduction Log.
        """
        log = frappe.get_doc({
            "doctype": "Leave Deduction Log",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "rule": "Late Entry Rule",             # Mandatory Data
            "date": today(),                       # Mandatory Date
            "company": self.company,               # Mandatory Link
            "deduction_unit": 0.5,                 # Mandatory Float
            "reference_doctype": "Employee",       # Mandatory Link
            "reference_name": self.test_employee   # Mandatory Dynamic Link
        })
        log.insert()
        self.assertTrue(frappe.db.exists("Leave Deduction Log", log.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {log.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_deduction_unit_gap(self):
        """
        GAP CHECK: Testing if system allows negative deduction units.
        Deduction should always be a positive number.
        """
        log = frappe.get_doc({
            "doctype": "Leave Deduction Log",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "rule": "Late Entry Rule",
            "date": today(),
            "company": self.company,
            "deduction_unit": -1.0, # INVALID DATA
            "reference_doctype": "Employee",
            "reference_name": self.test_employee
        })

        try:
            log.insert()
            print("\n[GAP FOUND] Leave Deduction Log allowed NEGATIVE Deduction Unit!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative deduction unit.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_future_date_gap(self):
        """
        GAP CHECK: Testing if system allows future dates for a deduction log.
        A log is usually created for a past event.
        """
        future_date = add_days(today(), 30)
        log = frappe.get_doc({
            "doctype": "Leave Deduction Log",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "rule": "Late Entry Rule",
            "date": future_date, # INVALID: Future date
            "company": self.company,
            "deduction_unit": 0.5,
            "reference_doctype": "Employee",
            "reference_name": self.test_employee
        })

        try:
            log.insert()
            print("[GAP FOUND] Leave Deduction Log allowed FUTURE Date!")
        except ValidationError:
            print("[SUCCESS] System blocked future date for deduction log.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()