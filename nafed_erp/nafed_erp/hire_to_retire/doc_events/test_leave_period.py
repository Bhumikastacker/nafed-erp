import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLeavePeriod(FrappeTestCase):

    def setUp(self):
        self.company = "_Test Indian Registered Company"

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_leave_period_creation(self):
        """Verify standard creation."""
        leave_period = frappe.get_doc({
            "doctype": "Leave Period",
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "company": self.company,
            "is_active": 1
        })
        leave_period.insert()
        self.assertTrue(frappe.db.exists("Leave Period", leave_period.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {leave_period.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_order_gap(self):
        """GAP CHECK: To Date < From Date."""
        leave_period = frappe.get_doc({
            "doctype": "Leave Period",
            "from_date": "2026-12-31",
            "to_date": "2026-01-01",
            "company": self.company
        })
        try:
            leave_period.insert()
            print("\n[GAP FOUND] Leave Period allowed invalid date sequence!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_overlapping_period_gap(self):
        """GAP CHECK: Overlapping periods."""
        frappe.get_doc({
            "doctype": "Leave Period",
            "from_date": "2027-01-01",
            "to_date": "2027-12-31",
            "company": self.company
        }).insert()

        duplicate = frappe.get_doc({
            "doctype": "Leave Period",
            "from_date": "2027-06-01", 
            "to_date": "2027-12-31",
            "company": self.company
        })
        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed OVERLAPPING Leave Periods!")
        except ValidationError:
            print("[SUCCESS] System blocked overlapping leave periods.")

    def tearDown(self):
        frappe.db.rollback()