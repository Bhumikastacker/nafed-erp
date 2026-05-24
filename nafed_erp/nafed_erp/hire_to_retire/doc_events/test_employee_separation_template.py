import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, MandatoryError

class TestEmployeeSeparationTemplate(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Activity Type ka field name fix kiya gaya hai.
        """
        self.company = "_Test Indian Registered Company"
        self.template_title = "Standard Exit Process"
        
        # 1. Ensure Activity Type exists 
        # NOTE: Field name badal kar 'activity_type' kar diya gaya hai (Label: Activity Type)
        if not frappe.db.exists("Activity Type", "Asset Handover"):
            frappe.get_doc({
                "doctype": "Activity Type",
                "activity_type": "Asset Handover" 
            }).insert(ignore_permissions=True)

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_template_creation(self):
        """
        CASE 1: Verify successful creation of a template with activities.
        """
        template = frappe.get_doc({
            "doctype": "Employee Separation Template",
            "title": self.template_title,
            "company": self.company,
            "activities": [
                {
                    "activity_name": "Asset Handover", # Child table field
                    "role": "HR Manager"
                }
            ]
        })
        template.insert()
        self.assertTrue(frappe.db.exists("Employee Separation Template", template.name))
        print(f"\n[Positive Test] SUCCESS! Created Template: {template.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_empty_activities_gap(self):
        """
        GAP CHECK: Testing if system allows a template with NO activities.
        """
        template = frappe.get_doc({
            "doctype": "Employee Separation Template",
            "title": "Empty Template Test",
            "company": self.company,
            "activities": [] 
        })

        # Agar system khali template save karne de raha hai, toh hum usey 'GAP' log karenge.
        try:
            template.insert()
            if not template.activities:
                print("\n[GAP FOUND] Employee Separation Template allowed saving with ZERO activities!")
        except (ValidationError, MandatoryError):
            print("\n[SUCCESS] System correctly blocked template without activities.")

    # ------------------------
    # Logic/Duplicate Check
    # ------------------------
    def test_3_duplicate_title_gap(self):
        """
        LOGIC CHECK: Check if two templates can have the same title.
        """
        # Create first
        frappe.get_doc({
            "doctype": "Employee Separation Template",
            "title": "Exit Template Unique",
            "company": self.company
        }).insert()

        # Try to create second with same title
        duplicate = frappe.get_doc({
            "doctype": "Employee Separation Template",
            "title": "Exit Template Unique",
            "company": self.company
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed duplicate Template Titles!")
        except ValidationError:
            print("\n[SUCCESS] System blocked duplicate Template Titles.")

    def tearDown(self):
        frappe.db.rollback()