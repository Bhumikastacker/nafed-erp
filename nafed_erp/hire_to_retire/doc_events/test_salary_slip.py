import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, get_last_day, get_first_day, add_months
from frappe import ValidationError

class TestSalarySlipGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup test environment: Ensure all prerequisites exist with valid dates.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "GAP-SLIP-999"
        self.structure_name = "Gap Test Structure"
        
        # 1. Ensure Holiday List exists
        if not frappe.db.exists("Holiday List", "Test Holidays"):
            frappe.get_doc({
                "doctype": "Holiday List", 
                "holiday_list_name": "Test Holidays", 
                "from_date": "2020-01-01", 
                "to_date": "2030-12-31"
            }).insert(ignore_permissions=True)

        # 2. Ensure Employee exists with NAFED mandatory fields
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Gap",
                "last_name": "Tester",
                "company": self.company,
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1995-01-01",
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

        # 3. Ensure Salary Structure Assignment exists from an early date
        if not frappe.db.exists("Salary Structure", self.structure_name):
            frappe.get_doc({
                "doctype": "Salary Structure", 
                "name": self.structure_name, 
                "company": self.company, 
                "currency": "INR", 
                "is_active": "Yes"
            }).insert(ignore_permissions=True)
        
        if not frappe.db.exists("Salary Structure Assignment", {"employee": self.employee}):
            frappe.get_doc({
                "doctype": "Salary Structure Assignment",
                "employee": self.employee,
                "salary_structure": self.structure_name,
                "from_date": "2020-01-01",
                "base": 50000
            }).insert(ignore_permissions=True)

        frappe.db.commit()
        frappe.clear_cache()

    # ---------------------------------------------------------
    # GAP 1: Duplicate Monthly Slip Check
    # ---------------------------------------------------------
    def test_gap_1_duplicate_monthly_slip(self):
        """
        CHECK: Does the system allow two salary slips for the same employee in the same month?
        """
        # Create the first slip
        slip1 = frappe.get_doc({
            "doctype": "Salary Slip",
            "employee": self.employee,
            "start_date": get_first_day(today()),
            "end_date": get_last_day(today()),
            "posting_date": today(),
            "company": self.company
        }).insert()

        # Try to create a second slip for the SAME month
        slip2 = frappe.get_doc({
            "doctype": "Salary Slip",
            "employee": self.employee,
            "start_date": get_first_day(today()),
            "end_date": get_last_day(today()),
            "posting_date": today(),
            "company": self.company
        })

        try:
            slip2.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Salary Slips for the same month!")
        except (ValidationError, Exception):
            print("\n[SECURE] System correctly blocked duplicate monthly salary slips.")

    # ---------------------------------------------------------
    # GAP 2: Negative Net Pay Check
    # ---------------------------------------------------------
    def test_gap_2_negative_net_pay(self):
        """
        CHECK: Does the system allow a slip where Net Pay is negative (Deductions > Earnings)?
        """
        salary_slip = frappe.get_doc({
            "doctype": "Salary Slip",
            "employee": self.employee,
            "start_date": get_first_day(add_months(today(), -1)),
            "end_date": get_last_day(add_months(today(), -1)),
            "posting_date": today(),
            "company": self.company
        })
        
        # Manually force a massive deduction to create negative net pay
        salary_slip.append("deductions", {
            "salary_component": "Professional Tax",
            "amount": 999999 # Much higher than earning
        })

        try:
            salary_slip.insert()
            if salary_slip.net_pay < 0:
                print(f"\n[GAP FOUND] System allowed a Salary Slip with NEGATIVE Net Pay ({salary_slip.net_pay})!")
            else:
                print("\n[SECURE] System recalculated or blocked negative net pay.")
        except ValidationError:
            print("\n[SECURE] System correctly blocked negative net pay creation.")

    # ---------------------------------------------------------
    # GAP 3: Future Posting Date Check
    # ---------------------------------------------------------
    def test_gap_3_future_posting_date(self):
        """
        CHECK: Does the system allow a Posting Date in the far future (e.g., next year)?
        """
        future_date = add_days(today(), 365)
        salary_slip = frappe.get_doc({
            "doctype": "Salary Slip",
            "employee": self.employee,
            "start_date": get_first_day(today()),
            "end_date": get_last_day(today()),
            "posting_date": future_date, # INVALID: 1 year ahead
            "company": self.company
        })

        try:
            salary_slip.insert()
            print(f"\n[GAP FOUND] System allowed a Salary Slip with a FUTURE Posting Date ({future_date})!")
        except ValidationError:
            print("\n[SECURE] System correctly blocked future-dated posting.")

    def tearDown(self):
        frappe.db.rollback()