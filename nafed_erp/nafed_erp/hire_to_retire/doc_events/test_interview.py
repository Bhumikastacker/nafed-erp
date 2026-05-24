import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestInterview(FrappeTestCase):

    def setUp(self):
        # 1. Setup Designation
        self.designation = "Software Engineer"
        if not frappe.db.exists("Designation", self.designation):
            frappe.get_doc({"doctype": "Designation", "designation_name": self.designation}).insert()

        # 2. Setup Skill
        if not frappe.db.exists("Skill", "Python"):
            frappe.get_doc({"doctype": "Skill", "skill_name": "Python"}).insert()

        # 3. Setup Interview Round
        self.round_name = "Technical Round 1"
        if not frappe.db.exists("Interview Round", self.round_name):
            frappe.get_doc({
                "doctype": "Interview Round",
                "round_name": self.round_name,
                "designation": self.designation,
                "expected_skill_set": [{"skill": "Python"}]
            }).insert()

        # 4. Setup Job Applicant
        email = "interview.gap@example.com"
        if not frappe.db.exists("Job Applicant", {"email_id": email}):
            app = frappe.get_doc({
                "doctype": "Job Applicant",
                "applicant_name": "Gap Candidate",
                "email_id": email,
                "status": "Open",
                "designation": self.designation
            }).insert()
            self.applicant_id = app.name
        else:
            self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": email}, "name")

        # 5. Setup Interviewer
        self.interviewer_id = "Administrator"
        if not frappe.db.exists("Interviewer", self.interviewer_id):
            itw = frappe.new_doc("Interviewer")
            itw.name = self.interviewer_id
            itw.insert(ignore_mandatory=True)
        
        frappe.db.commit()

    def test_1_interview_creation(self):
        """Positive Case: Standard interview creation"""
        interview = self.create_dummy_interview()
        interview.insert()
        self.assertTrue(frappe.db.exists("Interview", interview.name))
        print(f"\n[Positive Test] SUCCESS! ID: {interview.name}")

    def test_2_time_sequence_gap(self):
        """GAP CHECK: Testing if To Time can be BEFORE From Time"""
        interview = self.create_dummy_interview()
        interview.from_time = "11:00:00"
        interview.to_time = "10:00:00" # Wrong DATA
        
        try:
            interview.insert()
            print("\n[GAP FOUND] System allowed Interview End Time < Start Time!")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid time sequence.")

    def test_3_designation_mismatch_gap(self):
        """GAP CHECK: Testing if system blocks Round-Designation mismatch"""
        # reate a new round for the Accountant.
        wrong_round = "Accountant Round Test"
        if not frappe.db.exists("Interview Round", wrong_round):
            frappe.get_doc({
                "doctype": "Interview Round",
                "round_name": wrong_round,
                "designation": "Accountant", # DIFFERENT DESIGNATION
                "expected_skill_set": [{"skill": "Python"}]
            }).insert()

        interview = self.create_dummy_interview()
        interview.interview_round = wrong_round # Applicant is SE, Round is Accountant
        
        try:
            interview.insert()
            print("[GAP FOUND] System allowed Designation Mismatch (SE Applicant in Accountant Round)!")
        except Exception: # We had seen earlier that it throws a custom error.
            print("[SUCCESS] System blocked designation mismatch.")

    def test_4_empty_interviewer_gap(self):
        """GAP CHECK: Testing if an interview can be created without interviewers"""
        interview = self.create_dummy_interview()
        interview.interview_details = [] # WRONG DATA (Empty table)
        
        try:
            interview.insert()
            print("[GAP FOUND] System allowed Interview without any Interviewers!")
        except ValidationError:
            print("[SUCCESS] System blocked interview with no interviewers.")

    def create_dummy_interview(self):
        """Helper to create Interview object"""
        return frappe.get_doc({
            "doctype": "Interview",
            "interview_round": self.round_name,
            "job_applicant": self.applicant_id,
            "status": "Pending",
            "scheduled_on": add_days(getdate(), 1),
            "from_time": "10:00:00",
            "to_time": "11:00:00",
            "interview_details": [{"interviewer": self.interviewer_id}]
        })

    def tearDown(self):
        frappe.db.rollback()



# ===========================================Positive Case========================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate, add_days

# class TestInterview(FrappeTestCase):

#     def setUp(self):
#         """
#         Setup pre-requisites: Designation, Skill, Round, Applicant, and Interviewer.
#         """
#         # 1. Ensure Designation exists
#         designation = "Software Engineer"
#         if not frappe.db.exists("Designation", designation):
#             frappe.get_doc({
#                 "doctype": "Designation", 
#                 "designation_name": designation
#             }).insert()

#         # 2. Ensure Skill exists
#         if not frappe.db.exists("Skill", "Python"):
#             frappe.get_doc({"doctype": "Skill", "skill_name": "Python"}).insert()

#         # 3. Create an Interview Round linked to the Designation
#         if not frappe.db.exists("Interview Round", "Technical Round 1"):
#             frappe.get_doc({
#                 "doctype": "Interview Round",
#                 "round_name": "Technical Round 1",
#                 "designation": designation, # Round is for Software Engineer
#                 "expected_skill_set": [{"skill": "Python"}]
#             }).insert()

#         # 4. Create a Job Applicant WITH DESIGNATION
#         app_email = "interview.final.101@example.com"
#         if not frappe.db.exists("Job Applicant", {"email_id": app_email}):
#             app = frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 "applicant_name": "Final Candidate",
#                 "email_id": app_email,
#                 "status": "Open",
#                 "designation": designation # <--- SETTING DESIGNATION HERE
#             }).insert()
#             self.applicant_id = app.name
#         else:
#             self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": app_email}, "name")

#         # 5. CREATE/GET INTERVIEWER 
#         self.interviewer_id = "Administrator"
#         if not frappe.db.exists("Interviewer", self.interviewer_id):
#             itw = frappe.new_doc("Interviewer")
#             itw.name = self.interviewer_id
#             try: itw.set("interviewer", "Administrator")
#             except: pass
#             itw.insert(ignore_mandatory=True, ignore_permissions=True)
        
#         frappe.db.commit()

#     def test_interview_creation(self):
#         """
#         Verify that an Interview can be created successfully.
#         """
#         interview = frappe.get_doc({
#             "doctype": "Interview",
#             "interview_round": "Technical Round 1",
#             "job_applicant": self.applicant_id,
#             "status": "Pending",
#             "scheduled_on": add_days(getdate(), 1),
#             "from_time": "10:00:00",
#             "to_time": "11:00:00",
#             "interview_details": [
#                 {
#                     "interviewer": self.interviewer_id
#                 }
#             ]
#         })
        
#         interview.insert()
        
#         # Save for UI check
#         # frappe.db.commit()
        
#         self.assertTrue(frappe.db.exists("Interview", interview.name))
#         print(f"\n[Interview Test] SUCCESS! Created ID: {interview.name}")

#     def tearDown(self):
#         frappe.db.rollback()
#         # pass