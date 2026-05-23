import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestCompensatoryLeaveRequest(FrappeTestCase):

    def setUp(self):
        """
        Setup: Holiday List, Employee, Attendance and Leave Allocation.
        """
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Compensatory Off"
        self.admin_user = "Administrator"
        self.holiday_date = "2026-03-15"
        holiday_list_name = "COFF Holiday List 2026"

        # Holiday List
        if not frappe.db.exists("Holiday List", holiday_list_name):
            frappe.get_doc({
                "doctype": "Holiday List",
                "holiday_list_name": holiday_list_name,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31"
            }).insert()

        hl = frappe.get_doc("Holiday List", holiday_list_name)

        if not any(h.holiday_date == getdate(self.holiday_date) for h in hl.holidays):
            hl.append("holidays", {
                "holiday_date": self.holiday_date,
                "description": "Sunday Holiday"
            })
            hl.save()

        # Employee
        if not frappe.db.exists("Employee", {"employee_number": "EMP-COFF-V4"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-COFF-V4",
                "first_name": "CompUserFinalV4",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "holiday_list": holiday_list_name,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE2222Z",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No",
                "custom_leave_approvers": [{
                    "leave_type": self.leave_type,
                    "leave_approver": self.admin_user,
                    "second_approver": self.admin_user,
                    "third_approver": self.admin_user
                }]
            }).insert()

            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value(
                "Employee",
                {"employee_number": "EMP-COFF-V4"},
                "name"
            )

        # Attendance on Holiday
        if not frappe.db.exists("Attendance", {
            "employee": self.test_employee,
            "attendance_date": self.holiday_date
        }):
            att = frappe.get_doc({
                "doctype": "Attendance",
                "employee": self.test_employee,
                "attendance_date": self.holiday_date,
                "status": "Present",
                "company": self.company
            })
            att.insert(ignore_permissions=True)
            att.submit()

        # Leave Allocation
        if not frappe.db.exists("Leave Allocation", {
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "docstatus": 1
        }):
            allocation = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": self.test_employee,
                "leave_type": self.leave_type,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31",
                "new_leaves_allocated": 10,
                "company": self.company
            })

            allocation.insert()
            allocation.submit()

        frappe.db.commit()

    # ----------------------------------------------------

    def test_1_positive_coff_creation(self):
        """CASE 1: Valid compensatory leave request."""

        comp = self.create_coff(self.holiday_date, self.holiday_date)

        comp.insert()

        self.assertTrue(
            frappe.db.exists("Compensatory Leave Request", comp.name)
        )

        print(f"\n[Positive Test] SUCCESS! ID: {comp.name}")

    # ----------------------------------------------------

    def test_2_non_holiday_gap(self):
        """
        GAP CHECK:
        COFF should only be allowed if employee worked on a holiday.
        """

        normal_day = add_days(self.holiday_date, 1)

        comp = self.create_coff(normal_day, normal_day)

        try:
            comp.insert()
            print("\n[GAP FOUND] System allowed COFF for non-holiday work date!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked non-holiday COFF request.")

    # ----------------------------------------------------

    def test_3_duplicate_coff_gap(self):
        """
        GAP CHECK:
        Same employee should not create multiple COFF for same date.
        """

        self.create_coff(self.holiday_date, self.holiday_date).insert()

        duplicate = self.create_coff(self.holiday_date, self.holiday_date)

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed duplicate COFF request!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked duplicate COFF request.")

    # ----------------------------------------------------

    def create_coff(self, from_date, to_date):
        """Helper function"""

        return frappe.get_doc({
            "doctype": "Compensatory Leave Request",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "work_from_date": from_date,
            "work_end_date": to_date,
            "reason": "Holiday support work",
            "half_day": 0
        })

    def tearDown(self):
        frappe.db.rollback()




# ========================================Positive Case========================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestCompensatoryLeaveRequest(FrappeTestCase):

