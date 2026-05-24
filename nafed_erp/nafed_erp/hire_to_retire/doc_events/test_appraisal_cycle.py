import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestAppraisalCycle(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure Company exists.
        """
        self.company = "_Test Indian Registered Company"

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_cycle_creation(self):
        """
        CASE 1: Verify that a valid Appraisal Cycle can be created.
        """
        cycle_name = "Annual Performance Review 2026"
        
        # Cleanup to ensure a clean test
        if frappe.db.exists("Appraisal Cycle", cycle_name):
            frappe.delete_doc("Appraisal Cycle", cycle_name)

        cycle = frappe.get_doc({
            "doctype": "Appraisal Cycle",
            "cycle_name": cycle_name,      # Mandatory & Unique
            "company": self.company,       # Mandatory
            "start_date": "2026-01-01",    # Mandatory
            "end_date": "2026-12-31",      # Mandatory
            "kra_evaluation_method": "Automated Based on Goal Progress"
        })
        cycle.insert()
        
        self.assertTrue(frappe.db.exists("Appraisal Cycle", cycle_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {cycle.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_order_gap(self):
        """
        GAP CHECK: Testing if system allows 'End Date' before 'Start Date'.
        """
        cycle_name = "Invalid Date Cycle"
        if frappe.db.exists("Appraisal Cycle", cycle_name):
            frappe.delete_doc("Appraisal Cycle", cycle_name)

        cycle = frappe.get_doc({
            "doctype": "Appraisal Cycle",
            "cycle_name": cycle_name,
            "company": self.company,
            "start_date": "2026-12-31",
            "end_date": "2026-01-01" # INVALID: End date is earlier
        })

        try:
            cycle.insert()
            print("\n[GAP FOUND] Appraisal Cycle allowed invalid date sequence (End < Start)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric cycle names are allowed.
        """
        numeric_name = "99999"
        if frappe.db.exists("Appraisal Cycle", numeric_name):
            frappe.delete_doc("Appraisal Cycle", numeric_name)

        cycle = frappe.get_doc({
            "doctype": "Appraisal Cycle",
            "cycle_name": numeric_name,
            "company": self.company,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        })

        try:
            cycle.insert()
            print("[GAP FOUND] Appraisal Cycle allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric cycle name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()