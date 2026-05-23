import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestLeaveEncashmentRequest(FrappeTestCase):

    def setUp(self):
        """Set up prerequisites with mandatory employee fields and high leave balance."""
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Earned Leave"
        
        # 1. Ensure Leave Type allows encashment
        if frappe.db.exists("Leave Type", self.leave_type):
            lt = frappe.get_doc("Leave Type", self.leave_type)
            lt.allow_encashment = 1
            lt.earning_component = "Basic"
            lt.save(ignore_permissions=True)

        # 2. Setup Employee with all mandatory fields
        if not frappe.db.exists("Employee", {"first_name": "EncashApproverUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-ENC-APP-01",
                "first_name": "EncashApproverUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_ppedate": "2020-01-01",
                "custom_vpf_applicable": "No",
                "custom_allotted_official_accommodation": "No"
            }).insert()
            self.test_employee = emp.name

        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "EncashApproverUser"}, "name")

        # 3. Setup High Allocation (100 Days) to bypass "max 1 day" error
        if not frappe.db.exists("Leave Allocation", {"employee": self.test_employee, "leave_type": self.leave_type, "docstatus": 1}):
            frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": self.test_employee,
                "leave_type": self.leave_type,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31",
                "new_leaves_allocated": 100,
                "company": self.company
            }).insert().submit()

        frappe.db.commit()

    def test_1_positive_encashment_creation(self):
        """Positive Case: Standard encashment request with mandatory Approver."""

        req = self.create_dummy_request(days=1, date=today()) # Using 1 day to be safe with balance
        req.insert()

        frappe.db.commit()

        self.assertTrue(frappe.db.exists("Leave Encashment Request", req.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {req.name}")

    def test_2_negative_days_gap(self):
        """GAP CHECK: Testing if system allows negative encashment days"""

        req = self.create_dummy_request(days=-10, date=today())
        try:
            req.insert()
            print("\n[GAP FOUND] System allowed NEGATIVE encashment days!")

        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative encashment days.")

    def test_3_future_request_date_gap(self):
        """GAP CHECK: Testing if system allows future request dates"""

        future_date = add_days(today(), 30)
        req = self.create_dummy_request(days=1, date=future_date)

        try:
            req.insert()
            print("[GAP FOUND] System allowed FUTURE request date!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked future request dates.")

    def create_dummy_request(self, days, date):
        """Helper to create object with mandatory Approver child table."""

        return frappe.get_doc({
            "doctype": "Leave Encashment Request",
            "company": self.company,
            "employee": self.test_employee,
            "request_date": date,
            "leave_type": self.leave_type,
            "leave_days_to_encash": days,
            
            # --- ADDING MANDATORY APPROVER TABLE ---
            "leave_encashment_request_approvers": [
                {
                    "leave_encashment_request_approvers": "Administrator" 
                }
            ]
        })

    def tearDown(self):
        frappe.db.rollback()