# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestIncrementLog(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, getdate
from frappe import ValidationError

class TestIncrementLogGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup test prerequisites: Ensure Company and Employee exist.
        The Employee must have 'custom_basic_pay' as it is fetched into 'old_basic'.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "INC-LOG-999"
        
        # 1. Setup Employee with NAFED mandatory fields and a starting Basic Pay
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Increment",
                "last_name": "Tester",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "company": self.company,
                "custom_basic_pay": 50000, # Required for 'old_basic' fetch
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
            # Ensure basic pay is set for existing record
            frappe.db.set_value("Employee", self.employee, "custom_basic_pay", 50000)

        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_increment_creation(self):
        """
        CASE 1: Verify successful creation of an Increment Log with valid data.
        """
        log = frappe.get_doc({
            "doctype": "Increment Log",
            "company": self.company,
            "employee": self.employee,
            "effective_date": today(),
            "old_basic": 50000,
            "new_basic": "60000", # Note: new_basic is a Select field in your JSON
            "increment_amount": 10000,
            "increment_month": "July",
            "increment_year": 2026
        })
        log.insert()
        self.assertTrue(frappe.db.exists("Increment Log", log.name))
        print(f"\n[Positive Test] SUCCESS! Increment Log Created: {log.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Negative or Lower Salary Check
    # ---------------------------------------------------------
    def test_gap_1_negative_increment_logic(self):
        """
        GAP CHECK: Does the system allow a 'New Basic' that is lower than 'Old Basic'?
        An increment should logically increase the salary, not decrease it.
        """
        log = frappe.get_doc({
            "doctype": "Increment Log",
            "company": self.company,
            "employee": self.employee,
            "old_basic": 50000,
            "new_basic": "40000", # INVALID: Lower than old basic
            "increment_month": "January",
            "increment_year": 2026
        })

        try:
            log.insert()
            # If saved, it means the system allows "Negative Increments"
            if float(log.new_basic) < log.old_basic:
                print("\n[GAP FOUND] System allowed an Increment where New Basic is LOWER than Old Basic!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative increment logic.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Future Year Limit
    # ---------------------------------------------------------
    def test_gap_2_future_year_limit(self):
        """
        GAP CHECK: Does the system allow an 'Increment Year' too far in the future?
        Example: Setting an increment for the year 2050.
        """
        log = frappe.get_doc({
            "doctype": "Increment Log",
            "company": self.company,
            "employee": self.employee,
            "increment_year": 2050, # INVALID: Unrealistic future year
            "increment_month": "July",
            "new_basic": "70000",
            "old_basic": 50000
        })

        try:
            log.insert()
            print(f"\n[GAP FOUND] System allowed an unrealistic Increment Year ({log.increment_year})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly restricted future years.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Effective Date Consistency
    # ---------------------------------------------------------
    def test_gap_3_effective_date_mismatch(self):
        """
        GAP CHECK: Verify if 'Effective Date' is forced to match 'Increment Month/Year'.
        If effective date is Today (March) but Month is July, it creates a data mismatch.
        """
        log = frappe.get_doc({
            "doctype": "Increment Log",
            "company": self.company,
            "employee": self.employee,
            "effective_date": "2026-03-01",
            "increment_month": "July", # MISMATCH
            "increment_year": 2026,
            "new_basic": "60000",
            "old_basic": 50000
        })

        try:
            log.insert()
            # Logically, the Effective Date should be the 1st of the Increment Month
            print("\n[GAP FOUND] System allowed mismatch between Effective Date and Increment Month!")
        except ValidationError:
            print("\n[SUCCESS] System correctly enforced date/month consistency.")
	
	# ---------------------------------------------------------
    # NEGATIVE TEST - GAP 4: Stop Increment Bypass Check
    # ---------------------------------------------------------
    def test_gap_4_stop_increment_bypass(self):
        """
        GAP CHECK: If an employee has an active 'Stop Increment Log', 
        the system must block creating a new 'Increment Log' for them.
        """
        # 1. Pehle is employee ka increment rokne ka record banayein
        frappe.get_doc({
            "doctype": "Stop Increment Log",
            "company": self.company,
            "employee": self.employee,
            "increment_month": "July",
            "increment_year": 2026,
            "reason": "Disciplinary Action",
            "effective_date": today()
        }).insert()

        # 2. Ab wahi same mahine/saal ke liye Increment dene ki koshish karein
        log = frappe.get_doc({
            "doctype": "Increment Log",
            "company": self.company,
            "employee": self.employee,
            "increment_month": "July",
            "increment_year": 2026,
            "new_basic": "65000",
            "old_basic": 50000,
            "effective_date": today()
        })

        try:
            log.insert()
            # Agar save ho gaya, toh iska matlab "Stop" ka "Increment" par koi asar nahi hai (GAP FOUND)
            print("\n[GAP FOUND] System allowed Increment despite an active STOP INCREMENT record!")
        except ValidationError:
            # Agar error aaya, toh system mazboot hai
            print("\n[SECURE] System correctly blocked increment for a stopped employee.")

    def tearDown(self):
        """
        Cleanup database changes.
        """
        frappe.db.rollback()