#     def setUp(self):
#         """
#         Setup: Holiday List, Employee, Submitted Attendance and Allocation.
#         """
#         company_name = "_Test Indian Registered Company"
#         holiday_list_name = "COFF Holiday List 2026"
#         leave_type_name = "Compensatory Off"
#         admin_user = "Administrator"
#         self.holiday_date = "2026-03-15" 

#         # 1. Holiday List
#         if not frappe.db.exists("Holiday List", holiday_list_name):
#             hl = frappe.get_doc({
#                 "doctype": "Holiday List",
#                 "holiday_list_name": holiday_list_name,
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31"
#             }).insert()
        
#         hl = frappe.get_doc("Holiday List", holiday_list_name)
#         if not any(h.holiday_date == getdate(self.holiday_date) for h in hl.holidays):
#             hl.append("holidays", {"holiday_date": self.holiday_date, "description": "Sunday Holiday"})
#             hl.save()
        
#         # 2. Salutation
#         if not frappe.db.exists("Salutation", "Mr."):
#             frappe.get_doc({"doctype": "Salutation", "salutation": "Mr."}).insert()

#         # 3. Create dummy Employee (V3 to be safe)
#         if not frappe.db.exists("Employee", {"first_name": "CompUserFinalV3"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-COFF-V3",
#                 "first_name": "CompUserFinalV3",
#                 "gender": "Male",
#                 "date_of_joining": "2023-01-01",
#                 "status": "Active",
#                 "company": company_name,
#                 "holiday_list": holiday_list_name,
#                 "salutation": "Mr.",
#                 "date_of_birth": "1990-01-01",
#                 "pan_number": "ABCDE1111Z",
#                 "custom_uan_number": "111122223333",
#                 "custom_vpf_applicable": "No",
#                 "custom_ppedate": "2023-01-01",
#                 "custom_allotted_official_accommodation": "No",
#                 "custom_leave_approvers": [
#                     {
#                         "leave_type": leave_type_name,
#                         "leave_approver": admin_user,
#                         "second_approver": admin_user,
#                         "third_approver": admin_user
#                     }
#                 ]
#             }).insert()
#             self.test_employee = emp.name
#         else:
#             self.test_employee = frappe.db.get_value("Employee", {"first_name": "CompUserFinalV3"}, "name")

#         # 4. Create & Submit Attendance
#         if not frappe.db.exists("Attendance", {"employee": self.test_employee, "attendance_date": self.holiday_date}):
#             attendance = frappe.get_doc({
#                 "doctype": "Attendance",
#                 "employee": self.test_employee,
#                 "attendance_date": self.holiday_date,
#                 "status": "Present",
#                 "company": company_name
#             })
#             attendance.insert(ignore_permissions=True)
#             attendance.submit()

#         # 5. Create Leave Allocation (Submitted)
#         if not frappe.db.exists("Leave Allocation", {"employee": self.test_employee, "leave_type": leave_type_name, "docstatus": 1}):
#             allocation = frappe.get_doc({
#                 "doctype": "Leave Allocation",
#                 "employee": self.test_employee,
#                 "leave_type": leave_type_name,
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31",
#                 "new_leaves_allocated": 10,
#                 "company": company_name
#             })
#             allocation.insert()
#             allocation.submit()

#         frappe.db.commit()

#     def test_compensatory_leave_request_creation(self):
#         """
#         Verify COFF creation including the mandatory Leave Type field.
#         """
#         comp_request = frappe.get_doc({
#             "doctype": "Compensatory Leave Request",
#             "employee": self.test_employee,
#             "leave_type": "Compensatory Off", # <--- YE MANDATORY FIELD ADD KI HAI
#             "work_from_date": self.holiday_date, 
#             "work_end_date": self.holiday_date,
#             "reason": "Holiday work support.",
#             "half_day": 0
#         })
        
#         comp_request.insert()
#         frappe.db.commit()
        
#         self.assertTrue(frappe.db.exists("Compensatory Leave Request", comp_request.name))
#         print(f"\n[Compensatory Leave Test] SUCCESS! Created ID: {comp_request.name}")

#     def tearDown(self):
#         pass