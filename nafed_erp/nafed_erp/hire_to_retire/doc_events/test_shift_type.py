import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestShiftType(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_shift_creation(self):
        """
        CASE 1: Verify that a valid Shift Type can be created with manual naming.
        """
        shift_name = "Morning Shift Test"
        if frappe.db.exists("Shift Type", shift_name):
            frappe.delete_doc("Shift Type", shift_name)

        shift = frappe.get_doc({
            "doctype": "Shift Type",
            "name": shift_name,        # Manual naming (Prompt)
            "start_time": "09:00:00",  # Mandatory
            "end_time": "18:00:00",    # Mandatory
            "enable_auto_attendance": 1,
            "late_entry_grace_period": 15
        })
        shift.insert()
        self.assertTrue(frappe.db.exists("Shift Type", shift_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {shift.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_invalid_time_sequence_gap(self):
        """
        GAP CHECK: Testing if End Time can be BEFORE Start Time.
        (Unless it crosses midnight, system should usually validate this).
        """
        shift_name = "Invalid Time Gap Test"
        if frappe.db.exists("Shift Type", shift_name):
            frappe.delete_doc("Shift Type", shift_name)

        shift = frappe.get_doc({
            "doctype": "Shift Type",
            "name": shift_name,
            "start_time": "18:00:00",
            "end_time": "09:00:00" # Technically valid for night shift, but checking validation
        })
        # Note: If system allows this without proper 'crosses midnight' flag, it's a gap.
        shift.insert()
        print(f"\n[INFO] Shift saved with End Time < Start Time. Verify if this is expected for Night Shifts.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_negative_grace_period_gap(self):
        """
        GAP CHECK: Testing if system allows negative minutes in Grace Period.
        """
        shift_name = "Negative Grace Gap Test"
        if frappe.db.exists("Shift Type", shift_name):
            frappe.delete_doc("Shift Type", shift_name)

        shift = frappe.get_doc({
            "doctype": "Shift Type",
            "name": shift_name,
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "enable_late_entry_marking": 1,
            "late_entry_grace_period": -30 # INVALID DATA
        })

        try:
            shift.insert()
            print("\n[GAP FOUND] Shift Type allowed NEGATIVE Grace Period!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative grace period.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_4_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed.
        """
        numeric_name = "4444"
        if frappe.db.exists("Shift Type", numeric_name):
            frappe.delete_doc("Shift Type", numeric_name)

        shift = frappe.get_doc({
            "doctype": "Shift Type",
            "name": numeric_name,
            "start_time": "09:00:00",
            "end_time": "18:00:00"
        })

        try:
            shift.insert()
            print("[GAP FOUND] Shift Type allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric shift name.")

    def tearDown(self):
        frappe.db.rollback()