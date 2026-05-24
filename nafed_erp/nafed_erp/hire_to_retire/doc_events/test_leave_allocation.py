import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestLeaveAllocation(FrappeTestCase):

    def setUp(self):
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Sick Leave"
        
        if not frappe.db.exists("Leave Type", self.leave_type):
            frappe.get_doc({"doctype": "Leave Type", "leave_type_name": self.leave_type}).insert()

        if not frappe.db.exists("Employee", {"first_name": "AllocUserFinal"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-AL-101",
                "first_name": "AllocUserFinal",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE8888Z",
                "custom_uan_number": "888877776666",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "AllocUserFinal"}, "name")

        # Fresh start for each test
        frappe.db.delete("Leave Allocation", {"employee": self.test_employee})
        frappe.db.commit()

    def test_1_positive_allocation_creation(self):
        """CASE 1: Sahi data ke saath allocation."""
        allocation = frappe.get_doc({
            "doctype": "Leave Allocation",
            "naming_series": "HR-LAL-.YYYY.-",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "new_leaves_allocated": 15,
            "company": self.company
        })
        allocation.insert()
        self.assertTrue(frappe.db.exists("Leave Allocation", allocation.name))

    def test_2_wrong_date_order_validation(self):
        """
        CASE 2 (Negative): Verify that system blocks when 'To Date' is before 'From Date'.
        This is a standard Frappe validation.
        """
        allocation = frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "from_date": "2026-12-31",
            "to_date": "2026-01-01", # GALAT: To Date pehle hai
            "new_leaves_allocated": 10,
            "company": self.company
        })
        
        # System MUST throw an error here
        with self.assertRaises(ValidationError):
            allocation.insert()
        
        print("\n[Negative Test] SUCCESS! System correctly blocked wrong date order.")

    def test_3_overlap_allocation_validation(self):
        """CASE 3: Ek hi period mein do allocation block honi chahiye."""
        # Pehli valid allocation
        frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "from_date": "2028-01-01",
            "to_date": "2028-12-31",
            "new_leaves_allocated": 10,
            "company": self.company
        }).insert().submit()

        # Doosri overlapping allocation
        duplicate_alloc = frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": self.test_employee,
            "leave_type": self.leave_type,
            "from_date": "2028-06-01", # Overlap
            "to_date": "2028-12-31",
            "new_leaves_allocated": 10,
            "company": self.company
        })

        with self.assertRaises(ValidationError):
            duplicate_alloc.insert()

        print("\n[Overlap Test] SUCCESS! System correctly blocked overlapping allocation.")

    def tearDown(self):
        frappe.db.rollback()


# =====================================================Wrong==================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate
# from frappe import ValidationError

# class TestLeaveAllocation(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites: Employee and Leave Type.
#         """
#         self.company = "_Test Indian Registered Company"
#         self.leave_type = "Sick Leave"

#         if not frappe.db.exists("Leave Type", self.leave_type):
#             frappe.get_doc({"doctype": "Leave Type", "leave_type_name": self.leave_type}).insert()

#         if not frappe.db.exists("Employee", {"first_name": "AllocUserFinal"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-AL-101",
#                 "first_name": "AllocUserFinal",
#                 "gender": "Male",
#                 "date_of_joining": "2023-01-01",
#                 "status": "Active",
#                 "company": self.company,
#                 "date_of_birth": "1990-01-01",
#                 "pan_number": "ABCDE8888Z",
#                 "custom_uan_number": "888877776666",
#                 "custom_vpf_applicable": "No",
#                 "custom_ppedate": "2023-01-01",
#                 "custom_allotted_official_accommodation": "No"
#             })
#             emp.insert()
#             self.test_employee = emp.name
#         else:
#             self.test_employee = frappe.db.get_value("Employee", {"first_name": "AllocUserFinal"}, "name")

#         # Cleanup existing allocations for a fresh test run
#         frappe.db.delete("Leave Allocation", {"employee": self.test_employee})
#         frappe.db.commit()

#     def test_1_positive_allocation_creation(self):
#         """
#         CASE 1 (Positive): Verify that Leave Allocation can be created and submitted.
#         """
#         allocation = frappe.get_doc({
#             "doctype": "Leave Allocation",
#             "naming_series": "HR-LAL-.YYYY.-",
#             "employee": self.test_employee,
#             "leave_type": self.leave_type,
#             "from_date": "2026-01-01",
#             "to_date": "2026-12-31",
#             "new_leaves_allocated": 15,
#             "company": self.company
#         })
#         allocation.insert()
#         allocation.submit()
        
#         self.assertEqual(allocation.docstatus, 1)
#         print(f"\n[Positive Test] SUCCESS! Allocation created: {allocation.name}")

#     def test_2_negative_leaves_validation(self):
#         """
#         CASE 2 (Negative): Verify that system blocks negative leave allocation.
#         """
#         allocation = frappe.get_doc({
#             "doctype": "Leave Allocation",
#             "employee": self.test_employee,
#             "leave_type": self.leave_type,
#             "from_date": "2027-01-01",
#             "to_date": "2027-12-31",
#             "new_leaves_allocated": -5, # WRONG DATA (Negative)
#             "company": self.company
#         })
        
#         # System should throw an error
#         with self.assertRaises(ValidationError):
#             allocation.insert()
        
#         print("\n[Negative Test] SUCCESS! System correctly blocked negative leaves.")

#     def test_3_overlap_allocation_validation(self):
#         """
#         CASE 3 (Negative): Verify that system blocks overlapping allocations for the same period.
#         """
#         # First valid allocation
#         frappe.get_doc({
#             "doctype": "Leave Allocation",
#             "employee": self.test_employee,
#             "leave_type": self.leave_type,
#             "from_date": "2028-01-01",
#             "to_date": "2028-12-31",
#             "new_leaves_allocated": 10,
#             "company": self.company
#         }).insert().submit()

#         # Second allocation on SAME DATE (Should Fail)
#         duplicate_alloc = frappe.get_doc({
#             "doctype": "Leave Allocation",
#             "employee": self.test_employee,
#             "leave_type": self.leave_type,
#             "from_date": "2028-06-01", # Overlapping date
#             "to_date": "2028-12-31",
#             "new_leaves_allocated": 10,
#             "company": self.company
#         })

#         with self.assertRaises(ValidationError):
#             duplicate_alloc.insert()

#         print("\n[Overlap Test] SUCCESS! System correctly blocked overlapping allocation.")

#     def tearDown(self):
#         frappe.db.rollback()