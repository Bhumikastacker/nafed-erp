import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestRetentionBonusGaps(FrappeTestCase):

    def setUp(self):
        """
        Set up test prerequisites: Ensure Company, Employee, and Salary Component exist.
        Includes all NAFED mandatory custom fields for the Employee.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "RET-BON-999"
        self.component_name = "Retention Bonus Component"

        # 1. Create Employee with all NAFED mandatory fields to avoid Setup Errors
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Retention",
                "last_name": "Tester",
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
            emp.insert(ignore_permissions=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_no}, "name")

        # 2. Ensure Salary Component exists
        if not frappe.db.exists("Salary Component", self.component_name):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": self.component_name,
                "salary_component_abbr": "RBON",
                "type": "Earning"
            }).insert()

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_retention_bonus_creation(self):
        """
        CASE 1: Verify successful creation of a Retention Bonus with valid data.
        """
        bonus = frappe.get_doc({
            "doctype": "Retention Bonus",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "bonus_amount": 10000,
            "bonus_payment_date": add_days(today(), 30), # Future payment date
            "currency": "INR"
        })
        bonus.insert()
        self.assertTrue(frappe.db.exists("Retention Bonus", bonus.name))
        print(f"\n[Positive Test] SUCCESS! Retention Bonus Created: {bonus.name}")

    # ---------------------------------------------------------
    # GAP 1: Negative Bonus Amount
    # ---------------------------------------------------------
    def test_gap_1_negative_bonus_amount(self):
        """
        GAP CHECK: Does the system allow a negative value in the Bonus Amount field?
        A bonus should always be a positive financial reward.
        """
        bonus = frappe.get_doc({
            "doctype": "Retention Bonus",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "bonus_amount": -5000, # INVALID FINANCIAL DATA
            "bonus_payment_date": today()
        })

        try:
            bonus.insert()
            # If saved, it indicates a lack of numerical validation (Gap)
            print("\n[GAP FOUND] Retention Bonus allowed a NEGATIVE Amount!")
        except ValidationError:
            # Successfully blocked by the system
            print("\n[SUCCESS] System correctly blocked negative bonus amount.")

    # ---------------------------------------------------------
    # GAP 2: Resigned Employee Logic Gap
    # ---------------------------------------------------------
    def test_gap_2_resigned_employee_bonus(self):
        """
        GAP CHECK: Does the system allow creating a 'Retention' bonus for an employee 
        who has already resigned (Relieving Date is set)?
        """
        # Set a relieving date for the tester employee to simulate resignation
        frappe.db.set_value("Employee", self.employee, "relieving_date", today())
        
        bonus = frappe.get_doc({
            "doctype": "Retention Bonus",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "bonus_amount": 5000,
            "bonus_payment_date": add_days(today(), 10)
        })

        try:
            bonus.insert()
            # If saved for a resigned employee, it's a process gap
            print("\n[GAP FOUND] System allowed a Retention Bonus for a RESIGNED employee!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked bonus for resigned employee.")

    def tearDown(self):
        """
        Rollback changes to clean the database.
        """
        frappe.db.rollback()