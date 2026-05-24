import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestAppointmentLetterTemplate(FrappeTestCase):

    def test_1_positive_template_creation(self):
        """
        Positive Case: Create a valid Appointment Letter Template.
        """
        template_name = "Success Template Test"
        if frappe.db.exists("Appointment Letter Template", template_name):
            frappe.delete_doc("Appointment Letter Template", template_name)

        template = frappe.get_doc({
            "doctype": "Appointment Letter Template",
            "template_name": template_name,
            "introduction": "We are pleased to offer you...",
            "terms": [
                {
                    "title": "Working Hours",
                    "description": "9 AM to 6 PM"
                }
            ]
        })
        template.insert()
        self.assertTrue(frappe.db.exists("Appointment Letter Template", template_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {template.name}")

    def test_2_empty_terms_gap(self):
        """
        GAP CHECK: Testing if system allows Template creation without any Terms.
        As per JSON, terms is mandatory.
        """
        template_name = "Empty Terms Gap Test"
        if frappe.db.exists("Appointment Letter Template", template_name):
            frappe.delete_doc("Appointment Letter Template", template_name)

        template = frappe.get_doc({
            "doctype": "Appointment Letter Template",
            "template_name": template_name,
            "introduction": "Test Intro",
            "terms": [] # GALAT DATA (Empty child table)
        })

        try:
            template.insert()
            print("\n[GAP FOUND] Appointment Letter Template allowed WITHOUT any Terms!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked template without terms.")

    def test_3_duplicate_name_gap(self):
        """
        GAP CHECK: Testing duplicate Template Name handling.
        """
        template_name = "Duplicate Name Test"
        # Pehla record
        if not frappe.db.exists("Appointment Letter Template", template_name):
            frappe.get_doc({
                "doctype": "Appointment Letter Template",
                "template_name": template_name,
                "introduction": "Intro 1",
                "terms": [{"title": "T1", "description": "D1"}]
            }).insert()

        # Dusra record SAME NAME ke saath
        duplicate = frappe.get_doc({
            "doctype": "Appointment Letter Template",
            "template_name": template_name,
            "introduction": "Intro 2",
            "terms": [{"title": "T2", "description": "D2"}]
        })

        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed DUPLICATE Template Names!")
        except frappe.DuplicateEntryError:
            print("[SUCCESS] System correctly blocked duplicate template name.")

    def tearDown(self):
        frappe.db.rollback()