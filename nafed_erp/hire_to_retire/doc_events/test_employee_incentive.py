import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestEmployeeIncentiveGaps(FrappeTestCase):

    def setUp(self):
        """
        Set up test prerequisites: Ensure Company, Employee, and Salary Component exist.
        Includes all NAFED mandatory fields for the Employee record.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "INC-TEST-999"
        self.component_name = "Sales Incentive"

        # 1. Create Employee with all NAFED mandatory custom fields
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Incentive",
                "last_name": "Tester",
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
            emp.insert(ignore_permissions=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_no}, "name")

        # 2. Ensure Salary Component (Incentive type) exists
        if not frappe.db.exists("Salary Component", self.component_name):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": self.component_name,
                "salary_component_abbr": "SINC",
                "type": "Earning"
            }).insert()

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_incentive_creation(self):
        """
        CASE 1: Verify successful creation of an Employee Incentive with valid data.
        """
        incentive = frappe.get_doc({
            "doctype": "Employee Incentive",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "payroll_date": today(),
            "incentive_amount": 3500
        })
        incentive.insert()
        self.assertTrue(frappe.db.exists("Employee Incentive", incentive.name))
        print(f"\n[Positive Test] SUCCESS! Employee Incentive Created: {incentive.name}")

    # ---------------------------------------------------------
    # GAP 1: Negative Incentive Amount
    # ---------------------------------------------------------
    def test_gap_1_negative_incentive_amount(self):
        """
        GAP CHECK: Does the system allow a negative value in the Incentive Amount field?
        An incentive should logically be a positive reward.
        """
        incentive = frappe.get_doc({
            "doctype": "Employee Incentive",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "payroll_date": today(),
            "incentive_amount": -500 # INVALID DATA
        })

        try:
            incentive.insert()
            # If the code reaches here, it means the system failed to block the negative amount.
            print("\n[GAP FOUND] Employee Incentive allowed a NEGATIVE Amount!")
        except ValidationError:
            # If an error is thrown, the system logic is secure.
            print("\n[SUCCESS] System correctly blocked negative incentive amount.")

    # ---------------------------------------------------------
    # GAP 2: Future Payroll Date Check
    # ---------------------------------------------------------
    def test_gap_2_future_payroll_date(self):
        """
        GAP CHECK: Does the system allow awarding an incentive for a date far in the future?
        Example: Setting a payroll date for next year.
        """
        future_date = add_days(today(), 365) # 1 year later
        incentive = frappe.get_doc({
            "doctype": "Employee Incentive",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "payroll_date": future_date, # INVALID: Far future
            "incentive_amount": 1000
        })

        try:
            incentive.insert()
            print(f"\n[GAP FOUND] System allowed an Incentive for a FUTURE Payroll Date ({future_date})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked future-dated incentive.")

    def tearDown(self):
        """
        Rollback database changes to maintain a clean test environment.
        """
        frappe.db.rollback()