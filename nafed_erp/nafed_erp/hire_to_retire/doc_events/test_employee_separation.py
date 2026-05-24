import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestEmployeeSeparation(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Existing data ko check karke fetch karein.
        """
        self.company = "_Test Indian Registered Company"
        # Unique identifier use karein taaki collision na ho
        self.emp_id_check = "SEP-TEST-99" 
        self.template_title = "Standard Exit Template"

        # 1. Check karein agar Employee pehle se hai (By ID or Employee Number)
        existing_emp = frappe.db.exists("Employee", {"employee_number": self.emp_id_check})
        
        if not existing_emp:
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_id_check,
                "first_name": "Sep",
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
            # ignore_if_duplicate use karein safety ke liye
            emp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.employee = emp.name
        else:
            self.employee = existing_emp

        # 2. Ensure Separation Template exists
        existing_template = frappe.db.exists("Employee Separation Template", {"title": self.template_title})
        if not existing_template:
            template = frappe.get_doc({
                "doctype": "Employee Separation Template",
                "title": self.template_title,
                "company": self.company,
                "activities": [{"activity_name": "IT Clearance", "role": "IT Manager"}]
            })
            template.insert(ignore_permissions=True, ignore_if_duplicate=True)
            self.template = template.name
        else:
            self.template = existing_template

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_separation_creation(self):
        """
        CASE 1: Sahi data ke sath creation.
        """
        sep = frappe.get_doc({
            "doctype": "Employee Separation",
            "employee": self.employee,
            "company": self.company,
            "boarding_begins_on": today(),
            "custom_employee_sepstation_type": "Resignation",
            "employee_separation_template": self.template
        })
        sep.insert()
        self.assertTrue(frappe.db.exists("Employee Separation", sep.name))
        print(f"\n[Positive Test] SUCCESS! Record: {sep.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_future_date_gap(self):
        """
        GAP CHECK: Future date validation.
        """
        future_date = add_days(today(), 90) 
        sep = frappe.get_doc({
            "doctype": "Employee Separation",
            "employee": self.employee,
            "company": self.company,
            "boarding_begins_on": future_date, 
            "custom_employee_sepstation_type": "Resignation"
        })

        with self.assertRaises(ValidationError, msg="GAP FOUND: System allowed FUTURE date!"):
            sep.insert()

    # ------------------------
    # Logic Gap Check
    # ------------------------
    def test_3_duplicate_active_separation_gap(self):
        """
        LOGIC GAP: Same employee ke liye 2 baar process shuru nahi hona chahiye.
        """
        # First creation (should pass)
        frappe.get_doc({
            "doctype": "Employee Separation",
            "employee": self.employee,
            "company": self.company,
            "boarding_begins_on": today(),
            "custom_employee_sepstation_type": "Resignation"
        }).insert()

        # Second creation (should fail if validation exists)
        duplicate_sep = frappe.get_doc({
            "doctype": "Employee Separation",
            "employee": self.employee,
            "company": self.company,
            "boarding_begins_on": today(),
            "custom_employee_sepstation_type": "Retire"
        })

        try:
            duplicate_sep.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Separation process for same employee!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked duplicate separation.")

    def tearDown(self):
        frappe.db.rollback()