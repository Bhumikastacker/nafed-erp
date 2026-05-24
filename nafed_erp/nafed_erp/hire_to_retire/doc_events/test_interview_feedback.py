import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate
from frappe import ValidationError

class TestInterviewFeedback(FrappeTestCase):

    def setUp(self):
        designation = "Software Engineer"
        round_name = "Technical Round Feedback Test"
        applicant_email = "feedback.gap@example.com"

        if not frappe.db.exists("Designation", designation):
            frappe.get_doc({"doctype": "Designation", "designation_name": designation}).insert()
        if not frappe.db.exists("Skill", "Python"):
            frappe.get_doc({"doctype": "Skill", "skill_name": "Python"}).insert()
        if not frappe.db.exists("Interview Round", round_name):
            frappe.get_doc({
                "doctype": "Interview Round", "round_name": round_name,
                "designation": designation, "expected_skill_set": [{"skill": "Python"}]
            }).insert()
        self.round_id = round_name

        if not frappe.db.exists("Job Applicant", {"email_id": applicant_email}):
            app = frappe.get_doc({
                "doctype": "Job Applicant", "applicant_name": "Gap Candidate",
                "email_id": applicant_email, "status": "Open", "designation": designation
            }).insert()
            self.applicant_id = app.name
        else:
            self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": applicant_email}, "name")

        if not frappe.db.exists("Interviewer", "Administrator"):
            itw = frappe.new_doc("Interviewer")
            itw.name = "Administrator"
            itw.insert(ignore_mandatory=True)

        interview = frappe.get_doc({
            "doctype": "Interview", "interview_round": self.round_id,
            "job_applicant": self.applicant_id, "status": "Pending",
            "scheduled_on": getdate(), "from_time": "10:00:00", "to_time": "11:00:00",
            "interview_details": [{"interviewer": "Administrator"}]
        }).insert()
        self.interview_id = interview.name
        frappe.db.commit()

    def test_1_feedback_creation(self):
        """Positive Case: Standard feedback creation"""
        feedback = self.create_dummy_feedback()
        feedback.insert()
        self.assertTrue(frappe.db.exists("Interview Feedback", feedback.name))
        print(f"\n[Positive Test] SUCCESS! ID: {feedback.name}")

    def test_2_empty_skill_assessment_gap(self):
        """GAP CHECK: Testing if system allows feedback without skill ratings"""
        feedback = self.create_dummy_feedback()
        feedback.skill_assessment = [] # Wrong DATA (Empty table)
        
        try:
            feedback.insert()
            print("\n[GAP FOUND] Interview Feedback allowed WITHOUT any Skill Assessment!")
        except ValidationError:
            print("\n[SUCCESS] System blocked empty skill assessment.")

    def test_3_duplicate_feedback_gap(self):
        """GAP CHECK: Testing if same interviewer can give multiple feedbacks for same session"""
        # insert the first feedback.
        self.create_dummy_feedback().insert()
        
        # Insert the second feedback for the same interview and the same user (Administrator).
        duplicate = self.create_dummy_feedback()
        
        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed DUPLICATE feedback from the same interviewer!")
        except ValidationError:
            print("[SUCCESS] System blocked duplicate feedback.")

    def create_dummy_feedback(self):
        """Helper to create Interview Feedback object"""
        return frappe.get_doc({
            "doctype": "Interview Feedback",
            "interview": self.interview_id,
            "interview_round": self.round_id,
            "interviewer": "Administrator",
            "result": "Cleared",
            "feedback": "Technical skills are good.",
            "skill_assessment": [{"skill": "Python", "rating": 4}]
        })

    def tearDown(self):
        frappe.db.rollback()


# ========================================Positive Case=========================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestInterviewFeedback(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites: Designation, Skill, Interview Round, Job Applicant, and Interview.
#         """
#         designation = "Software Engineer"
#         round_name = "Technical Round Feedback Test"
#         applicant_email = "feedback.test@example.com"

#         # 1. Ensure Designation exists
#         if not frappe.db.exists("Designation", designation):
#             frappe.get_doc({"doctype": "Designation", "designation_name": designation}).insert()

#         # 2. Ensure Skill exists
#         if not frappe.db.exists("Skill", "Python"):
#             frappe.get_doc({"doctype": "Skill", "skill_name": "Python"}).insert()

#         # 3. Create an Interview Round
#         if not frappe.db.exists("Interview Round", round_name):
#             frappe.get_doc({
#                 "doctype": "Interview Round",
#                 "round_name": round_name,
#                 "designation": designation,
#                 "expected_skill_set": [{"skill": "Python"}]
#             }).insert()
#         self.round_id = round_name

#         # 4. Create a Job Applicant
#         if not frappe.db.exists("Job Applicant", {"email_id": applicant_email}):
#             app = frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 "applicant_name": "Feedback Candidate",
#                 "email_id": applicant_email,
#                 "status": "Open",
#                 "designation": designation
#             }).insert()
#             self.applicant_id = app.name
#         else:
#             self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": applicant_email}, "name")

#         # 5. Create/Get Interviewer (Administrator)
#         if not frappe.db.exists("Interviewer", "Administrator"):
#             itw = frappe.new_doc("Interviewer")
#             itw.name = "Administrator"
#             try: itw.set("interviewer", "Administrator")
#             except: pass
#             itw.insert(ignore_mandatory=True)

#         # 6. Create an Interview and Assign Administrator
#         interview = frappe.get_doc({
#             "doctype": "Interview",
#             "interview_round": self.round_id,
#             "job_applicant": self.applicant_id,
#             "status": "Pending",
#             "scheduled_on": getdate(),
#             "from_time": "10:00:00",
#             "to_time": "11:00:00",
#             "interview_details": [{"interviewer": "Administrator"}]
#         }).insert()
#         self.interview_id = interview.name

#         # Commit changes so links are visible
#         frappe.db.commit()

#     def test_interview_feedback_creation(self):
#         """
#         Positive Test: Create Interview Feedback with correct data.
#         """
#         feedback_doc = frappe.get_doc({
#             "doctype": "Interview Feedback",
#             "interview": self.interview_id,
#             "interview_round": self.round_id,
#             "interviewer": "Administrator",
#             "result": "Cleared",
#             "feedback": "Excellent technical knowledge.",
#             "skill_assessment": [{"skill": "Python", "rating": 4}]
#         })
        
#         feedback_doc.insert()
#         # frappe.db.commit() # To see in UI
        
#         self.assertTrue(frappe.db.exists("Interview Feedback", feedback_doc.name))
#         print(f"\n[Feedback Test] SUCCESS! Created ID: {feedback_doc.name}")

#     def test_invalid_email_validation(self):
#         """
#         Negative Test: Check if system blocks email without '@'.
#         """
#         from frappe import ValidationError
        
#         invalid_email = "tester.at.gmail.com" # MISSING @
        
#         # We expect the system to throw a ValidationError
#         with self.assertRaises(ValidationError):
#             frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 "applicant_name": "Invalid User",
#                 "email_id": invalid_email,
#                 "status": "Open"
#             }).insert()
        
#         print(f"\n[Email Validation Test] SUCCESS! System blocked invalid email: {invalid_email}")

#     def tearDown(self):
#         frappe.db.rollback()
#         # pass