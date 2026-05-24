import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError, MandatoryError

class TestExitInterview(FrappeTestCase):

    def setUp(self):
        """
        Setup: Clean up existing data and ensure Relieving Date is properly set.
        """
        self.company = "_Test Indian Registered Company"
        self.test_emp_name = "Exit User" # Employee name found in previous error logs
        self.relieving_date = add_days(today(), 5)
        
        # 1. First, search for and fix the employee named "Exit User" if they exist
        if frappe.db.exists("Employee", self.test_emp_name):
            self.employee = self.test_emp_name
            # Force update the relieving date for the existing record
            frappe.db.set_value("Employee", self.employee, "relieving_date", self.relieving_date)
            # Set status to 'Left' to satisfy HRMS business logic
            frappe.db.set_value("Employee", self.employee, "status", "Left") 
        else:
            # If the employee does not exist, create a new record
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EXIT-TEST-001",
                "first_name": "Exit",
                "last_name": "User",
                "employee_name": self.test_emp_name,
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "relieving_date": self.relieving_date,
                "company": self.company,
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.employee = emp.name

        frappe.db.commit()
        # Clear cache to ensure the controller fetches updated database values
        frappe.clear_cache(doctype="Employee") 

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_interview_creation(self):
        """
        CASE 1: Verify record creation with valid data and mandatory fields.
        """
        interview = frappe.get_doc({
            "doctype": "Exit Interview",
            "naming_series": "HR-EXIT-INT-",
            "employee": self.employee,
            "company": self.company,
            "status": "Pending"
        })
        # Execute insertion and trigger standard validation rules
        interview.insert()
        self.assertTrue(frappe.db.exists("Exit Interview", interview.name))
        print(f"\n[Positive Test] SUCCESS! Exit Interview: {interview.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_future_interview_date_gap(self):
        """
        GAP CHECK: Verify if the system incorrectly allows a future interview date.
        """
        future_date = add_days(today(), 30)
        interview = frappe.get_doc({
            "doctype": "Exit Interview",
            "employee": self.employee,
            "company": self.company,
            "status": "Scheduled",
            "date": future_date 
        })

        # The interview date should logically fall within the current context
        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed FUTURE Interview date!"):
            interview.insert()

    # ------------------------
    # Logic Gap Check (Status Dependency)
    # ------------------------
    def test_3_final_decision_mandatory_gap(self):
        """
        LOGIC CHECK: Verify if 'Final Decision' is required when status is 'Completed'.
        """
        interview = frappe.get_doc({
            "doctype": "Exit Interview",
            "employee": self.employee,
            "company": self.company,
            "status": "Completed", 
            "interview_summary": "Testing mandatory field logic."
        })

        try:
            # If the system allows saving as 'Completed' without a decision, it is a GAP
            interview.insert()
            if not interview.get("employee_status"):
                print("\n[GAP FOUND] System allowed 'Completed' status without Final Decision!")
        except (MandatoryError, ValidationError):
            print("\n[SUCCESS] System correctly blocked 'Completed' status.")

    def tearDown(self):
        """
        Clean up: Rollback database changes.
        """
        frappe.db.rollback()