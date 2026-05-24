import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestInterviewRound(FrappeTestCase):

    def setUp(self):
        # 1. Setup Designation
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

        # 2. Setup Skill
        if not frappe.db.exists("Skill", "Python"):
            frappe.get_doc({"doctype": "Skill", "skill_name": "Python"}).insert()

        # 3. Setup Interview Type
        if not frappe.db.exists("Interview Type", "Technical"):
            frappe.get_doc({"doctype": "Interview Type", "name": "Technical"}).insert()

    def test_1_round_creation(self):
        """Positive Case: Standard interview round creation"""
        round_name = "Success Round Test"
        if frappe.db.exists("Interview Round", round_name):
            frappe.delete_doc("Interview Round", round_name)

        doc = self.create_dummy_round(round_name)
        doc.insert()
        self.assertTrue(frappe.db.exists("Interview Round", round_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {doc.name}")

    def test_2_empty_skillset_gap(self):
        """GAP CHECK: Testing if system allows Round creation without any Skills"""
        round_name = "Empty Skill Gap Test"
        if frappe.db.exists("Interview Round", round_name):
            frappe.delete_doc("Interview Round", round_name)

        doc = self.create_dummy_round(round_name)
        doc.expected_skill_set = [] # WRONG DATA (Empty child table)

        try:
            doc.insert()
            print("\n[GAP FOUND] Interview Round allowed creation without any SKILLS!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty skillset.")

    def test_3_duplicate_round_name_gap(self):
        """GAP CHECK: Testing duplicate Round Name handling"""
        round_name = "Duplicate Check Test"
        # Create the first record.
        self.create_dummy_round(round_name).insert()
        
        # Trying to create the second record with the same name.
        duplicate_doc = self.create_dummy_round(round_name)
        
        try:
            duplicate_doc.insert()
            print("[GAP FOUND] System allowed DUPLICATE Round Names!")
        except frappe.DuplicateEntryError:
            print("[SUCCESS] System correctly blocked duplicate round name.")

    def create_dummy_round(self, name):
        """Helper to create Interview Round object"""
        return frappe.get_doc({
            "doctype": "Interview Round",
            "round_name": name,
            "interview_type": "Technical",
            "designation": "Software Engineer",
            "expected_average_rating": 3,
            "expected_skill_set": [{"skill": "Python"}]
        })

    def tearDown(self):
        frappe.db.rollback()

# ============================================Positive Case==================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase

# class TestInterviewRound(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites for the Interview Round test.
#         Ensures Designation, Skill, and Interview Type exist.
#         """
#         # 1. Ensure Designation exists
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({
#                 "doctype": "Designation", 
#                 "designation_name": "Software Engineer"
#             }).insert()

#         # 2. Ensure Skill exists (Mandatory for Expected Skillset table)
#         if not frappe.db.exists("Skill", "Python"):
#             frappe.get_doc({
#                 "doctype": "Skill",
#                 "skill_name": "Python"
#             }).insert()

#         # 3. Ensure Interview Type exists
#         if not frappe.db.exists("Interview Type", "Technical"):
#             frappe.get_doc({
#                 "doctype": "Interview Type",
#                 "name": "Technical"
#             }).insert()

#     def test_interview_round_creation(self):
#         """
#         Verify that an Interview Round can be created with mandatory fields and child table.
#         """
#         round_name = "Technical Round Test"

#         # Cleanup existing record to avoid unique constraint error
#         if frappe.db.exists("Interview Round", round_name):
#             frappe.delete_doc("Interview Round", round_name)

#         # Creating the Interview Round document based on JSON structure
#         interview_round = frappe.get_doc({
#             "doctype": "Interview Round",
#             "round_name": round_name,          # Mandatory field (Autoname)
#             "interview_type": "Technical",    # Link field
#             "designation": "Software Engineer", # Link field
#             "expected_average_rating": 4,      # Rating field
            
#             # --- MANDATORY CHILD TABLE: expected_skill_set ---
#             "expected_skill_set": [
#                 {
#                     "skill": "Python"          # Mandatory field in child table
#                 }
#             ]
#         })
        
#         # Insert the record
#         interview_round.insert()
        
#         # Commit for UI verification (Optional)
#         # frappe.db.commit()

#         # Assert: Verify the record exists in the database
#         self.assertTrue(frappe.db.exists("Interview Round", round_name))
#         print(f"\n[Interview Round Test] SUCCESS! Created ID: {interview_round.name}")

#     def tearDown(self):
#         """
#         Cleanup test data.
#         """
#         frappe.db.rollback()
#         # pass