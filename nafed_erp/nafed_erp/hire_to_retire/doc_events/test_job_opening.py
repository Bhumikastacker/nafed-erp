import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days, getdate
from frappe import ValidationError
import uuid

class TestDocEvents(FrappeTestCase):

    def setUp(self):
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()
        if not frappe.db.exists("Employment Type", "Full-time"):
            frappe.get_doc({"doctype": "Employment Type", "employee_type_name": "Full-time"}).insert()

    def test_job_opening_creation(self):
        """Positive Case: Standard record creation"""
        unique_title = f"Python Developer {uuid.uuid4().hex[:5]}"
        job = self.create_dummy_job_opening(job_title=unique_title)
        job.insert()
        self.assertTrue(frappe.db.exists("Job Opening", job.name))
        print(f"\n[Positive Test] SUCCESS! ID: {job.name}")

    def test_age_logic_gap(self):
        """GAP CHECK: Testing if Max Age can be less than Min Age"""
        unique_title = f"Age Test {uuid.uuid4().hex[:5]}"
        job = self.create_dummy_job_opening(job_title=unique_title, min_age=40, max_age=20)
        try:
            job.insert()
            print("\n[GAP FOUND] Job Opening allowed Max Age (20) < Min Age (40)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid Age range.")

    def test_negative_experience_gap(self):
        """GAP CHECK: Testing if system allows negative experience"""
        unique_title = f"Exp Test {uuid.uuid4().hex[:5]}"
        job = self.create_dummy_job_opening(job_title=unique_title)
        job.custom_minimum_experience_no = -2
        try:
            job.insert()
            print("[GAP FOUND] Job Opening allowed NEGATIVE experience!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked negative experience.")

    def test_wrong_date_sequence_gap(self):
        """GAP CHECK: Testing if Closing Date can be before Publish Date"""
        unique_title = f"Date Test {uuid.uuid4().hex[:5]}"
        job = self.create_dummy_job_opening(job_title=unique_title)
        job.posted_on = now_datetime()
        job.closes_on = add_days(getdate(), -10)
        try:
            job.insert()
            print("[GAP FOUND] Job Opening allowed Closing Date < Publish Date!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked invalid date sequence.")

    def create_dummy_job_opening(self, job_title, min_age=18, max_age=45):
        return frappe.get_doc({
            "doctype": "Job Opening",
            "job_title": job_title,
            "designation": "Software Engineer",
            "employment_type": "Full-time",
            "status": "Open",
            "posted_on": now_datetime(),
            "closes_on": add_days(getdate(), 30),
            "company": "_Test Indian Registered Company",
            "description": "Test",
            "custom_application_fees_category": [{"category": "General", "fees": 500}],
            "custom_qualification_and_marks": [{"qualification": "B.Tech", "marks": "60%"}],
            "custom_minimum_age_limit": min_age,
            "custom_maximum_age_limit": max_age,
            "custom_minimum_experience_no": 2,
            "custom_maximum_age_limit_desc": "Test",
            "custom_minimum_experience_details": "Test",
            "custom_pay__scalefixed_monthly_revaluation": "Test",
            "custom_essentional_duties_and__responsibilities": "Test",
            "custom_instructions": "Test",
            "custom_minimum_qualification": "Test",
            "custom_method_of_recruitment": "Direct"
        })

    def tearDown(self):
        frappe.db.rollback()



# =========================================Possitive==========================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import now_datetime, add_days, getdate

# class TestDocEvents(FrappeTestCase):

#     def setUp(self):

#         # 1. Create Designation 
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

#         # 2. Create Employment Type 
#         if not frappe.db.exists("Employment Type", "Full-time"):
#             frappe.get_doc({"doctype": "Employment Type", "employee_type_name": "Full-time"}).insert()

#     def test_job_opening_creation(self):
#         """Job Opening test with exact fields from Customize Form"""
        
#         job = frappe.get_doc({
#             "doctype": "Job Opening",
#             "job_title": "Python Developer", 
#             "designation": "Software Engineer",
#             "employment_type": "Full-time",
#             "status": "Open",
#             "posted_on": now_datetime(), 
#             "closes_on": add_days(getdate(), 30),
#             "company": "_Test Indian Registered Company",
#             "description": "Test Job Description",

#             # --- CHILD TABLES (List of Dicts) ---
#             # Table Type: Fees Applicable for Category and Amount
#             "custom_application_fees_category": [
#                 {"category": "General", "fees": 500} 
#             ],

#             # Table Type: Qualification
#             "custom_qualification_and_marks": [
#                 {"qualification": "B.Tech", "marks": "60%"}
#             ],

#             # --- MANDATORY CUSTOM FIELDS (Simple Data/Text) ---
#             "custom_minimum_age_limit": 18,
#             "custom_maximum_age_limit": 45,
#             "custom_minimum_experience_no": "2",
#             "custom_maximum_age_limit_desc": "Age relaxation as per govt rules",
#             "custom_minimum_experience_details": "Minimum 2 years in Python/Django",
#             "custom_pay__scalefixed_monthly_revaluation": "Level 10 Pay Scale",
#             "custom_essentional_duties_and__responsibilities": "Development and Support",
#             "custom_instructions": "Read all instructions carefully before applying",
#             "custom_minimum_qualification": "Graduate in Engineering", 
#             "custom_method_of_recruitment": "Direct Recruitment" 
#         })
        
#         job.insert()
#         # frappe.db.commit()
        
#         self.assertTrue(frappe.db.exists("Job Opening", job.name))
#         print(f"\n[Job Opening Test] SUCCESS! ID: {job.name}")

#     def tearDown(self):
#         frappe.db.rollback()