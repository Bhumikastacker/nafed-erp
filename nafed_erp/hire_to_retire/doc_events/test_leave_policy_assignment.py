import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestLeavePolicyAssignment(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee, Leave Type, and Leave Policy.
        Captures the actual database ID of the policy to avoid Link errors.
        """
        self.company = "_Test Indian Registered Company"
        self.leave_type = "Annual Leave"
        self.policy_title = "Standard Policy Test"
        
        # 1. Setup Employee
        if not frappe.db.exists("Employee", {"first_name": "PolicyUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-POL-101",
                "first_name": "PolicyUser",
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
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "PolicyUser"}, "name")

        # 2. Setup Leave Type
        if not frappe.db.exists("Leave Type", self.leave_type):
            frappe.get_doc({"doctype": "Leave Type", "leave_type_name": self.leave_type}).insert()

        # 3. Setup Leave Policy and Get ACTUAL ID (Fix: Using 'title' field)
        existing_policy = frappe.db.get_value("Leave Policy", {"title": self.policy_title}, "name")
        
        if not existing_policy:
            policy = frappe.get_doc({
                "doctype": "Leave Policy",
                "title": self.policy_title, # Backend fieldname is 'title'
                "leave_policy_details": [
                    {
                        "leave_type": self.leave_type, 
                        "annual_allocation": 12
                    }
                ]
            })
            policy.insert()
            self.policy_id = policy.name 
        else:
            self.policy_id = existing_policy

        frappe.db.commit()

    def test_1_positive_assignment_creation(self):
        """Positive Case: Successfully assign a policy to an employee."""
        assignment = frappe.get_doc({
            "doctype": "Leave Policy Assignment",
            "employee": self.test_employee,
            "leave_policy": self.policy_id,
            "effective_from": "2026-01-01",
            "effective_to": "2026-12-31"
        })
        assignment.insert()
        self.assertTrue(frappe.db.exists("Leave Policy Assignment", assignment.name))
        print(f"\n[Positive Test] SUCCESS! ID: {assignment.name}")

    def test_2_invalid_date_order_gap(self):
        """GAP CHECK: Verify if system blocks invalid date sequence."""
        assignment = frappe.get_doc({
            "doctype": "Leave Policy Assignment",
            "employee": self.test_employee,
            "leave_policy": self.policy_id,
            "effective_from": "2026-12-31",
            "effective_to": "2026-01-01"
        })
        try:
            assignment.insert()
            print("\n[GAP FOUND] System allowed invalid date order!")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid date order.")

    def test_3_overlapping_assignment_gap(self):
        """GAP CHECK: Verify if system blocks overlapping policy assignments."""
        # Create first assignment
        frappe.get_doc({
            "doctype": "Leave Policy Assignment",
            "employee": self.test_employee,
            "leave_policy": self.policy_id,
            "effective_from": "2027-01-01",
            "effective_to": "2027-12-31"
        }).insert()

        # Try to overlap
        duplicate = frappe.get_doc({
            "doctype": "Leave Policy Assignment",
            "employee": self.test_employee,
            "leave_policy": self.policy_id,
            "effective_from": "2027-06-01", 
            "effective_to": "2027-12-31"
        })
        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed OVERLAPPING Policy Assignments!")
        except ValidationError:
            print("[SUCCESS] System blocked overlapping policy.")

    def tearDown(self):
        frappe.db.rollback()