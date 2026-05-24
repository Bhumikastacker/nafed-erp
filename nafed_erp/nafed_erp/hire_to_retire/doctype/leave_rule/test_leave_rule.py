# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# # import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLeaveRule(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLeaveRule(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Company, Leave Type, and Shift Type.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure Leave Type exists
        if not frappe.db.exists("Leave Type", "Casual Leave"):
            frappe.get_doc({"doctype": "Leave Type", "leave_type_name": "Casual Leave"}).insert()
        
        # 2. Ensure Shift Type exists for the rule
        if not frappe.db.exists("Shift Type", "Day Shift"):
            frappe.get_doc({"doctype": "Shift Type", "name": "Day Shift"}).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_leave_rule_creation(self):
        """
        CASE 1: Verify that a valid Leave Rule can be created.
        """
        # Cleanup to avoid naming conflict
        frappe.db.delete("Leave Rule", {"company": self.company, "rule_type": "Uncompensated Late Entry Count"})

        leave_rule = frappe.get_doc({
            "doctype": "Leave Rule",
            "enable": 1,
            "company": self.company,
            "rule_name": "Late Entry Rule 2026",
            "rule_type": "Uncompensated Late Entry Count",
            "deduction_unit": "0.5",
            "violations": 3,
            "leave_type": "Casual Leave",
            "shift_type": "Day Shift"
        })
        leave_rule.insert()
        self.assertTrue(frappe.db.exists("Leave Rule", leave_rule.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {leave_rule.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_violations_gap(self):
        """
        GAP CHECK: Testing if system allows negative number of violations.
        """
        leave_rule = frappe.get_doc({
            "doctype": "Leave Rule",
            "company": self.company,
            "rule_name": "Negative Violation Test",
            "rule_type": "Uncompensated Late Entry Count",
            "deduction_unit": "1",
            "violations": -5 # INVALID DATA
        })

        try:
            # We use ignore_if_duplicate to focus on math logic
            leave_rule.insert(ignore_if_duplicate=True)
            print("\n[GAP FOUND] Leave Rule allowed NEGATIVE Violations!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative violations.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_rule_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric rule names are allowed.
        """
        leave_rule = frappe.get_doc({
            "doctype": "Leave Rule",
            "company": self.company,
            "rule_name": "123456", # INVALID DATA
            "rule_type": "Uncompensated Late Entry Count",
            "deduction_unit": "1",
            "violations": 3
        })

        try:
            leave_rule.insert(ignore_if_duplicate=True)
            print("[GAP FOUND] Leave Rule allowed PURELY NUMERIC rule name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric rule name.")

    def tearDown(self):
        """
        Rollback changes after the test.
        """
        frappe.db.rollback()
