import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError
import uuid  # For unique IDs


class TestEmployeeCustom(FrappeTestCase):

    def setUp(self):
        self.company = "_Test Indian Registered Company"

        # Ensure 'Male' gender exists
        if not frappe.db.exists("Gender", "Male"):
            frappe.get_doc({"doctype": "Gender", "gender": "Male"}).insert()

    def test_1_positive_employee_creation(self):
        """Create a unique employee with valid data."""

        unique_id = f"EMP-{uuid.uuid4().hex[:5]}"
        employee = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "Test",
            "last_name": f"User {unique_id}",
            "employee_number": unique_id,
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "status": "Active",
            "company": self.company,
            "date_of_joining": "2024-01-01",
            "pan_number": "ABCDE1234F",
            "custom_uan_number": "123456789012",
            "custom_vpf_applicable": "No",
            "custom_ppedate": "2024-06-01",
            "custom_allotted_official_accommodation": "No"
        })

        employee.insert()
        self.assertTrue(frappe.db.exists("Employee", employee.name))
        print(f"[Positive Test] SUCCESS! Created ID: {employee.name}")

    def test_2_pan_length_gap(self):
        """Check invalid PAN length."""

        employee = self.create_dummy_employee_doc()
        employee.pan_number = "ABC12"  # Invalid
        try:
            employee.insert()
            print("[GAP FOUND] Employee allowed INVALID PAN length!")

        except ValidationError:
            print("[SUCCESS] System blocked invalid PAN.")

    def test_3_uan_length_gap(self):
        """Check invalid UAN length."""

        employee = self.create_dummy_employee_doc()
        employee.custom_uan_number = "123"  # Invalid

        try:
            employee.insert()
            print("[GAP FOUND] Employee allowed INVALID UAN length!")

        except ValidationError:
            print("[SUCCESS] System blocked invalid UAN.")

    def test_4_future_dob_gap(self):
        """Check future Date of Birth."""

        employee = self.create_dummy_employee_doc()
        employee.date_of_birth = add_days(today(), 365)  # Future DOB

        try:
            employee.insert()
            print("[GAP FOUND] Employee allowed FUTURE DOB!")

        except ValidationError:
            print("[SUCCESS] System blocked future DOB.")

    def create_dummy_employee_doc(self):
        """Helper to create a base employee document."""
        
        unique_id = f"GAP-{uuid.uuid4().hex[:5]}"
        return frappe.get_doc({
            "doctype": "Employee",
            "first_name": "GapUser",
            "employee_number": unique_id,
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "status": "Active",
            "company": self.company,
            "date_of_joining": "2024-01-01",
            "pan_number": "ABCDE1234F",
            "custom_uan_number": "123456789012",
            "custom_vpf_applicable": "No",
            "custom_ppedate": "2024-01-01",
            "custom_allotted_official_accommodation": "No"
        })

    def tearDown(self):
        """Rollback database changes after each test."""
        frappe.db.rollback()