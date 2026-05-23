import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestShiftScheduleAssignment(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee, Shift Type, and Shift Schedule.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure Shift Type exists
        if not frappe.db.exists("Shift Type", "Morning Shift"):
            frappe.get_doc({
                "doctype": "Shift Type",
                "name": "Morning Shift",
                "start_time": "09:00:00",
                "end_time": "18:00:00"
            }).insert()

        # 2. Ensure Shift Schedule exists
        if not frappe.db.exists("Shift Schedule", "Weekly Roster"):
            frappe.get_doc({
                "doctype": "Shift Schedule",
                "name": "Weekly Roster",
                "shift_type": "Morning Shift",
                "frequency": "Every Week",
                "repeat_on_days": [{"day": "Monday"}, {"day": "Tuesday"}]
            }).insert()

        # 3. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "ScheduleUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-SHSA-01",
                "first_name": "ScheduleUser",
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
            }).insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "ScheduleUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_assignment_creation(self):
        """
        CASE 1: Verify successful creation of Shift Schedule Assignment.
        """
        assignment = frappe.get_doc({
            "doctype": "Shift Schedule Assignment",
            "employee": self.test_employee,
            "company": self.company,
            "shift_schedule": "Weekly Roster",
            "enabled": 1,
            "create_shifts_after": today()
        })
        assignment.insert()
        self.assertTrue(frappe.db.exists("Shift Schedule Assignment", assignment.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {assignment.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_duplicate_assignment_gap(self):
        """
        GAP CHECK: Testing if system allows two active schedule assignments 
        for the same employee.
        """
        # First assignment
        self.test_1_positive_assignment_creation()

        # Try to create another active assignment for SAME employee
        duplicate = frappe.get_doc({
            "doctype": "Shift Schedule Assignment",
            "employee": self.test_employee,
            "company": self.company,
            "shift_schedule": "Weekly Roster",
            "enabled": 1,
            "create_shifts_after": add_days(today(), 1)
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE active Shift Schedule Assignments!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked duplicate assignment.")

    def tearDown(self):
        frappe.db.rollback()