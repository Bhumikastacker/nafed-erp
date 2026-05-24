# Copyright (c) 2025, Aarti Kumari and Contributors
# See license.txt

# # import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestMedicalReimbursementForm(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestMedicalReimbursementForm(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee, Bank, and Hospital.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure a Bank exists
        if not frappe.db.exists("Bank", "Test Bank"):
            frappe.get_doc({"doctype": "Bank", "bank_name": "Test Bank"}).insert()

        # 2. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "MedicalUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-MED-001",
                "first_name": "MedicalUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "121212121212",
                "custom_vpf_applicable": "No",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert(ignore_mandatory=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"first_name": "MedicalUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_reimbursement_creation(self):
        """
        CASE 1: Verify successful creation of Medical Reimbursement Form.
        """
        mrf = frappe.get_doc({
            "doctype": "Medical Reimbursement Form",
            "employee_code": self.employee,
            "bank_account_no": "123456789",
            "bank_name": "Test Bank",
            "date_of_admission": add_days(today(), -5),
            "date_of_discharge": today(),
            "total_bill_amount": 5000,
            "medical_reimbursement_details": [
                {
                    "bill_no": "BILL-001",
                    "bill_date": today(),
                    "amount": 5000
                }
            ]
        })
        mrf.insert()
        self.assertTrue(frappe.db.exists("Medical Reimbursement Form", mrf.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {mrf.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_wrong_date_sequence_gap(self):
        """
        GAP CHECK: Testing if Discharge Date can be BEFORE Admission Date.
        """
        mrf = frappe.get_doc({
            "doctype": "Medical Reimbursement Form",
            "employee_code": self.employee,
            "bank_account_no": "123456789",
            "bank_name": "Test Bank",
            "date_of_admission": today(),
            "date_of_discharge": add_days(today(), -5), # INVALID: Discharge before Admission
            "total_bill_amount": 1000
        })

        try:
            mrf.insert()
            print("\n[GAP FOUND] System allowed Discharge Date BEFORE Admission Date!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date sequence.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_negative_bill_amount_gap(self):
        """
        GAP CHECK: Testing if system allows negative bill amounts.
        """
        mrf = frappe.get_doc({
            "doctype": "Medical Reimbursement Form",
            "employee_code": self.employee,
            "bank_account_no": "123456789",
            "bank_name": "Test Bank",
            "total_bill_amount": -1000 # INVALID DATA
        })

        try:
            mrf.insert()
            print("[GAP FOUND] System allowed NEGATIVE Total Bill Amount!")
        except ValidationError:
            print("[SUCCESS] System blocked negative bill amount.")

    def tearDown(self):
        frappe.db.rollback()