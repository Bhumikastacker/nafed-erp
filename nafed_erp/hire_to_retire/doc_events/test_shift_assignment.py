import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, today
from frappe import ValidationError

class TestShiftAssignment(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee and Shift Type.
        """
        self.company = "_Test Indian Registered Company"
        self.shift_type_name = "General Shift Test"

        # 1. Ensure Shift Type exists
        if not frappe.db.exists("Shift Type", self.shift_type_name):
            frappe.get_doc({
                "doctype": "Shift Type",
                "name": self.shift_type_name,
                "start_time": "09:00:00",
                "end_time": "18:00:00"
            }).insert()

        # 2. Create a dummy Employee with all mandatory custom fields
        if not frappe.db.exists("Employee", {"first_name": "ShiftUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-SH-001",
                "first_name": "ShiftUser",
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
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "ShiftUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_assignment_creation(self):
        """
        CASE 1: Verify that a valid Shift Assignment can be created.
        """
        assignment = frappe.get_doc({
            "doctype": "Shift Assignment",
            "employee": self.test_employee,        # Mandatory
            "company": self.company,               # Mandatory
            "shift_type": self.shift_type_name,    # Mandatory
            "start_date": today(),                 # Mandatory
            "status": "Active"
        })
        assignment.insert()
        self.assertTrue(frappe.db.exists("Shift Assignment", assignment.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {assignment.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_order_gap(self):
        """
        GAP CHECK: Testing if system allows 'End Date' to be before 'Start Date'.
        """
        assignment = frappe.get_doc({
            "doctype": "Shift Assignment",
            "employee": self.test_employee,
            "company": self.company,
            "shift_type": self.shift_type_name,
            "start_date": today(),
            "end_date": add_days(today(), -5) # INVALID: Ends in the past
        })

        try:
            assignment.insert()
            print("\n[GAP FOUND] Shift Assignment allowed invalid date sequence (End < Start)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_overlapping_assignment_gap(self):
        """
        GAP CHECK: Testing if system allows two overlapping shift assignments for the same employee.
        """
        # Create first assignment for a month
        frappe.get_doc({
            "doctype": "Shift Assignment",
            "employee": self.test_employee,
            "company": self.company,
            "shift_type": self.shift_type_name,
            "start_date": "2027-01-01",
            "end_date": "2027-01-31"
        }).insert()

        # Try to create another overlapping assignment
        duplicate = frappe.get_doc({
            "doctype": "Shift Assignment",
            "employee": self.test_employee,
            "company": self.company,
            "shift_type": self.shift_type_name,
            "start_date": "2027-01-15", # Overlaps
            "end_date": "2027-02-15"
        })

        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed OVERLAPPING Shift Assignments!")
        except ValidationError:
            print("[SUCCESS] System blocked overlapping assignment.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()