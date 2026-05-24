import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestSalaryStructureAssignment(FrappeTestCase):

    def setUp(self):
        """
        Set up test prerequisites: Ensure Company, Employee, and Salary Structure exist.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_id = "SSA-TEST-999"
        self.structure_name = "SSA Test Template"

        # 1. Ensure Employee exists with all NAFED mandatory custom fields
        existing_emp = frappe.db.exists("Employee", {"employee_number": self.emp_id})
        
        if not existing_emp:
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_id,
                "first_name": "SSA",
                "last_name": "Tester",
                "employee_name": "SSA Tester User",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "date_of_birth": "1995-01-01",
                "company": self.company,
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            # Insert using ignore_permissions for test environment safety
            emp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_id}, "name")

        # 2. Ensure a master Salary Structure exists for assignment
        if not frappe.db.exists("Salary Structure", self.structure_name):
            frappe.get_doc({
                "doctype": "Salary Structure",
                "name": self.structure_name,
                "company": self.company,
                "currency": "INR",
                "is_active": "Yes"
            }).insert(ignore_permissions=True)
        
        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_assignment_creation(self):
        """
        CASE 1: Verify successful creation of an assignment with valid data.
        """
        assignment = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": self.employee,
            "salary_structure": self.structure_name,
            "from_date": today(),
            "company": self.company,
            "base": 45000
        })
        assignment.insert()
        self.assertTrue(frappe.db.exists("Salary Structure Assignment", assignment.name))
        print(f"\n[Positive Test] SUCCESS! Assignment Created: {assignment.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_backdated_assignment_gap(self):
        """
        GAP CHECK: Verify if the system allows an assignment date before the Joining Date.
        """
        joining_date = frappe.db.get_value("Employee", self.employee, "date_of_joining")
        invalid_date = add_days(joining_date, -30) # 30 days before joining

        assignment = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": self.employee,
            "salary_structure": self.structure_name,
            "from_date": invalid_date, 
            "company": self.company,
            "base": 30000
        })

        try:
            assignment.insert()
            # If execution reaches here, it means the system allowed invalid data (Process Gap)
            print("\n[GAP FOUND] System allowed Salary Assignment BEFORE the Joining Date!")
        except ValidationError:
            # If an error is thrown, the system is secure
            print("\n[SUCCESS] System correctly blocked backdated assignment.")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_3_negative_base_pay_gap(self):
        """
        GAP CHECK: Verify if the system allows a negative 'Base' salary amount.
        """
        assignment = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": self.employee,
            "salary_structure": self.structure_name,
            "from_date": today(),
            "company": self.company,
            "base": -10000 # INVALID FINANCIAL DATA
        })

        try:
            assignment.insert()
            # If saved successfully, it indicates a missing validation for monetary values (Financial Gap)
            print("\n[GAP FOUND] Salary Structure Assignment allowed NEGATIVE Base Salary!")
        except ValidationError:
            # Successfully blocked by the system
            print("\n[SUCCESS] System correctly blocked negative base salary.")

    def tearDown(self):
        """
        Rollback database changes to keep the environment clean.
        """
        frappe.db.rollback()