import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestJobOffer(FrappeTestCase):

    def setUp(self):
        # 1. Setup Designation
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

        # 2. Setup Master Offer Terms
        for term_name in ["Notice Period", "Annual Leave"]:
            if not frappe.db.exists("Offer Term", term_name):
                frappe.get_doc({"doctype": "Offer Term", "offer_term": term_name}).insert()

        # 3. Create a valid Job Applicant for testing
        email = "offer.gap.test@example.com"
        if not frappe.db.exists("Job Applicant", {"email_id": email}):
            applicant = frappe.get_doc({
                "doctype": "Job Applicant",
                "applicant_name": "Suresh Gap Test",
                "email_id": email,
                "status": "Open",
                "designation": "Software Engineer"
            }).insert()
            self.applicant_id = applicant.name
        else:
            self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": email}, "name")

    def test_1_job_offer_creation(self):
        """Positive Case: Standard job offer creation"""
        offer = self.create_dummy_offer(self.applicant_id)
        offer.insert()
        self.assertTrue(frappe.db.exists("Job Offer", offer.name))
        print(f"\n[Positive Test] SUCCESS! ID: {offer.name}")

    def test_2_offer_to_rejected_applicant_gap(self):
        """GAP CHECK: Testing if system allows offer to a REJECTED applicant"""
        # Step 1: Applicant ko reject kar dete hain
        frappe.db.set_value("Job Applicant", self.applicant_id, "status", "Rejected")
        
        # Step 2: Try to create Job Offer
        offer = self.create_dummy_offer(self.applicant_id)
        
        try:
            offer.insert()
            print("\n[GAP FOUND] Job Offer allowed for a REJECTED applicant!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked offer to rejected applicant.")

    def test_3_backdated_offer_gap(self):
        """GAP CHECK: Testing if system allows backdated offers (1 year old)"""
        backdate = add_days(getdate(), -365) # 1 saal purani date
        offer = self.create_dummy_offer(self.applicant_id)
        offer.offer_date = backdate
        
        try:
            offer.insert()
            print("[GAP FOUND] Job Offer allowed BACKDATED offer dates!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked backdated offer.")

    def create_dummy_offer(self, applicant_id):
        """Helper to create Job Offer object"""
        return frappe.get_doc({
            "doctype": "Job Offer",
            "job_applicant": applicant_id,
            "applicant_name": "Suresh Gap Test",
            "offer_date": getdate(),
            "designation": "Software Engineer",
            "company": "_Test Indian Registered Company",
            "status": "Awaiting Response",
            "offer_terms": [{"offer_term": "Notice Period", "value": "3 Month"}]
        })

    def tearDown(self):
        frappe.db.rollback()

# ===============================================Positive Case====================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestJobOffer(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites: Designation, Master Offer Terms, and Job Applicant.
#         """
#         # 1. Ensure Designation exists
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({
#                 "doctype": "Designation", 
#                 "designation_name": "Software Engineer"
#             }).insert()

#         # 2. CREATE MASTER TERMS (In 'Offer Term' Master DocType)
#         # We are checking and creating "Notice Period" and "Annual Leave".
#         for term_name in ["Notice Period", "Annual Leave"]:
#             if not frappe.db.exists("Offer Term", term_name):
#                 frappe.get_doc({
#                     "doctype": "Offer Term",
#                     "offer_term": term_name # If the fieldname is 'term', then change it here.
#                 }).insert()

#         # 3. Create a Job Applicant (Mandatory dependency)
#         if not frappe.db.exists("Job Applicant", {"email_id": "offer.test@example.com"}):
#             applicant = frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 "applicant_name": "Suresh Offer Test",
#                 "email_id": "offer.test@example.com",
#                 "status": "Open",
#                 "designation": "Software Engineer"
#             }).insert()
#             self.applicant_id = applicant.name
#         else:
#             self.applicant_id = frappe.db.get_value("Job Applicant", {"email_id": "offer.test@example.com"}, "name")

#     def test_job_offer_creation(self):
#         """
#         Test Job Offer creation with Child Table linking to Master 'Offer Term'.
#         """
#         job_offer = frappe.get_doc({
#             "doctype": "Job Offer",
#             "job_applicant": self.applicant_id,
#             "applicant_name": "Suresh Offer Test",
#             "offer_date": getdate(),
#             "designation": "Software Engineer",
#             "company": "_Test Indian Registered Company",
#             "status": "Awaiting Response",
            
#             # --- CHILD TABLE DATA ---
#             "offer_terms": [
#                 {
#                     "offer_term": "Notice Period", # Link to Master 'Offer Term'
#                     "value": "3 Month"
#                 },
#                 {
#                     "offer_term": "Annual Leave",  # Link to Master 'Offer Term'
#                     "value": "20 Days"
#                 }
#             ]
#         })
        
#         # Insert Job Offer
#         job_offer.insert()
        
#         # Permanent save to check in UI
#         # frappe.db.commit()
        
#         self.assertTrue(frappe.db.exists("Job Offer", job_offer.name))
#         print(f"\n[Job Offer Test] SUCCESS! Created ID: {job_offer.name}")

#     def tearDown(self):
#         # Database rollback
#         frappe.db.rollback()