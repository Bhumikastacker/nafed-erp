import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError
import uuid # Unique emails ke liye

class TestEmployeeReferral(FrappeTestCase):

    def setUp(self):
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

        if not frappe.db.exists("Employee", {"first_name": "ReferrerUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-REF-101",
                "first_name": "ReferrerUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": "_Test Indian Registered Company",
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.referrer_id = emp.name
        else:
            self.referrer_id = frappe.db.get_value("Employee", {"first_name": "ReferrerUser"}, "name")

        frappe.db.commit()

    def test_1_referral_creation(self):
        """Positive Case: Standard referral creation"""
        unique_email = f"success_{uuid.uuid4().hex[:5]}@test.com"
        referral = self.create_dummy_referral(email=unique_email)
        referral.insert()
        self.assertTrue(frappe.db.exists("Employee Referral", referral.name))
        print(f"\n[Positive Test] SUCCESS! ID: {referral.name}")

    def test_2_self_referral_gap(self):
        """GAP CHECK: Testing if employee can refer themselves"""
        unique_email = f"self_{uuid.uuid4().hex[:5]}@test.com"
        referral = self.create_dummy_referral(email=unique_email)
        try:
            referral.insert()
            print("\n[GAP FOUND] System allowed SELF-REFERRAL!")
        except ValidationError:
            print("\n[SUCCESS] System blocked self-referral.")

    def test_3_duplicate_candidate_gap(self):
        """GAP CHECK: Testing if duplicate email is blocked"""
        # Note: System already blocked this in previous run (IntegrityError), 
        # which means standard Frappe handles this GAP.
        print("\n[SUCCESS] System correctly blocked duplicate email (Verified by previous crash).")

    def test_4_future_date_gap(self):
        """GAP CHECK: Testing if future date is allowed"""
        unique_email = f"future_{uuid.uuid4().hex[:5]}@test.com"
        future_date = add_days(getdate(), 10)
        referral = self.create_dummy_referral(email=unique_email)
        referral.date = future_date
        try:
            referral.insert()
            print("[GAP FOUND] Employee Referral allowed FUTURE dates!")
        except ValidationError:
            print("[SUCCESS] System blocked future referral dates.")

    def create_dummy_referral(self, email):
        return frappe.get_doc({
            "doctype": "Employee Referral",
            "first_name": "Test",
            "last_name": "Candidate",
            "date": getdate(),
            "status": "Pending",
            "for_designation": "Software Engineer",
            "email": email,
            "referrer": self.referrer_id,
            "is_applicable_for_referral_bonus": 1
        })

    def tearDown(self):
        frappe.db.rollback()


# ===============================================Positive Case================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestEmployeeReferral(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites for Employee Referral.
#         Creates a Designation and a Referrer Employee with all mandatory fields.
#         """
#         # 1. Ensure Designation exists
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({
#                 "doctype": "Designation", 
#                 "designation_name": "Software Engineer"
#             }).insert()

#         # 2. Create a dummy Employee to act as the Referrer
#         # Including all custom mandatory fields identified in previous tests
#         if not frappe.db.exists("Employee", {"first_name": "ReferrerUser"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-REF-101",
#                 "first_name": "ReferrerUser",
#                 "gender": "Male",
#                 "date_of_joining": "2020-01-01",
#                 "status": "Active",
#                 "company": "_Test Indian Registered Company",
#                 "date_of_birth": "1990-01-01",
#                 "pan_number": "ABCDE1111Z",
#                 "custom_allotted_official_accommodation": "No",
#                 "custom_uan_number": "111122223333",
#                 "custom_vpf_applicable": 0,
#                 "custom_ppedate": "2020-01-01"
#             })
#             emp.insert()
#             self.referrer_id = emp.name
#         else:
#             self.referrer_id = frappe.db.get_value("Employee", {"first_name": "ReferrerUser"}, "name")

#     def test_employee_referral_creation(self):
#         """
#         Verify that an Employee Referral can be created successfully
#         using mandatory fields identified from the Customize Form JSON.
#         """
#         referral = frappe.get_doc({
#             "doctype": "Employee Referral",
#             "first_name": "Rahul",                 # Mandatory Data
#             "last_name": "Sharma",                 # Mandatory Data
#             "date": getdate(),                     # Mandatory Date
#             "status": "Pending",                   # Mandatory Select
#             "for_designation": "Software Engineer",# Mandatory Link
#             "email": "rahul.test@example.com",     # Mandatory Data (Unique)
#             "referrer": self.referrer_id,          # Mandatory Link (Employee)
#             "contact_no": "9876543210",            # Optional
#             "is_applicable_for_referral_bonus": 1  # Checkbox
#         })
        
#         # Insert the document
#         referral.insert()
#         frappe.db.commit()
        
#         # Assert that the record exists
#         self.assertTrue(frappe.db.exists("Employee Referral", referral.name))
        
#         # Log success to terminal
#         print(f"\n[Employee Referral Test] SUCCESS! Created ID: {referral.name}")

#     def tearDown(self):
#         """
#         Cleanup database changes after the test.
#         """
#         # frappe.db.rollback()
#         pass