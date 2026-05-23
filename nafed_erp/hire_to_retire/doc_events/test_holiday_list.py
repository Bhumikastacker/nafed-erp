import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestHolidayList(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_holiday_list_creation(self):
        """
        CASE 1: Verify that a valid Holiday List can be created with dates and child table entries.
        """
        list_name = "Public Holidays 2026"
        
        # Cleanup to ensure fresh test
        if frappe.db.exists("Holiday List", list_name):
            frappe.delete_doc("Holiday List", list_name)

        holiday_list = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": list_name,
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "holidays": [
                {
                    "holiday_date": "2026-01-26",
                    "description": "Republic Day"
                },
                {
                    "holiday_date": "2026-08-15",
                    "description": "Independence Day"
                }
            ]
        })
        holiday_list.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Holiday List", list_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {holiday_list.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_range_gap(self):
        """
        GAP CHECK: Testing if system allows 'To Date' to be before 'From Date'.
        """
        list_name = "Invalid Period List"
        if frappe.db.exists("Holiday List", list_name):
            frappe.delete_doc("Holiday List", list_name)

        holiday_list = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": list_name,
            "from_date": "2026-12-31",
            "to_date": "2026-01-01" # INVALID: End date is before start date
        })

        try:
            holiday_list.insert()
            print("\n[GAP FOUND] Holiday List allowed invalid date sequence (To Date < From Date)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date sequence.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_holiday_outside_range_gap(self):
        """
        GAP CHECK: Testing if a holiday date can be outside the From/To date range.
        """
        list_name = "Out of Range Test"
        if frappe.db.exists("Holiday List", list_name):
            frappe.delete_doc("Holiday List", list_name)

        holiday_list = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": list_name,
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "holidays": [
                {
                    "holiday_date": "2025-12-25", # INVALID: Date is from previous year
                    "description": "Christmas"
                }
            ]
        })

        try:
            holiday_list.insert()
            print("[GAP FOUND] Holiday List allowed a holiday date outside its defined range!")
        except ValidationError:
            print("[SUCCESS] System blocked holiday date outside range.")

    def tearDown(self):
        """
        Rollback changes to keep the database clean.
        """
        frappe.db.rollback()