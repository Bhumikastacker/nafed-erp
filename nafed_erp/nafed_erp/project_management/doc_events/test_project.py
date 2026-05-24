import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import add_days, getdate

class TestProject(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Company and basic data.
        """
        self.company = "_Test Company" 
        if not frappe.db.exists("Company", self.company):
            frappe.get_doc({
                "doctype": "Company",
                "company_name": self.company,
                "default_currency": "INR"
            }).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_project_creation(self):
        """
        CASE 1: Verify successful creation of a valid Project.
        """
        project_name = "Unit Test Project 2026"
        
        # Cleanup existing to avoid unique constraint error
        if frappe.db.exists("Project", {"project_name": project_name}):
            frappe.delete_doc("Project", frappe.get_value("Project", {"project_name": project_name}, "name"))

        project = frappe.get_doc({
            "doctype": "Project",
            "naming_series": "PROJ-.####",
            "project_name": project_name,
            "status": "Open",
            "expected_start_date": "2026-01-01",
            "expected_end_date": "2026-12-31",
            "estimated_costing": 100000,
            "company": self.company,
            "is_active": "Yes"
        })
        project.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Project", project.name))
        print(f"\n[Positive Test] SUCCESS! Created Project ID: {project.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_invalid_date_range_gap(self):
        """
        GAP CHECK: Testing if system allows End Date before Start Date.
        Logic: Expected End Date should not be earlier than Expected Start Date.
        """
        project_name = "Invalid Date Project"
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": project_name,
            "expected_start_date": "2026-12-31",
            "expected_end_date": "2026-01-01", # INVALID: End before Start
            "estimated_costing": 50000,
            "company": self.company
        })

        try:
            project.insert()
            # Agar save ho gaya matlab GAP hai (bug hai)
            print(f"\n[GAP FOUND] Project allowed End Date ({project.expected_end_date}) before Start Date!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked invalid date range.")

    # ------------------------
    # Negative Test Case (Mandatory Check)
    # ------------------------
    def test_3_missing_mandatory_costing_gap(self):
        """
        GAP CHECK: Testing if system allows creation without Estimated Costing.
        As per your JSON, estimated_costing is reqd: 1.
        """
        project_name = "Missing Cost Project"
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": project_name,
            "expected_start_date": "2026-01-01",
            "expected_end_date": "2026-02-01",
            "company": self.company
            # Missing estimated_costing
        })

        try:
            project.insert()
            print("\n[GAP FOUND] Project allowed creation WITHOUT Estimated Costing!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked Project without mandatory costing.")

    def tearDown(self):
        """
        Rollback changes to keep DB clean.
        """
        frappe.db.rollback()