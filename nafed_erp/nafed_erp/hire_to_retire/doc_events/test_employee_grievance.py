import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError, MandatoryError

class TestEmployeeGrievance(FrappeTestCase):

    def setUp(self):
        """
        Set up: Employee aur Grievance Type ko robust tarike se handle karein.
        """
        self.emp_name = "Test Grievance User"
        self.grievance_type = "Workplace Environment"
        
        # 1. Check karein agar Employee pehle se hai (By Name)
        existing_emp = frappe.db.exists("Employee", {"employee_name": self.emp_name})
        
        if not existing_emp:
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "99999",
                "first_name": "Test",
                "last_name": "User",
                "employee_name": self.emp_name,
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "company": "_Test Indian Registered Company",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.insert(ignore_permissions=True)
            self.employee = emp.name
        else:
            self.employee = existing_emp

        # 2. Ensure Grievance Type exists
        if not frappe.db.exists("Grievance Type", self.grievance_type):
            frappe.get_doc({
                "doctype": "Grievance Type",
                "name": self.grievance_type,
                "description": "Issues related to the office environment."
            }).insert(ignore_permissions=True)

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_grievance_creation(self):
        """
        CASE 1: Sahi data ke sath creation.
        """
        grievance = frappe.get_doc({
            "doctype": "Employee Grievance",
            "subject": "Testing noise issues",
            "raised_by": self.employee,
            "date": today(),
            "status": "Open",
            "grievance_against_party": "Employee",
            "grievance_against": self.employee,
            "grievance_type": self.grievance_type,
            "description": "It's too loud in the office."
        })
        grievance.insert()
        self.assertTrue(frappe.db.exists("Employee Grievance", grievance.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {grievance.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_future_date_gap(self):
        """
        GAP CHECK: Future date validation.
        """
        future_date = add_days(today(), 10)
        grievance = frappe.get_doc({
            "doctype": "Employee Grievance",
            "subject": "Future Date Problem",
            "raised_by": self.employee,
            "date": future_date, 
            "status": "Open",
            "grievance_against_party": "Employee",
            "grievance_against": self.employee,
            "grievance_type": self.grievance_type,
            "description": "Testing future date gap."
        })

        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed FUTURE date!"):
            grievance.insert()

    # ------------------------
    # Logic/Mandatory Gap Check
    # ------------------------
    def test_3_resolution_details_gap(self):
        """
        LOGIC CHECK: Status 'Resolved' ke waqt details mandatory honi chahiye.
        """
        grievance = frappe.get_doc({
            "doctype": "Employee Grievance",
            "subject": "Resolution Gap Test",
            "raised_by": self.employee,
            "date": today(),
            "status": "Resolved", 
            "grievance_against_party": "Employee",
            "grievance_against": self.employee,
            "grievance_type": self.grievance_type,
            "description": "Resolution detail missing check."
        })

        try:
            grievance.insert()
            if not grievance.get("resolution_detail"):
                print("\n[GAP FOUND] System allowed 'Resolved' status without Details!")
        except (MandatoryError, ValidationError):
            print("\n[SUCCESS] System correctly blocked 'Resolved' status.")

    def tearDown(self):
        frappe.db.rollback()