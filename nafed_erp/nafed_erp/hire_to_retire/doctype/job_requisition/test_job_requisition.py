# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase

# from erpnext.setup.doctype.designation.test_designation import create_designation
# from erpnext.setup.doctype.employee.test_employee import make_employee

# from hrms.hr.doctype.job_opening.test_job_opening import get_job_opening
# from hrms.hr.doctype.job_requisition.job_requisition import make_job_opening


# class TestJobRequisition(FrappeTestCase):
# 	def setUp(self):
# 		self.employee = make_employee("test_employee_1@company.com", company="_Test Company")

# 	def test_make_job_opening(self):
# 		job_req = make_job_requisition(requested_by=self.employee)

# 		job_opening = make_job_opening(job_req.name)
# 		job_opening.status = "Closed"
# 		job_opening.save()

# 		job_req.reload()

# 		self.assertEqual(job_opening.job_requisition, job_req.name)
# 		self.assertEqual(job_req.status, "Filled")

# 	def test_associate_job_opening(self):
# 		job_req = make_job_requisition(requested_by=self.employee)
# 		job_opening = get_job_opening(company="_Test Company").insert()

# 		job_req.associate_job_opening(job_opening.name)
# 		job_opening.reload()

# 		self.assertEqual(job_opening.job_requisition, job_req.name)

# 	def test_time_to_fill(self):
# 		job_req = make_job_requisition(requested_by=self.employee)
# 		job_req.status = "Filled"
# 		job_req.completed_on = "2023-01-31"
# 		job_req.save()

# 		# 30 days from posting date to completion date = 2592000 seconds (duration field)
# 		self.assertEqual(job_req.time_to_fill, 2592000)


# def make_job_requisition(**args):
# 	frappe.db.delete("Job Requisition")
# 	args = frappe._dict(args)

# 	return frappe.get_doc(
# 		{
# 			"doctype": "Job Requisition",
# 			"designation": args.designation or create_designation().name,
# 			"department": args.department or frappe.db.get_value("Employee", args.requested_by, "department"),
# 			"no_of_positions": args.no_of_positions or 1,
# 			"expected_compensation": args.expected_compensation or 500000,
# 			"company": "_Test Company",
# 			"status": args.status or "Open & Approved",
# 			"requested_by": args.requested_by or "_Test Employee",
# 			"posting_date": args.posting_date or "2023-01-01",
# 			"expected_by": args.expected_by or "2023-01-15",
# 			"description": "Test",
# 			"reason_for_requesting": "Test",
# 		}
# 	).insert()

# ========================================================================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestJobRequisitionCustom(FrappeTestCase): 

#     def setUp(self):
#         # 1. Designation aur Department check/create 
#         if not frappe.db.exists("Designation", "Software Engineer"):
#             frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

#         if not frappe.db.exists("Department", "Dispatch"):
#             frappe.get_doc({"doctype": "Department", "department_name": "Dispatch"}).insert()

#         # 2. Create Dummy Employee (With mandatory fields)
#         if not frappe.db.exists("Employee", {"first_name": "TestUserOne"}):
#             frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-T-999",
#                 "first_name": "TestUserOne",
#                 "gender": "Male",
#                 "date_of_joining": "2020-01-01",
#                 "status": "Active",
#                 "company": "_Test Indian Registered Company",
#                 "date_of_birth": "1990-01-01",
#                 "pan_number": "ABCDE1234F",
#                 "custom_allotted_official_accommodation": "No",
#                 "custom_uan_number": "123456789012",
#                 "custom_vpf_applicable": 0,
#                 "custom_ppedate": "2020-01-01"
#             }).insert()
        
#         self.test_emp = frappe.db.get_value("Employee", {"first_name": "TestUserOne"}, "name")

#     def test_job_requisition_creation(self):
#         """Standard check for record creation"""
#         job_req = frappe.get_doc({
#             "doctype": "Job Requisition",
#             "naming_series": "HR-HIREQ-",
#             "designation": "Software Engineer",
#             "department": "Dispatch",
#             "no_of_positions": 2,
#             "expected_compensation": 600000,
#             "company": "_Test Indian Registered Company",
#             "status": "Pending",
#             "requested_by": self.test_emp,
#             "posting_date": getdate(),
#             "description": "Test Job Description"
#         })
        
#         job_req.insert()
#         # frappe.db.commit()

#         self.assertTrue(frappe.db.exists("Job Requisition", job_req.name))
#         print(f"\n[Job Requisition] SUCCESS! ID: {job_req.name}")

#     def tearDown(self):
#         frappe.db.rollback()

# =======================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate
from frappe import ValidationError

class TestJobRequisitionCustom(FrappeTestCase): 

    def setUp(self):
        # 1. Designation and Department setup
        if not frappe.db.exists("Designation", "Software Engineer"):
            frappe.get_doc({"doctype": "Designation", "designation_name": "Software Engineer"}).insert()

        if not frappe.db.exists("Department", "Dispatch"):
            frappe.get_doc({"doctype": "Department", "department_name": "Dispatch"}).insert()

        # 2. Create Dummy Employee with mandatory fields
        if not frappe.db.exists("Employee", {"first_name": "TestUserOne"}):
            frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-T-999",
                "first_name": "TestUserOne",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": "_Test Indian Registered Company",
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_allotted_official_accommodation": "No",
                "custom_uan_number": "123456789012",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01"
            }).insert()
        
        self.test_emp = frappe.db.get_value("Employee", {"first_name": "TestUserOne"}, "name")

    def test_job_requisition_creation(self):
        """Positive Case: Standard record creation"""
        job_req = frappe.get_doc({
            "doctype": "Job Requisition",
            "naming_series": "HR-HIREQ-",
            "designation": "Software Engineer",
            "department": "Dispatch",
            "no_of_positions": 2,
            "expected_compensation": 600000,
            "company": "_Test Indian Registered Company",
            "status": "Pending",
            "requested_by": self.test_emp,
            "posting_date": getdate(),
            "description": "Test Job Description"
        }).insert()
        self.assertTrue(frappe.db.exists("Job Requisition", job_req.name))
        print(f"\n[Positive Test] SUCCESS! ID: {job_req.name}")

    def test_negative_no_of_positions(self):
        """GAP CHECK: Testing if system allows negative number of positions"""
        job_req = frappe.get_doc({
            "doctype": "Job Requisition",
            "designation": "Software Engineer",
            "no_of_positions": -5, # WRONG DATA
            "expected_compensation": 500000,
            "company": "_Test Indian Registered Company",
            "status": "Pending",
            "requested_by": self.test_emp,
            "description": "Negative positions test"
        })
        
        # System should ideally throw ValidationError. If not, it's a GAP.
        try:
            job_req.insert()
            print("\n[GAP FOUND] Job Requisition allowed NEGATIVE no_of_positions!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative positions.")

    def test_negative_compensation(self):
        """GAP CHECK: Testing if system allows negative expected compensation"""
        job_req = frappe.get_doc({
            "doctype": "Job Requisition",
            "designation": "Software Engineer",
            "no_of_positions": 1,
            "expected_compensation": -10000, # WRONG DATA
            "company": "_Test Indian Registered Company",
            "status": "Pending",
            "requested_by": self.test_emp,
            "description": "Negative compensation test"
        })

        try:
            job_req.insert()
            print("[GAP FOUND] Job Requisition allowed NEGATIVE expected_compensation!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked negative compensation.")

    def tearDown(self):
        frappe.db.rollback()