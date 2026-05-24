import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestAdditionalSalaryGaps(FrappeTestCase):

    def setUp(self):
        """
        Set up test prerequisites: Ensure Company, Employee, and Salary Component exist.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "ADD-SAL-999"
        self.component_name = "Performance Bonus"

        # 1. Create Employee with all NAFED mandatory fields to avoid setup errors
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Additional",
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

        # 2. Ensure Salary Component exists
        if not frappe.db.exists("Salary Component", self.component_name):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": self.component_name,
                "salary_component_abbr": "PB",
                "type": "Earning"
            }).insert()

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_additional_salary_creation(self):
        """
        Verify successful creation of an Additional Salary record with valid data.
        """
        add_sal = frappe.get_doc({
            "doctype": "Additional Salary",
            "naming_series": "HR-ADS-.YY.-.MM.-",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "payroll_date": today(),
            "amount": 5000,
            "overwrite_salary_structure_amount": 1
        })
        add_sal.insert()
        self.assertTrue(frappe.db.exists("Additional Salary", add_sal.name))
        print(f"\n[Positive Test] SUCCESS! Additional Salary Created: {add_sal.name}")

    # ---------------------------------------------------------
    # GAP 1: Negative Amount Check
    # ---------------------------------------------------------
    def test_gap_1_negative_amount(self):
        """
        CHECK: Does the system allow a negative value in the Amount field?
        """
        add_sal = frappe.get_doc({
            "doctype": "Additional Salary",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "payroll_date": today(),
            "amount": -1500 # INVALID FINANCIAL DATA
        })

        try:
            add_sal.insert()
            # If execution reaches here, the system allowed invalid data.
            print("\n[GAP FOUND] Additional Salary allowed a NEGATIVE Amount!")
        except ValidationError:
            # If it throws an error, the system is secure.
            print("\n[SUCCESS] System correctly blocked negative additional salary amount.")

    # ---------------------------------------------------------
    # GAP 2: Invalid Recurring Date Range (From Date > To Date)
    # ---------------------------------------------------------
    def test_gap_2_invalid_recurring_dates(self):
        """
        CHECK: In recurring mode, does the system allow From Date to be AFTER To Date?
        """
        add_sal = frappe.get_doc({
            "doctype": "Additional Salary",
            "employee": self.employee,
            "company": self.company,
            "salary_component": self.component_name,
            "is_recurring": 1,
            "from_date": add_days(today(), 30), # Start in next month
            "to_date": today(),                 # End today (Invalid Range)
            "amount": 2000
        })

        try:
            add_sal.insert()
            print("\n[GAP FOUND] Additional Salary allowed an INVALID recurring date range (From > To)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid recurring date sequence.")

    def tearDown(self):
        """
        Rollback database changes to maintain a clean environment.
        """
        frappe.db.rollback()