import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestLeaveApplication(FrappeTestCase):

    def setUp(self):
        """Set up prerequisites with all mandatory employee fields."""
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Medical Leave"
        
        # 1. Setup Holiday List
        if not frappe.db.exists("Holiday List", "Test HL"):
            frappe.get_doc({
                "doctype": "Holiday List", 
                "holiday_list_name": "Test HL", 
                "from_date": "2026-01-01", 
                "to_date": "2026-12-31"
            }).insert()

        # 2. Setup Employee with ALL Mandatory Fields
        if not frappe.db.exists("Employee", {"first_name": "LeaveGapUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-L-GAP-99",
                "first_name": "LeaveGapUser",
                "gender": "Female",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "holiday_list": "Test HL",
                "date_of_birth": "1990-01-01",
                "custom_vpf_applicable": "No",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "123456789012",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No",
                "custom_leave_approvers": [{
                    "leave_type": self.leave_type, 
                    "leave_approver": "Administrator", 
                    "second_approver": "Administrator", 
                    "third_approver": "Administrator"
                }]
            }).insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "LeaveGapUser"}, "name")

        # 3. Setup Allocation (15 Days)
        if not frappe.db.exists("Leave Allocation", {"employee": self.test_employee, "leave_type": self.leave_type, "docstatus": 1}):
            frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": self.test_employee,
                "leave_type": self.leave_type,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31",
                "new_leaves_allocated": 15,
                "company": self.company
            }).insert().submit()
        
        frappe.db.commit()

    def test_1_positive_leave_creation(self):
        """Positive Case: Standard leave application"""
        leave = self.create_dummy_leave(add_days(getdate(), 1), add_days(getdate(), 2))
        leave.insert()
        self.assertTrue(frappe.db.exists("Leave Application", leave.name))
        print(f"\n[Positive Test] SUCCESS! ID: {leave.name}")

    def test_2_overlap_leave_gap(self):
        """GAP CHECK: Testing if two leave applications can overlap"""
        start = add_days(getdate(), 10)
        end = add_days(getdate(), 12)
        self.create_dummy_leave(start, end).insert()
        
        duplicate = self.create_dummy_leave(start, end)
        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed OVERLAPPING leave applications!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked overlapping leaves.")

    def test_3_over_balance_gap(self):
        """GAP CHECK: Testing if employee can apply for more leaves than balance"""
        # Applying for 50 days when balance is only 15
        leave = self.create_dummy_leave("2026-04-01", "2026-05-20")
        try:
            leave.insert()
            print("[GAP FOUND] System allowed leave exceeding available BALANCE!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked leave exceeding balance.")

    def create_dummy_leave(self, from_date, to_date):
        return frappe.get_doc({
            "doctype": "Leave Application",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "company": self.company,
            "status": "Leave Requested",
            "leave_approver": "Administrator"
        })

    def tearDown(self):
        frappe.db.rollback()



# ============================================Positive Case====================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate, add_days

# class TestLeaveApplication(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites: Holiday List, Employee (with 3-level Approvers), 
#         Leave Type, and Allocation.
#         """
#         company_name = "_Test Indian Registered Company"
#         holiday_list_name = "Test Holiday List 2026"
#         leave_type_name = "Medical Leave"
#         admin_user = "Administrator"

#         # 1. Create a dummy Holiday List
#         if not frappe.db.exists("Holiday List", holiday_list_name):
#             frappe.get_doc({
#                 "doctype": "Holiday List",
#                 "holiday_list_name": holiday_list_name,
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31"
#             }).insert()

#         # 2. Create a dummy Leave Type
#         if not frappe.db.exists("Leave Type", leave_type_name):
#             frappe.get_doc({
#                 "doctype": "Leave Type",
#                 "leave_type_name": leave_type_name
#             }).insert()

#         # 3. Create dummy Employee with 3-LEVEL APPROVERS (Fix for MandatoryError)
#         if not frappe.db.exists("Employee", {"first_name": "NewLeaveUser"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-LEAVE-01",
#                 "first_name": "NewLeaveUser",
#                 "gender": "Female",
#                 "date_of_joining": "2023-01-01",
#                 "status": "Active",
#                 "company": company_name,
#                 "holiday_list": holiday_list_name,
#                 "date_of_birth": "1996-01-01",
#                 "pan_number": "ABCDE5555Z",
#                 "custom_uan_number": "555544443333",
#                 "custom_vpf_applicable": "No",
#                 "custom_ppedate": "2023-01-01",
#                 "custom_allotted_official_accommodation": "No",
#                 # --- CHILD TABLE: custom_leave_approvers (Adding all 3 levels) ---
#                 "custom_leave_approvers": [
#                     {
#                         "leave_type": leave_type_name,
#                         "leave_approver": admin_user,   # Level 1
#                         "second_approver": admin_user,  # Level 2 (Mandatory)
#                         "third_approver": admin_user,   # Level 3 (Mandatory)
#                         "upto_days": 100
#                     }
#                 ]
#             })
#             emp.insert()
#             self.test_employee = emp.name
#         else:
#             self.test_employee = frappe.db.get_value("Employee", {"first_name": "NewLeaveUser"}, "name")
#             # Ensure existing record is updated with 3 approvers if empty
#             emp_doc = frappe.get_doc("Employee", self.test_employee)
#             if not emp_doc.get("custom_leave_approvers"):
#                 emp_doc.append("custom_leave_approvers", {
#                     "leave_type": leave_type_name,
#                     "leave_approver": admin_user,
#                     "second_approver": admin_user,
#                     "third_approver": admin_user
#                 })
#                 emp_doc.save()

#         # 4. Create Leave Allocation (Submitted)
#         if not frappe.db.exists("Leave Allocation", {"employee": self.test_employee, "leave_type": leave_type_name, "docstatus": 1}):
#             allocation = frappe.get_doc({
#                 "doctype": "Leave Allocation",
#                 "employee": self.test_employee,
#                 "leave_type": leave_type_name,
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31",
#                 "new_leaves_allocated": 15,
#                 "company": company_name
#             })
#             allocation.insert()
#             allocation.submit()

#         frappe.db.commit()

#     def test_leave_application_creation(self):
#         """
#         Verify Leave Application creation with multi-level approvers logic.
#         """
#         leave_app = frappe.get_doc({
#             "doctype": "Leave Application",
#             "naming_series": "HR-LAP-.YYYY.-",
#             "employee": self.test_employee,
#             "leave_type": "Medical Leave",
#             "from_date": "2026-03-20",
#             "to_date": "2026-03-21",
#             "company": "_Test Indian Registered Company",
#             "posting_date": getdate(),
#             "status": "Leave Requested",
#             "leave_approver": "Administrator" 
#         })
        
#         # Insert the record
#         leave_app.insert()
#         frappe.db.commit()
        
#         # Verify
#         self.assertTrue(frappe.db.exists("Leave Application", leave_app.name))
#         print(f"\n[Leave Application Test] SUCCESS! Created ID: {leave_app.name}")

#     def tearDown(self):
#         # frappe.db.rollback()
#         pass