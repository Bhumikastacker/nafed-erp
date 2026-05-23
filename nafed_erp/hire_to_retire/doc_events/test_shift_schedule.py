import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestShiftSchedule(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure a Shift Type exists.
        """
        self.shift_type = "General Shift Test"
        if not frappe.db.exists("Shift Type", self.shift_type):
            frappe.get_doc({
                "doctype": "Shift Type",
                "name": self.shift_type,
                "start_time": "09:00:00",
                "end_time": "18:00:00"
            }).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_schedule_creation(self):
        """
        CASE 1: Verify that a valid Shift Schedule can be created with manual naming.
        """
        schedule_name = "Weekly Roster A"
        if frappe.db.exists("Shift Schedule", schedule_name):
            frappe.delete_doc("Shift Schedule", schedule_name)

        schedule = frappe.get_doc({
            "doctype": "Shift Schedule",
            "name": schedule_name,          # Prompt naming
            "shift_type": self.shift_type,  # Mandatory Link
            "frequency": "Every Week",      # Mandatory Select
            "repeat_on_days": [             # Mandatory Child Table
                {"day": "Monday"},
                {"day": "Tuesday"},
                {"day": "Wednesday"}
            ]
        })
        schedule.insert()
        self.assertTrue(frappe.db.exists("Shift Schedule", schedule_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {schedule.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_repeat_days_gap(self):
        """
        GAP CHECK: Testing if system allows saving a schedule without any 'Repeat On Days'.
        JSON says 'reqd: 1' for this table.
        """
        schedule_name = "Empty Schedule Gap Test"
        if frappe.db.exists("Shift Schedule", schedule_name):
            frappe.delete_doc("Shift Schedule", schedule_name)

        schedule = frappe.get_doc({
            "doctype": "Shift Schedule",
            "name": schedule_name,
            "shift_type": self.shift_type,
            "frequency": "Every Week",
            "repeat_on_days": [] # INVALID: Empty child table
        })

        try:
            schedule.insert()
            print("\n[GAP FOUND] Shift Schedule allowed creation WITHOUT any Repeat Days!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked schedule without repeat days.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for schedules.
        """
        numeric_name = "123123"
        if frappe.db.exists("Shift Schedule", numeric_name):
            frappe.delete_doc("Shift Schedule", numeric_name)

        schedule = frappe.get_doc({
            "doctype": "Shift Schedule",
            "name": numeric_name,
            "shift_type": self.shift_type,
            "frequency": "Every Week",
            "repeat_on_days": [{"day": "Monday"}]
        })

        try:
            schedule.insert()
            print("[GAP FOUND] Shift Schedule allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric schedule name.")

    def tearDown(self):
        frappe.db.rollback()