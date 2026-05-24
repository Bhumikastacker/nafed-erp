import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestFullAndFinalStatement(FrappeTestCase):

    def setUp(self):
        """
        Set up: Robust Employee creation with ALL NAFED mandatory fields.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "FNF-NUM-999"
        self.relieving_date = today()
        
        # 1. Main Tester Employee
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "FnF",
                "last_name": "Tester",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "relieving_date": self.relieving_date,
                "status": "Left",
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
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_no}, "name")
            frappe.db.set_value("Employee", self.employee, "relieving_date", self.relieving_date)

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_fnf_creation(self):
        fnf = frappe.get_doc({
            "doctype": "Full and Final Statement",
            "employee": self.employee,
            "transaction_date": today()
        })
        fnf.insert()
        self.assertTrue(frappe.db.exists("Full and Final Statement", fnf.name))
        print(f"\n[Positive Test] SUCCESS! F&F Created: {fnf.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_active_employee_fnf_gap(self):
        """
        GAP CHECK: Kya Active employee ka F&F ban sakta hai?
        """
        active_emp_no = "ACT-NUM-888"
        if not frappe.db.exists("Employee", {"employee_number": active_emp_no}):
            active_emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": active_emp_no,
                "first_name": "Active",
                "employee_name": "Active User",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "company": self.company,
                "date_of_joining": today(),
                "pan_number": "ABCDE5555F",
                "custom_uan_number": "200000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            }).insert(ignore_permissions=True)
            active_emp_id = active_emp.name
        else:
            active_emp_id = frappe.db.get_value("Employee", {"employee_number": active_emp_no}, "name")

        fnf = frappe.get_doc({
            "doctype": "Full and Final Statement",
            "employee": active_emp_id,
            "transaction_date": today()
        })

        try:
            fnf.insert()
            # F&F controller mein check hona chahiye ki relieving_date set hai ya nahi
            emp_rd = frappe.db.get_value("Employee", active_emp_id, "relieving_date")
            if not emp_rd:
                print("\n[GAP FOUND] F&F Statement allowed for an ACTIVE employee!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked F&F for active employee.")

    # ------------------------
    # Logic Gap Check (Future Date)
    # ------------------------
    def test_3_future_transaction_date_gap(self):
        """
        GAP CHECK: Kya transaction date future ki ho sakti hai?
        """
        future_date = add_days(today(), 30)
        fnf = frappe.get_doc({
            "doctype": "Full and Final Statement",
            "employee": self.employee,
            "transaction_date": future_date 
        })

        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed FUTURE Transaction Date!"):
            fnf.insert()

    def tearDown(self):
        frappe.db.rollback()