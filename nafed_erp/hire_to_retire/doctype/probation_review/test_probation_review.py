# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# # import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestProbationReview(FrappeTestCase):
# 	pass



import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, today
from frappe import ValidationError

class TestProbationReview(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee and Checklist Template.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Create a dummy Employee for probation
        if not frappe.db.exists("Employee", {"first_name": "ProbationUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-PROB-001",
                "first_name": "ProbationUser",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "status": "Active",
                "company": self.company,
                "custom_ppedate": "2024-06-01", # Probation end date
                "date_of_birth": "1995-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"first_name": "ProbationUser"}, "name")

        # 2. Ensure a Probation Checklist Template exists
        if not frappe.db.exists("Probation Checklist Template", "Standard Review Template"):
            frappe.get_doc({
                "doctype": "Probation Checklist Template",
                "probation_review_template_title": "Standard Review Template",
                "probation_review": [{"check_list": "Initial Performance Check"}]
            }).insert()

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_probation_review_creation(self):
        """
        CASE 1: Verify successful creation of Probation Review.
        """
        review = frappe.get_doc({
            "doctype": "Probation Review",
            "employee_id": self.employee,
            "recommendation": "Probation Confirmed",
            "probation_start_date": "2024-01-01",
            "confirmation_date": "2024-06-01",
            "probhation_checklist_template": "Standard Review Template"
        })
        review.insert()
        self.assertTrue(frappe.db.exists("Probation Review", review.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {review.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_confirmation_before_start_gap(self):
        """
        GAP CHECK: Testing if Confirmation Date can be BEFORE Probation Start Date.
        """
        review = frappe.get_doc({
            "doctype": "Probation Review",
            "employee_id": self.employee,
            "recommendation": "Probation Confirmed",
            "probation_start_date": "2024-06-01",
            "confirmation_date": "2024-01-01" # INVALID: Confirmed before starting
        })

        try:
            review.insert()
            print("\n[GAP FOUND] System allowed Confirmation Date BEFORE Probation Start Date!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date sequence.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_empty_remarks_on_extension_gap(self):
        """
        GAP CHECK: Testing if system allows 'Extended' recommendation without Manager Comments.
        """
        review = frappe.get_doc({
            "doctype": "Probation Review",
            "employee_id": self.employee,
            "recommendation": "Extended",
            "probation_start_date": "2024-01-01",
            "extension_duration": "2024-09-01",
            "manager_comments": "" # INVALID: Should be mandatory if extended
        })

        try:
            review.insert()
            print("[GAP FOUND] System allowed Probation Extension WITHOUT Manager Comments!")
        except ValidationError:
            print("[SUCCESS] System blocked extension without comments.")

    def tearDown(self):
        """
        Cleanup database.
        """
        frappe.db.rollback()