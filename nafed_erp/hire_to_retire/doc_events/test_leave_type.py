import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLeaveType(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_leave_type_creation(self):
        """
        CASE 1: Verify successful creation of a valid Leave Type.
        """
        leave_name = "Privilege Leave Test"
        
        # Cleanup existing to avoid unique constraint error
        if frappe.db.exists("Leave Type", leave_name):
            frappe.delete_doc("Leave Type", leave_name)

        leave_type = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": leave_name,
            "max_leaves_allowed": 30,
            "is_carry_forward": 1,
            "expire_carry_forwarded_leaves_after_days": 365,
            "is_earned_leave": 1,
            "earned_leave_frequency": "Monthly"
        })
        leave_type.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Leave Type", leave_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {leave_type.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_numeric_name_gap(self):
        """
        GAP CHECK: Testing if system allows purely numeric names for master data.
        """
        numeric_name = "7777"
        if frappe.db.exists("Leave Type", numeric_name):
            frappe.delete_doc("Leave Type", numeric_name)

        leave_type = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": numeric_name
        })

        try:
            leave_type.insert()
            print("\n[GAP FOUND] Leave Type allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric master data name.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_negative_max_leaves_gap(self):
        """
        GAP CHECK: Testing if system allows negative values in 'Max Leaves Allowed'.
        """
        leave_name = "Negative Max Leaves Test"
        if frappe.db.exists("Leave Type", leave_name):
            frappe.delete_doc("Leave Type", leave_name)

        leave_type = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": leave_name,
            "max_leaves_allowed": -10 # INVALID DATA
        })

        try:
            leave_type.insert()
            print("[GAP FOUND] Leave Type allowed NEGATIVE Max Leaves Allowed!")
        except ValidationError:
            print("[SUCCESS] System blocked negative leave count.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_4_negative_applicable_after_gap(self):
        """
        GAP CHECK: Testing if system allows negative days in 'Applicable After'.
        """
        leave_name = "Negative Days Test"
        if frappe.db.exists("Leave Type", leave_name):
            frappe.delete_doc("Leave Type", leave_name)

        leave_type = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": leave_name,
            "applicable_after": -5 # INVALID DATA
        })

        try:
            leave_type.insert()
            print("[GAP FOUND] Leave Type allowed NEGATIVE 'Applicable After' days!")
        except ValidationError:
            print("[SUCCESS] System blocked negative working days.")

    def tearDown(self):
        """
        Rollback changes to maintain data integrity.
        """
        frappe.db.rollback()