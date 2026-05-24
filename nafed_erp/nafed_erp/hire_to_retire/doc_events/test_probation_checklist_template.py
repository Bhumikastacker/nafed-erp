import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestProbationChecklistTemplate(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_template_creation(self):
        """
        CASE 1: Verify that a valid Probation Checklist Template can be created.
        """
        title = "Standard Probation Review Plan"
        
        # Cleanup if exists
        if frappe.db.exists("Probation Checklist Template", title):
            frappe.delete_doc("Probation Checklist Template", title)

        template = frappe.get_doc({
            "doctype": "Probation Checklist Template",
            "probation_review_template_title": title, # Mandatory & Unique
            "probation_review": [
                {
                    "check_list": "Review job responsibilities"
                },
                {
                    "check_list": "Confirm tool access"
                }
            ]
        })
        template.insert()
        
        # Assertion
        self.assertTrue(frappe.db.exists("Probation Checklist Template", title))
        print(f"\n[Positive Test] SUCCESS! Created ID: {template.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_checklist_gap(self):
        """
        GAP CHECK: Testing if system allows saving a template without any checklist tasks.
        Logically, a checklist template must have items.
        """
        title = "Empty Checklist Gap Test"
        if frappe.db.exists("Probation Checklist Template", title):
            frappe.delete_doc("Probation Checklist Template", title)

        template = frappe.get_doc({
            "doctype": "Probation Checklist Template",
            "probation_review_template_title": title,
            "probation_review": [] # INVALID: Empty child table
        })

        try:
            template.insert()
            print("\n[GAP FOUND] System allowed Probation Template WITHOUT any checklist items!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty checklist template.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_title_gap(self):
        """
        GAP CHECK: Testing if purely numeric titles (e.g., '12345') are allowed.
        """
        numeric_title = "998877"
        if frappe.db.exists("Probation Checklist Template", numeric_title):
            frappe.delete_doc("Probation Checklist Template", numeric_title)

        template = frappe.get_doc({
            "doctype": "Probation Checklist Template",
            "probation_review_template_title": numeric_title
        })

        try:
            template.insert()
            print("[GAP FOUND] System allowed a PURELY NUMERIC title for the template!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric template title.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()