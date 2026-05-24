import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestAppraisalTemplate(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure KRA and Feedback Criteria exist.
        """
        self.company = "_Test Indian Registered Company"
        
        if not frappe.db.exists("KRA", "Coding Standards"):
            frappe.get_doc({"doctype": "KRA", "title": "Coding Standards"}).insert()
        
        if not frappe.db.exists("Employee Feedback Criteria", "Communication"):
            frappe.get_doc({"doctype": "Employee Feedback Criteria", "criteria": "Communication"}).insert()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_template_creation(self):
        """
        CASE 1: Verify valid creation with weightage summing to 100.
        """
        title = "Senior Developer Template"
        if frappe.db.exists("Appraisal Template", title):
            frappe.delete_doc("Appraisal Template", title)

        template = frappe.get_doc({
            "doctype": "Appraisal Template",
            "template_title": title,
            "goals": [
                {
                    "kra": "Coding Standards",
                    "per_weightage": 100 # Total KRA weightage = 100
                }
            ],
            "rating_criteria": [
                {
                    "feedback_criteria": "Communication",
                    "weightage": 100 # <--- FIXED: Added weightage to make it 100%
                }
            ]
        })
        template.insert()
        self.assertTrue(frappe.db.exists("Appraisal Template", title))
        print(f"\n[Positive Test] SUCCESS! Created ID: {template.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_goals_gap(self):
        """
        GAP CHECK: Testing if system blocks template without KRAs.
        """
        title = "Empty Goals Gap Test"
        if frappe.db.exists("Appraisal Template", title):
            frappe.delete_doc("Appraisal Template", title)

        template = frappe.get_doc({
            "doctype": "Appraisal Template",
            "template_title": title,
            "goals": []
        })

        try:
            template.insert()
            print("\n[GAP FOUND] Appraisal Template allowed WITHOUT any KRAs!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked template without KRAs.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_title_gap(self):
        """
        GAP CHECK: Testing if purely numeric titles are blocked.
        """
        numeric_title = "1234567"
        if frappe.db.exists("Appraisal Template", numeric_title):
            frappe.delete_doc("Appraisal Template", numeric_title)

        template = frappe.get_doc({
            "doctype": "Appraisal Template",
            "template_title": numeric_title,
            "goals": [{"kra": "Coding Standards", "per_weightage": 100}]
        })

        try:
            template.insert()
            print("[GAP FOUND] Appraisal Template allowed a PURELY NUMERIC title!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric template title.")

    def tearDown(self):
        frappe.db.rollback()