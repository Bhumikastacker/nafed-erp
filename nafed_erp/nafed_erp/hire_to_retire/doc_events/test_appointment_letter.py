import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestAppointmentLetter(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Appointment Letter tests.
        Creates a Job Applicant and an Appointment Letter Template with mandatory terms.
        """
        # 1. Create a Job Applicant for testing
        applicant_email = "appointment.gap@example.com"
        if not frappe.db.exists("Job Applicant", {"email_id": applicant_email}):
            applicant = frappe.get_doc({
                "doctype": "Job Applicant",
                "applicant_name": "Gap Test Candidate",
                "email_id": applicant_email,
                "status": "Open"
            }).insert()
            self.applicant_id = applicant.name
        else:
            self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": applicant_email}, "name")

        # 2. Create an Appointment Letter Template with Mandatory Fields
        template_name = "Standard Template Gap Test"
        if not frappe.db.exists("Appointment Letter Template", template_name):
            frappe.get_doc({
                "doctype": "Appointment Letter Template",
                "template_name": template_name,
                "introduction": "This is a test introduction.",
                "terms": [{"title": "Test Term", "description": "Test Description"}]
            }).insert()
        self.template_id = template_name

        frappe.db.commit()

    def test_1_appointment_letter_creation(self):
        """
        Positive Case: Verify that a valid Appointment Letter can be created.
        """
        letter = self.create_dummy_letter(self.applicant_id, getdate())
        letter.insert()
        self.assertTrue(frappe.db.exists("Appointment Letter", letter.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {letter.name}")

    def test_2_backdated_appointment_gap(self):
        """
        GAP CHECK: Testing if system allows Appointment Date to be from 1 year ago.
        """
        backdate = add_days(getdate(), -365) # 1 year ago
        letter = self.create_dummy_letter(self.applicant_id, backdate)
        
        try:
            letter.insert()
            print("\n[GAP FOUND] System allowed BACKDATED Appointment Letter (1 year old)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked backdated appointment dates.")

    def test_3_duplicate_appointment_gap(self):
        """
        GAP CHECK: Testing if multiple Appointment Letters are allowed for the same applicant.
        """
        # Create first letter
        self.create_dummy_letter(self.applicant_id, getdate()).insert()
        
        # Try to create second letter for the SAME applicant
        duplicate_letter = self.create_dummy_letter(self.applicant_id, getdate())
        
        try:
            duplicate_letter.insert()
            print("[GAP FOUND] Multiple Appointment Letters allowed for the SAME applicant!")
        except ValidationError:
            print("[SUCCESS] System blocked duplicate appointment letters.")

    def test_4_rejected_applicant_gap(self):
        """
        GAP CHECK: Testing if an Appointment Letter can be created for a REJECTED applicant.
        """
        # Mark applicant as Rejected
        frappe.db.set_value("Job Applicant", self.applicant_id, "status", "Rejected")
        
        letter = self.create_dummy_letter(self.applicant_id, getdate())
        
        try:
            letter.insert()
            print("[GAP FOUND] System allowed Appointment Letter for a REJECTED applicant!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked letter for rejected applicant.")

    def create_dummy_letter(self, applicant_id, app_date):
        """
        Helper function to generate an Appointment Letter object with mandatory fields.
        """
        return frappe.get_doc({
            "doctype": "Appointment Letter",
            "job_applicant": applicant_id,
            "applicant_name": "Gap Test Candidate",
            "company": "_Test Indian Registered Company",
            "appointment_date": app_date,
            "appointment_letter_template": self.template_id,
            "introduction": "Welcome aboard!",
            "terms": [{"title": "Condition 1", "description": "Description 1"}]
        })

    def tearDown(self):
        """
        Rollback database changes after each test.
        """
        frappe.db.rollback()



# ==========================================Positive Case========================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestAppointmentLetter(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites for the Appointment Letter test.
#         """
#         # 1. Create a Job Applicant
#         applicant_email = "appointment.test@example.com"
#         if not frappe.db.exists("Job Applicant", {"email_id": applicant_email}):
#             applicant = frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 "applicant_name": "Test Appointment Candidate",
#                 "email_id": applicant_email,
#                 "status": "Open"
#             }).insert()
#             self.applicant_id = applicant.name
#         else:
#             self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": applicant_email}, "name")

#         # 2. Create an Appointment Letter Template with MANDATORY FIELDS
#         template_name = "Standard Appointment Template"
#         if not frappe.db.exists("Appointment Letter Template", template_name):
#             frappe.get_doc({
#                 "doctype": "Appointment Letter Template",
#                 "template_name": template_name, # Mandatory field
#                 "introduction": "We are pleased to offer you the position...", # Mandatory Long Text
#                 "terms": [
#                     {
#                         "title": "General Condition",
#                         "description": "Terms and conditions apply."
#                     }
#                 ]
#             }).insert()
#         self.template_id = template_name

#         # Commit to ensure links are available for validation
#         frappe.db.commit()

#     def test_appointment_letter_creation(self):
#         """
#         Verify that an Appointment Letter can be created with all mandatory fields.
#         """
#         appointment_letter = frappe.get_doc({
#             "doctype": "Appointment Letter",
#             "job_applicant": self.applicant_id,             # Mandatory Link
#             "applicant_name": "Test Appointment Candidate", # Mandatory Data
#             "company": "_Test Indian Registered Company",   # Mandatory Link
#             "appointment_date": getdate(),                  # Mandatory Date
#             "appointment_letter_template": self.template_id, # Mandatory Link
#             "introduction": "Welcome to the team!",          # Mandatory Long Text
            
#             # --- MANDATORY CHILD TABLE: terms ---
#             "terms": [
#                 {
#                     "title": "Working Hours",
#                     "description": "9:00 AM to 6:00 PM"
#                 }
#             ]
#         })
        
#         # Insert the document
#         appointment_letter.insert()
        
#         # Permanent save for UI verification
#         # frappe.db.commit()
        
#         # Assert: Verify that the record exists in the database
#         self.assertTrue(frappe.db.exists("Appointment Letter", appointment_letter.name))
#         print(f"\n[Appointment Letter Test] SUCCESS! Created ID: {appointment_letter.name}")

#     def tearDown(self):
#         # Rollback (Commented because of commit)
#         frappe.db.rollback()
#         # pass