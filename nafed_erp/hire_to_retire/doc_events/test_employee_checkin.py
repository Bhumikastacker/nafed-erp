import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days
from frappe import ValidationError

class TestEmployeeCheckin(FrappeTestCase):

    def setUp(self):
        """Set up pre-requisites."""
        self.company = "_Test Indian Registered Company"
        
        # Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "CheckinUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-CK-101",
                "first_name": "CheckinUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1212F",
                "custom_uan_number": "121212121212",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "CheckinUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_checkin_creation(self):
        """Verify standard checkin."""
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": self.test_employee,
            "time": now_datetime(),
            "log_type": "IN",
            "device_id": "BIO-001"
        })
        checkin.insert()
        self.assertTrue(frappe.db.exists("Employee Checkin", checkin.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {checkin.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_future_checkin_gap(self):
        """GAP CHECK: Future time."""
        future_time = add_days(now_datetime(), 1)
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": self.test_employee,
            "time": future_time,
            "log_type": "IN"
        })
        try:
            checkin.insert()
            print("\n[GAP FOUND] Employee Checkin allowed for a FUTURE date/time!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked future check-in.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_missing_log_type_gap(self):
        """GAP CHECK: No Log Type."""
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": self.test_employee,
            "time": now_datetime(),
            "log_type": ""
        })
        try:
            checkin.insert()
            print("[GAP FOUND] Employee Checkin allowed WITHOUT Log Type!")
        except ValidationError:
            print("[SUCCESS] System blocked check-in without log type.")

    def tearDown(self):
        frappe.db.rollback()