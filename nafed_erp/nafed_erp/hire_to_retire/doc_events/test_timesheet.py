import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days, today, add_to_date
from frappe import ValidationError

class TestTimesheet(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee and Activity Type.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure Activity Type exists
        if not frappe.db.exists("Activity Type", "Internal Work"):
            frappe.get_doc({
                "doctype": "Activity Type",
                "activity_type": "Internal Work"
            }).insert()

        # 2. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "TimeUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-TS-101",
                "first_name": "TimeUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "company": self.company,
                "status": "Active"
            })
            emp.insert(ignore_mandatory=True)
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "TimeUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_timesheet_creation(self):
        """
        CASE 1: Verify successful creation of a valid Timesheet.
        """
        ts = frappe.get_doc({
            "doctype": "Timesheet",
            "naming_series": "TS-.YYYY.-",
            "employee": self.test_employee,
            "company": self.company,
            "time_logs": [
                {
                    "activity_type": "Internal Work",
                    "from_time": now_datetime(),
                    "to_time": add_to_date(now_datetime(), hours=2),
                    "description": "Completing unit testing task"
                }
            ]
        })
        ts.insert()
        self.assertTrue(frappe.db.exists("Timesheet", ts.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {ts.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_hours_gap(self):
        """
        GAP CHECK: Testing if system allows negative working hours.
        Logically, work duration cannot be negative.
        """
        ts = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": self.test_employee,
            "time_logs": [
                {
                    "activity_type": "Internal Work",
                    "from_time": now_datetime(),
                    "to_time": add_to_date(now_datetime(), hours=-5), # INVALID: End time before start
                    "hours": -5
                }
            ]
        })

        try:
            ts.insert()
            print("\n[GAP FOUND] Timesheet allowed NEGATIVE working hours!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked negative hours.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_overlapping_logs_gap(self):
        """
        GAP CHECK: Testing if system allows overlapping time logs for the same employee.
        An employee cannot work on two different tasks at the exact same time.
        """
        start_time = now_datetime()
        end_time = add_to_date(start_time, hours=1)

        # Create first valid log
        self.test_1_positive_timesheet_creation()

        # Try to create another timesheet with the SAME overlapping time
        duplicate = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": self.test_employee,
            "time_logs": [
                {
                    "activity_type": "Internal Work",
                    "from_time": start_time,
                    "to_time": end_time
                }
            ]
        })

        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed OVERLAPPING time logs for the same employee!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked overlapping logs.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()