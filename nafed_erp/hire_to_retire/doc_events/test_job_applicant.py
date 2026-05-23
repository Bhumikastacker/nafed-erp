import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestJobApplicant(FrappeTestCase):

    def setUp(self):
        # 1. Setup Designation
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({
                "doctype": "Designation", 
                "designation_name": "Software Engineer"
            }).insert()

    def test_1_job_applicant_creation(self):
        """Positive Case: Standard record creation"""
        applicant = self.create_dummy_applicant(email="ramesh.success@example.com")
        applicant.insert()
        self.assertTrue(frappe.db.exists("Job Applicant", applicant.name))
        print(f"\n[Positive Test] SUCCESS! ID: {applicant.name}")

    def test_2_invalid_email_gap(self):
        """GAP CHECK: Testing if system allows invalid email format"""
        applicant = self.create_dummy_applicant(email="wrongemail.com")
        try:
            applicant.insert()
            print("\n[GAP FOUND] Job Applicant allowed INVALID EMAIL format!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid email.")

    def test_3_invalid_phone_gap(self):
        """GAP CHECK: Testing alphabets and length (10 digits) for phone number"""
        
        # A. Testing Alphabets (Unique Email)
        app_a = self.create_dummy_applicant(email="phone_alpha@test.com")
        app_a.phone_number = "ABCDEFGHIJ" 
        try:
            app_a.insert()
            print("[GAP FOUND] Job Applicant allowed ALPHABETS in phone number!")
        except ValidationError:
            print("[SUCCESS] System blocked alphabets in phone number.")

        # B. Testing Short Length (Unique Email)
        app_b = self.create_dummy_applicant(email="phone_short@test.com")
        app_b.phone_number = "12345" 
        try:
            app_b.insert()
            print("[GAP FOUND] Job Applicant allowed SHORT phone number (5 digits)!")
        except ValidationError:
            print("[SUCCESS] System blocked short phone number.")

        # C. Testing Long Length (Unique Email)
        app_c = self.create_dummy_applicant(email="phone_long@test.com")
        app_c.phone_number = "123456789012345" 
        try:
            app_c.insert()
            print("[GAP FOUND] Job Applicant allowed LONG phone number (15 digits)!")
        except ValidationError:
            print("[SUCCESS] System blocked long phone number.")

    def test_4_numeric_name_gap(self):
        """GAP CHECK: Testing if system allows only numbers in applicant name"""
        applicant = self.create_dummy_applicant(email="name_numeric@test.com")
        applicant.applicant_name = "12345678"
        try:
            applicant.insert()
            print("[GAP FOUND] Job Applicant allowed NUMERIC applicant name!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked numeric name.")

    def create_dummy_applicant(self, email):
        return frappe.get_doc({
            "doctype": "Job Applicant",
            "applicant_name": "Test User",
            "email_id": email,
            "status": "Open",
            "designation": "Software Engineer",
            "phone_number": "9876543210",
            "country": "India"
        })

    def tearDown(self):
        frappe.db.rollback()

# =================================================Positive Case===================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase

# class TestJobApplicant(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites for the test case.
#         Ensures that required master data like Designation exists.
#         """
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({
#                 "doctype": "Designation", 
#                 "designation_name": "Software Engineer"
#             }).insert()

#     def test_job_applicant_creation(self):
#         """
#         Verify that a Job Applicant record can be created successfully
#         with all mandatory fields as per the DocType definition.
#         """
        
#         # Creating a new Job Applicant document using mandatory fields identified from JSON
#         applicant = frappe.get_doc({
#             "doctype": "Job Applicant",
#             "applicant_name": "Ramesh Singh",
#             "email_id": "ramesh.singh@example.com", # Mandatory field: email_id
#             "status": "Open",                        # Mandatory field: status
#             "designation": "Software Engineer",      # Linked field
#             "phone_number": "9876543210",            # Optional data field
#             "country": "India"                       # Optional link field
#         })
        
#         # Insert the document into the database
#         applicant.insert()

#         # Save the record in the Database
#         # frappe.db.commit()
        
#         # Assert that the record was successfully saved in the database
#         self.assertTrue(frappe.db.exists("Job Applicant", applicant.name))
        
#         # Log the success message and Created ID to the console
#         print(f"\n[Job Applicant Test] SUCCESS! Created ID: {applicant.name}")

#     def tearDown(self):
#         """
#         Clean up after the test. 
#         Rollback database changes to keep the test environment clean.
#         """
#         frappe.db.rollback()