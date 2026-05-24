import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEmployeeOnboardingTemplate(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for testing.
        Ensuring Designation, Grade, and ROLES exist.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure Designation exists
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()
        
        # 2. Ensure Grade exists
        if not frappe.db.exists("Employee Grade", "Grade A"):
            frappe.get_doc({"doctype": "Employee Grade", "name": "Grade A"}).insert()

        # 3. Ensure the Role 'IT Manager' exists (The Fix for LinkValidationError)
        if not frappe.db.exists("Role", "IT Manager"):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": "IT Manager"
            }).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_template_creation(self):
        """
        CASE 1: Verify that a valid Onboarding Template can be created 
        with all required fields and activities.
        """
        template = frappe.get_doc({
            "doctype": "Employee Onboarding Template",
            "title": "Professional IT Onboarding",
            "company": self.company,
            "designation": "Software Engineer",
            "employee_grade": "Grade A",
            "activities": [
                {
                    "activity_name": "Issue Laptop & ID Card",
                    "role": "IT Manager" # Role now exists in setUp
                }
            ]
        })
        template.insert()
        # frappe.db.commit()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Employee Onboarding Template", template.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {template.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_activities_gap(self):
        """
        GAP CHECK: Testing if system allows saving a template without any activities.
        A template without tasks should ideally be blocked.
        """
        template = frappe.get_doc({
            "doctype": "Employee Onboarding Template",
            "title": "Invalid Empty Template",
            "company": self.company,
            "activities": [] # INVALID: Empty child table
        })

        try:
            template.insert()
            print("\n[GAP FOUND] System allowed Onboarding Template WITHOUT any activities!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked template without activities.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_duplicate_title_gap(self):
        """
        GAP CHECK: Testing if system allows multiple templates with the same Title.
        """
        duplicate_title = "Onboarding Plan V1"
        
        # Step 1: Create the first template
        frappe.get_doc({
            "doctype": "Employee Onboarding Template",
            "title": duplicate_title,
            "company": self.company
        }).insert()

        # Step 2: Attempt to create another template with the SAME title
        duplicate_doc = frappe.get_doc({
            "doctype": "Employee Onboarding Template",
            "title": duplicate_title,
            "company": self.company
        })

        try:
            duplicate_doc.insert()
            print("[GAP FOUND] System allowed DUPLICATE titles for Onboarding Templates!")
        except (ValidationError, frappe.DuplicateEntryError):
            print("[SUCCESS] System blocked duplicate titles.")

    def tearDown(self):
        """
        Rollback changes to maintain a clean database.
        """
        frappe.db.rollback()
        # pass