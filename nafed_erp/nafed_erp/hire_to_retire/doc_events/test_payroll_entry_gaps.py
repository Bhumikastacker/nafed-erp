import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, get_last_day, get_first_day
from frappe import ValidationError

class TestPayrollEntryGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Create Employee with ALL NAFED mandatory custom fields.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "PAY-ROLL-999"
        
        # 1. Handle Employee creation with all mandatory fields
        existing_emp = frappe.db.exists("Employee", {"employee_number": self.emp_no})
        
        if not existing_emp:
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Payroll",
                "last_name": "Tester",
                "employee_name": "Payroll Tester",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": "2020-01-01",
                "company": self.company,
                # NAFED Mandatory Fields:
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.employee = emp.name
        else:
            self.employee = existing_emp

        # 2. Get a valid Payroll Payable Account for the company
        self.payable_account = frappe.db.get_value("Account", 
            {"account_type": "Payable", "company": self.company}, "name") or "Salary Payable - _BC"

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_payroll_entry_creation(self):
        """
        Verify successful creation of a Payroll Entry.
        """
        pe = frappe.get_doc({
            "doctype": "Payroll Entry",
            "company": self.company,
            "posting_date": today(),
            "payroll_frequency": "Monthly",
            "start_date": get_first_day(today()),
            "end_date": get_last_day(today()),
            "payroll_payable_account": self.payable_account,
            "currency": "INR",
            "exchange_rate": 1.0,
            "cost_center": "Main - _BC"
        })
        pe.insert()
        self.assertTrue(frappe.db.exists("Payroll Entry", pe.name))
        print(f"\n[Positive Test] SUCCESS! Payroll Entry: {pe.name}")

    # ---------------------------------------------------------
    # GAP 1: Invalid Date Range
    # ---------------------------------------------------------
    def test_gap_1_invalid_period_dates(self):
        """
        CHECK: Does the system allow Start Date > End Date?
        """
        pe = frappe.get_doc({
            "doctype": "Payroll Entry",
            "company": self.company,
            "start_date": add_days(today(), 30), # Next month
            "end_date": today(),                 # Today (Invalid)
            "payroll_payable_account": self.payable_account
        })

        try:
            pe.insert()
            print("\n[GAP FOUND] Payroll Entry allowed INVALID date range (Start > End)!")
        except ValidationError:
            print("\n[SECURE] System correctly blocked invalid dates.")

    # ---------------------------------------------------------
    # GAP 2: Future Posting Date
    # ---------------------------------------------------------
    def test_gap_2_future_posting_date(self):
        """
        CHECK: Does the system allow booking payroll for far future?
        """
        future_date = "2030-01-01"
        pe = frappe.get_doc({
            "doctype": "Payroll Entry",
            "company": self.company,
            "posting_date": future_date, 
            "start_date": get_first_day(today()),
            "end_date": get_last_day(today()),
            "payroll_payable_account": self.payable_account
        })

        try:
            pe.insert()
            print(f"\n[GAP FOUND] System allowed Posting Date in Year 2030!")
        except ValidationError:
            print("\n[SECURE] System correctly blocked future posting.")

    def tearDown(self):
        frappe.db.rollback()