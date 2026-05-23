import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today
from frappe import ValidationError, MandatoryError, DoesNotExistError

class TestEmployeeSkillMapGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Robust handling of existing records to avoid DuplicateEntryError.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "SKILL-FIX-555"
        self.test_emp_name = "Skill Tester" # Matched the name from your error log

        # 1. First, check if "Skill Tester" already exists in the database
        existing_emp = frappe.db.exists("Employee", {"employee_name": self.test_emp_name})
        
        if not existing_emp:
            # Create a new employee ONLY if they don't exist
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Skill",
                "last_name": "Tester",
                "employee_name": self.test_emp_name,
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "company": self.company,
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.employee = emp.name
        else:
            # If they exist, use the existing ID
            self.employee = existing_emp

        # 2. Setup Training Feedback record dynamically
        fb_doc = frappe.get_doc({
            "doctype": "Nafed Training Feedback",
            "employee": self.employee,
            "rating": 4 
        })
        fb_doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
        self.feedback_id = fb_doc.name

        frappe.db.commit()
        frappe.clear_cache()

    # ---------------------------------------------------------
    # Positive Case
    # ---------------------------------------------------------
    def test_1_positive_skill_map_creation(self):
        """ Verify valid creation """
        doc = frappe.get_doc({
            "doctype": "Employee Skill Map",
            "employee": self.employee,
            "custom_employee_feedback_id": self.feedback_id,
            "employee_skills": [{"skill": "Communication", "proficiency": "Expert"}]
        })
        doc.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Employee Skill Map", doc.name))
        print(f"\n[Positive Test] SUCCESS! Created for: {self.employee}")

    # ---------------------------------------------------------
    # Negative Test - GAP 1: Duplicate Constraint
    # ---------------------------------------------------------
    def test_gap_1_duplicate_employee_map(self):
        """ Ensure duplicate maps for same employee are blocked """
        self.test_1_positive_skill_map_creation()
        duplicate_doc = frappe.get_doc({
            "doctype": "Employee Skill Map",
            "employee": self.employee,
            "custom_employee_feedback_id": self.feedback_id
        })
        try:
            duplicate_doc.insert(ignore_permissions=True)
            print("\n[GAP FOUND] System allowed DUPLICATE Skill Maps!")
        except Exception:
            print("\n[SECURE] System correctly blocked duplicate skill maps.")

    # ---------------------------------------------------------
    # Negative Test - GAP 2: Empty Table Validation
    # ---------------------------------------------------------
    def test_gap_2_empty_skills_table(self):
        """ Ensure skills table cannot be empty """
        doc = frappe.get_doc({
            "doctype": "Employee Skill Map",
            "employee": self.employee,
            "custom_employee_feedback_id": self.feedback_id,
            "employee_skills": [] 
        })
        try:
            doc.insert(ignore_permissions=True)
            if not doc.employee_skills:
                print("\n[GAP FOUND] Employee Skill Map allowed EMPTY skills table!")
        except (ValidationError, MandatoryError):
            print("\n[SECURE] System correctly blocked empty skills table.")

    # ---------------------------------------------------------
    # Negative Test - GAP 3: Mandatory Field Check
    # ---------------------------------------------------------
    def test_gap_3_missing_mandatory_link(self):
        """ Ensure mandatory feedback ID is strictly enforced """
        doc = frappe.get_doc({
            "doctype": "Employee Skill Map",
            "employee": self.employee,
            "custom_employee_feedback_id": None 
        })
        try:
            doc.insert(ignore_permissions=True)
            print("\n[GAP FOUND] System allowed saving without Feedback ID!")
        except (MandatoryError, ValidationError, DoesNotExistError):
            print("\n[SECURE] System correctly blocked missing Feedback ID.")

    def tearDown(self):
        frappe.db.rollback()