import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestEmployeePromotion(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Create a dummy Employee with current CTC.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Create a dummy Employee for promotion testing
        if not frappe.db.exists("Employee", {"first_name": "PromoUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-PRO-101",
                "first_name": "PromoUser",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "status": "Active",
                "company": self.company,
                "ctc": 500000, # Current CTC
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2024-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "PromoUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_promotion_creation(self):
        """
        CASE 1: Verify successful creation of a valid Employee Promotion.
        """
        promotion = frappe.get_doc({
            "doctype": "Employee Promotion",
            "employee": self.test_employee,
            "promotion_date": today(),
            "company": self.company,
            "current_ctc": 500000,
            "revised_ctc": 600000 # Salary Increase
        })
        promotion.insert()
        self.assertTrue(frappe.db.exists("Employee Promotion", promotion.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {promotion.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_ctc_gap(self):
        """
        GAP CHECK: Testing if system allows negative values in Revised CTC.
        """
        promotion = frappe.get_doc({
            "doctype": "Employee Promotion",
            "employee": self.test_employee,
            "promotion_date": today(),
            "revised_ctc": -10000 # INVALID DATA
        })

        try:
            promotion.insert()
            print("\n[GAP FOUND] Employee Promotion allowed NEGATIVE Revised CTC!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative CTC.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_backdated_promotion_gap(self):
        """
        GAP CHECK: Testing if promotion date can be BEFORE Joining Date.
        Joining Date is 2024-01-01, we try promotion in 2023.
        """
        promotion = frappe.get_doc({
            "doctype": "Employee Promotion",
            "employee": self.test_employee,
            "promotion_date": "2023-01-01", # INVALID: Before joining
            "revised_ctc": 600000
        })

        try:
            promotion.insert()
            print("[GAP FOUND] Employee Promotion allowed BEFORE Joining Date!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked invalid promotion date.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_4_salary_decrease_gap(self):
        """
        GAP CHECK: Testing if system allows a 'Promotion' with a salary DECREASE.
        """
        promotion = frappe.get_doc({
            "doctype": "Employee Promotion",
            "employee": self.test_employee,
            "promotion_date": today(),
            "current_ctc": 500000,
            "revised_ctc": 400000 # INVALID: Decrease in promotion
        })

        try:
            promotion.insert()
            print("[GAP FOUND] Employee Promotion allowed a salary DECREASE!")
        except ValidationError:
            print("[SUCCESS] System blocked salary decrease during promotion.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()                                                                                                    