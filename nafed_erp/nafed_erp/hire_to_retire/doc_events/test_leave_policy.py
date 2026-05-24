import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLeavePolicy(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure a Leave Type exists for the policy details.
        """
        if not frappe.db.exists("Leave Type", "Sick Leave"):
            frappe.get_doc({"doctype": "Leave Type", "leave_type_name": "Sick Leave"}).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_policy_creation(self):
        """
        Verify that a valid Leave Policy can be created with mandatory fields.
        """
        policy = frappe.get_doc({
            "doctype": "Leave Policy",
            "title": "Standard HR Policy 2026",
            "leave_policy_details": [
                {
                    "leave_type": "Sick Leave",
                    "annual_allocation": 12
                }
            ]
        })
        policy.insert()
        self.assertTrue(frappe.db.exists("Leave Policy", policy.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {policy.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_details_gap(self):
        """
        GAP CHECK: Testing if system allows saving a policy without any leave details.
        As per JSON, leave_policy_details is mandatory.
        """
        policy = frappe.get_doc({
            "doctype": "Leave Policy",
            "title": "Empty Policy Gap Test",
            "leave_policy_details": [] # INVALID: Empty child table
        })

        try:
            policy.insert()
            print("\n[GAP FOUND] Leave Policy allowed creation WITHOUT any details!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked policy without details.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_negative_allocation_gap(self):
        """
        GAP CHECK: Testing if system allows negative leave allocation in policy details.
        """
        policy = frappe.get_doc({
            "doctype": "Leave Policy",
            "title": "Negative Allocation Gap Test",
            "leave_policy_details": [
                {
                    "leave_type": "Sick Leave",
                    "annual_allocation": -5 # INVALID DATA
                }
            ]
        })

        try:
            policy.insert()
            print("[GAP FOUND] Leave Policy allowed NEGATIVE annual allocation!")
        except ValidationError:
            print("[SUCCESS] System blocked negative allocation.")

    def tearDown(self):
        """
        Rollback changes after the test.
        """
        frappe.db.rollback()