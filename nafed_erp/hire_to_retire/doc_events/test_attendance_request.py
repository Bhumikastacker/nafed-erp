import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestAttendanceRequest(FrappeTestCase):

    def setUp(self):
        """Set up prerequisites: Employee and Holiday List."""
        self.company = "_Test Indian Registered Company"
        holiday_list = "Attendance Test Holiday List"

        # 1. Create Holiday List
        if not frappe.db.exists("Holiday List", holiday_list):
            frappe.get_doc({
                "doctype": "Holiday List",
                "holiday_list_name": holiday_list,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31"
            }).insert()

        # 2. Setup Employee with Holiday List
        if not frappe.db.exists("Employee", {"first_name": "ReqUserOne"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-ARQ-99",
                "first_name": "ReqUserOne",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "holiday_list": holiday_list, # <--- FIXED
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            }).insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "ReqUserOne"}, "name")
            frappe.db.set_value("Employee", self.test_employee, "holiday_list", holiday_list)

        frappe.db.delete("Attendance Request", {"employee": self.test_employee})
        frappe.db.commit()

    def test_1_positive_request_creation(self):
        """CASE 1: Verify valid creation."""
        request = self.create_dummy_request(today())
        request.insert()
        self.assertTrue(frappe.db.exists("Attendance Request", request.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {request.name}")

    def test_2_wrong_date_order_gap(self):
        """CASE 2: Blocks invalid date sequence."""
        request = self.create_dummy_request(today())
        request.from_date = add_days(today(), 1)
        request.to_date = today()
        with self.assertRaises(ValidationError):
            request.insert()
        print("\n[SUCCESS] System correctly blocked invalid date order.")

    def test_3_overlap_request_gap(self):
        """GAP CHECK: Overlapping requests."""
        self.test_1_positive_request_creation()
        duplicate = self.create_dummy_request(today())
        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed OVERLAPPING Attendance Requests!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked overlapping request.")

    def create_dummy_request(self, date):
        return frappe.get_doc({
            "doctype": "Attendance Request",
            "employee": self.test_employee,
            "company": self.company,
            "from_date": date,
            "to_date": date,
            "reason": "Work From Home"
        })

    def tearDown(self):
        frappe.db.rollback()