import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestAttendanceCustom(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Create a dummy Employee with all mandatory fields.
        """
        self.company = "_Test Indian Registered Company"
        
        # Create a fresh dummy employee to avoid ledger/overlap issues
        if not frappe.db.exists("Employee", {"first_name": "AttendanceUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-ATT-999",
                "first_name": "AttendanceUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "AttendanceUser"}, "name")

        # Cleanup existing attendance for this employee for a clean test run
        frappe.db.delete("Attendance", {"employee": self.test_employee})
        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_attendance_creation(self):
        """
        CASE 1: Verify successful creation of a standard Attendance record.
        """
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "naming_series": "HR-ATT-.YYYY.-",
            "employee": self.test_employee,
            "attendance_date": today(),
            "status": "Present",
            "company": self.company
        })
        attendance.insert()
        self.assertTrue(frappe.db.exists("Attendance", attendance.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {attendance.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_duplicate_attendance_gap(self):
        """
        GAP CHECK: Testing if system allows two attendance records for the same employee on the same date.
        """
        # First creation for today
        self.test_1_positive_attendance_creation()

        # Attempt to create SECOND attendance for the SAME DATE
        duplicate = frappe.get_doc({
            "doctype": "Attendance",
            "naming_series": "HR-ATT-.YYYY.-",
            "employee": self.test_employee,
            "attendance_date": today(),
            "status": "Present",
            "company": self.company
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE attendance for the same day!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked duplicate attendance.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_future_attendance_gap(self):
        """
        GAP CHECK: Testing if system allows attendance for a FUTURE date.
        Ideally, one cannot be 'Present' tomorrow, today.
        """
        future_date = add_days(today(), 5) # 5 days in future
        
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "naming_series": "HR-ATT-.YYYY.-",
            "employee": self.test_employee,
            "attendance_date": future_date,
            "status": "Present",
            "company": self.company
        })

        try:
            attendance.insert()
            print("[GAP FOUND] System allowed FUTURE date attendance!")
        except ValidationError:
            print("[SUCCESS] System blocked future date attendance.")

    def tearDown(self):
        """
        Rollback changes to maintain a clean database.
        """
        frappe.db.rollback()