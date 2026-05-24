import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestInterviewType(FrappeTestCase):

    def test_1_interview_type_creation(self):
        """Positive Case: Standard interview type creation"""
        test_name = "Technical Discussion Test"
        if frappe.db.exists("Interview Type", test_name):
            frappe.delete_doc("Interview Type", test_name)

        it_doc = frappe.get_doc({
            "doctype": "Interview Type",
            "name": test_name,
            "description": "Standard technical assessment."
        })
        it_doc.insert()
        self.assertTrue(frappe.db.exists("Interview Type", test_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {it_doc.name}")

    def test_2_numeric_name_gap(self):
        """GAP CHECK: Testing if system allows purely numeric names for master data"""
        numeric_name = "123456789" # WRONG DATA
        if frappe.db.exists("Interview Type", numeric_name):
            frappe.delete_doc("Interview Type", numeric_name)

        it_doc = frappe.get_doc({
            "doctype": "Interview Type",
            "name": numeric_name
        })

        try:
            it_doc.insert()
            print("\n[GAP FOUND] Interview Type allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric master data name.")

    def test_3_special_character_gap(self):
        """GAP CHECK: Testing if system allows special characters in master data name"""
        special_name = "HR @#$%^&*" # WRONG DATA
        if frappe.db.exists("Interview Type", special_name):
            frappe.delete_doc("Interview Type", special_name)

        it_doc = frappe.get_doc({
            "doctype": "Interview Type",
            "name": special_name
        })

        try:
            it_doc.insert()
            print("[GAP FOUND] Interview Type allowed SPECIAL CHARACTERS in name!")
        except ValidationError:
            print("[SUCCESS] System blocked special characters in master data.")

    def tearDown(self):
        frappe.db.rollback()


# ==============================================Positive Case==================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase

# class TestInterviewType(FrappeTestCase):

#     def test_interview_type_creation(self):
#         """
#         Verify that a new Interview Type can be created successfully.
#         Focus: Validating record creation with manual naming (Prompt).
#         """
#         # The name of the Interview Type we want to create
#         test_type_name = "Technical Discussion"

#         # Check if the record already exists to prevent DuplicateEntryError
#         if frappe.db.exists("Interview Type", test_type_name):
#             frappe.delete_doc("Interview Type", test_type_name)

#         # Creating the Interview Type document
#         interview_type = frappe.get_doc({
#             "doctype": "Interview Type",
#             "name": test_type_name, # This acts as the ID/Name
#             "description": "Assessment of technical skills and coding ability." # Optional field
#         })
        
#         # Inserting the record into the database
#         interview_type.insert()

#         # Save the record in database
#         # frappe.db.commit()

#         # Assert: Verify that the record actually exists in the database
#         self.assertTrue(frappe.db.exists("Interview Type", test_type_name))
        
#         # Log success message
#         print(f"\n[Interview Type Test] SUCCESS! Created ID: {interview_type.name}")

#     def tearDown(self):
#         """
#         Cleanup after the test to keep the database clean.
#         """
#         frappe.db.rollback()