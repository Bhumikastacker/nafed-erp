# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestProjectExtensionRequest(FrappeTestCase):
# 	pass

# ==================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import add_days, getdate

class TestProjectExtensionRequest(FrappeTestCase):

    def setUp(self):
        """
        Set up dependencies: Approved Project with some progress.
        """
        self.company = "_Test Company"
        random_str = frappe.generate_hash(length=8)
        self.project_name = f"Ext Test Project {random_str}"
        self.div = "Climate Resilient Innovations"

        # Ensure Division exists
        if not frappe.db.exists("Division", self.div):
            frappe.get_doc({"doctype": "Division", "division_name": self.div, "allow_project_creation": 1}).insert()

        # 1. Create Project (Must be Approved, Active, Open and have Progress > 0 as per filters)
        self.project = frappe.get_doc({
            "doctype": "Project",
            "project_name": self.project_name,
            "status": "Open",
            "is_active": "Yes",
            "custom_approval_status": "Approved",
            "expected_start_date": "2026-01-01",
            "expected_end_date": "2026-06-01",
            "estimated_costing": 100000,
            "company": self.company,
            "custom_division": self.div,
            "percent_complete": 10 # Adding progress to satisfy link filter
        }).insert()
        
        # Manual update for percent_complete as it's often read-only/calculated
        frappe.db.set_value("Project", self.project.name, "percent_complete", 10)
        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_extension_request(self):
        """
        CASE 1: Successful creation of Extension Request.
        """
        ext = frappe.get_doc({
            "doctype": "Project Extension Request",
            "project": self.project.name,
            "division": self.div,
            "project_old_end_date": "2026-06-01",
            "project_new_end_date": "2026-08-01",
            "justification": "Delay due to monsoon season.",
            "additional_cost": 5000
        })
        ext.insert()
        
        self.assertTrue(frappe.db.exists("Project Extension Request", ext.name))
        print(f"\n[Positive Test] SUCCESS! Created Extension ID: {ext.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_new_date_before_old_date_gap(self):
        """
        GAP CHECK: Testing if New End Date can be before Old End Date.
        """
        ext = frappe.get_doc({
            "doctype": "Project Extension Request",
            "project": self.project.name,
            "division": self.div,
            "project_old_end_date": "2026-06-01",
            "project_new_end_date": "2026-05-01", # INVALID: Earlier than old date
            "justification": "Invalid date test"
        })

        try:
            ext.insert()
            print(f"\n[GAP FOUND] Extension allowed New Date ({ext.project_new_end_date}) before Old Date!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked extension with earlier date.")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_3_missing_justification_gap(self):
        """
        GAP CHECK: Testing if system blocks request without Justification (reqd: 1).
        """
        ext = frappe.get_doc({
            "doctype": "Project Extension Request",
            "project": self.project.name,
            "division": self.div,
            "project_old_end_date": "2026-06-01",
            "project_new_end_date": "2026-09-01"
            # Justification missing
        })

        try:
            ext.insert()
            print("\n[GAP FOUND] System allowed Extension Request WITHOUT Justification!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked request without justification.")

    def tearDown(self):
        frappe.db.rollback()