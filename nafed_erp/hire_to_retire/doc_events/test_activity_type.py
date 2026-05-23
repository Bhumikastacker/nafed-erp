import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestActivityType(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_activity_creation(self):
        """
        CASE 1: Verify that a valid Activity Type can be created.
        """
        activity_name = "System Development Test"
        
        # Cleanup if exists to ensure a fresh test
        if frappe.db.exists("Activity Type", activity_name):
            frappe.delete_doc("Activity Type", activity_name)

        activity = frappe.get_doc({
            "doctype": "Activity Type",
            "activity_type": activity_name, # Mandatory field (acts as ID)
            "costing_rate": 500,
            "billing_rate": 1000,
            "disabled": 0
        })
        activity.insert()
        
        # Assertion: Check if record exists in database
        self.assertTrue(frappe.db.exists("Activity Type", activity_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {activity.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_numeric_name_gap(self):
        """
        GAP CHECK: Testing if system allows purely numeric names for master data.
        """
        numeric_name = "12345" # INVALID DATA for an activity
        
        if frappe.db.exists("Activity Type", numeric_name):
            frappe.delete_doc("Activity Type", numeric_name)

        activity = frappe.get_doc({
            "doctype": "Activity Type",
            "activity_type": numeric_name
        })

        try:
            activity.insert()
            print("\n[GAP FOUND] Activity Type allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric master data name.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_negative_rates_gap(self):
        """
        GAP CHECK: Testing if system allows negative costing or billing rates.
        Rates should ideally be positive currency values.
        """
        activity_name = "Negative Rate Test"
        if frappe.db.exists("Activity Type", activity_name):
            frappe.delete_doc("Activity Type", activity_name)

        activity = frappe.get_doc({
            "doctype": "Activity Type",
            "activity_type": activity_name,
            "costing_rate": -100, # INVALID DATA
            "billing_rate": -200  # INVALID DATA
        })

        try:
            activity.insert()
            print("[GAP FOUND] Activity Type allowed NEGATIVE Costing/Billing Rates!")
        except ValidationError:
            print("[SUCCESS] System blocked negative currency values.")

    def tearDown(self):
        """
        Rollback changes after the test.
        """
        frappe.db.rollback()