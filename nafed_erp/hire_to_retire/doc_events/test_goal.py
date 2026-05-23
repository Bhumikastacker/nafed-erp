import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestGoal(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure a dummy Employee exists.
        """
        self.company = "_Test Indian Registered Company"
        
        if not frappe.db.exists("Employee", {"first_name": "GoalUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-GOAL-001",
                "first_name": "GoalUser",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_ppedate": "2024-01-01",
                "custom_vpf_applicable": "No",
                "custom_allotted_official_accommodation": "No"
            }).insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "GoalUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_goal_creation(self):
        """
        CASE 1: Verify that a valid Goal can be created with mandatory fields.
        """
        goal = frappe.get_doc({
            "doctype": "Goal",
            "goal_name": "Complete Unit Testing Suite", # Mandatory
            "employee": self.test_employee,             # Mandatory
            "start_date": today(),                      # Mandatory
            "status": "In Progress",
            "progress": 50
        })
        goal.insert()
        self.assertTrue(frappe.db.exists("Goal", goal.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {goal.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_sequence_gap(self):
        """
        GAP CHECK: Testing if system allows 'End Date' to be before 'Start Date'.
        """
        goal = frappe.get_doc({
            "doctype": "Goal",
            "goal_name": "Invalid Date Test",
            "employee": self.test_employee,
            "start_date": today(),
            "end_date": add_days(today(), -10) # INVALID: End date is in the past
        })

        try:
            goal.insert()
            print("\n[GAP FOUND] Goal allowed invalid date sequence (End < Start)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_invalid_progress_percentage_gap(self):
        """
        GAP CHECK: Testing if system allows progress percentage to be > 100%.
        """
        goal = frappe.get_doc({
            "doctype": "Goal",
            "goal_name": "Invalid Progress Test",
            "employee": self.test_employee,
            "start_date": today(),
            "progress": 150 # INVALID: Percentage cannot exceed 100
        })

        try:
            goal.insert()
            print("[GAP FOUND] Goal allowed progress percentage GREATER than 100%!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked invalid progress percentage.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()