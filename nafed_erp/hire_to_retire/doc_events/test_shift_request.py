import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, today
from frappe import ValidationError

class TestShiftRequest(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee, Shift Type, and User (for Approver).
        """
        self.company = "_Test Indian Registered Company"
        self.shift_type = "General Shift Test"
        
        # 1. Ensure Shift Type exists
        if not frappe.db.exists("Shift Type", self.shift_type):
            frappe.get_doc({
                "doctype": "Shift Type",
                "name": self.shift_type,
                "start_time": "09:00:00",
                "end_time": "18:00:00"
            }).insert()

        # 2. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "ShiftReqUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-SR-101",
                "first_name": "ShiftReqUser",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "ShiftReqUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_request_creation(self):
        """
        CASE 1: Verify successful creation of a valid Shift Request.
        """
        request = frappe.get_doc({
            "doctype": "Shift Request",
            "employee": self.test_employee,
            "shift_type": self.shift_type,
            "company": self.company,
            "from_date": today(),
            "approver": "Administrator", # Mandatory Link (User)
            "status": "Draft"
        })
        request.insert()
        self.assertTrue(frappe.db.exists("Shift Request", request.name))
        print(f"\n[Positive Test] SUCCESS! Created Request ID: {request.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_order_gap(self):
        """
        GAP CHECK: Testing if system allows 'To Date' to be before 'From Date'.
        """
        request = frappe.get_doc({
            "doctype": "Shift Request",
            "employee": self.test_employee,
            "shift_type": self.shift_type,
            "company": self.company,
            "from_date": add_days(today(), 5), 
            "to_date": today(),               # INVALID: Ends before it starts
            "approver": "Administrator",
            "status": "Draft"
        })

        try:
            request.insert()
            print("\n[GAP FOUND] Shift Request allowed invalid date sequence (To Date < From Date)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_self_approval_gap(self):
        """
        GAP CHECK: Testing if an employee can be their own approver.
        Ideally, the requester and approver should be different people.
        """
        # Scenario: Admin requesting for themselves (if Admin is linked to an employee)
        request = frappe.get_doc({
            "doctype": "Shift Request",
            "employee": self.test_employee,
            "shift_type": self.shift_type,
            "company": self.company,
            "from_date": today(),
            "approver": frappe.session.user, # Approver is the same as the current user
            "status": "Draft"
        })

        try:
            request.insert()
            print("[GAP FOUND] System allowed an employee to set themselves as the Approver!")
        except ValidationError:
            print("[SUCCESS] System blocked self-approval.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()