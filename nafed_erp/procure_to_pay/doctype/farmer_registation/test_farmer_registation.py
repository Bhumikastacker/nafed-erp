# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestFarmerRegistation(FrappeTestCase):
# 	pass

# ===============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestFarmerRegistration(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Society (Supplier) and Gender.
        """
        # 1. Setup Society (Supplier with custom_is_sla=1)
        self.society = "Test Farmer Society"
        if not frappe.db.exists("Supplier", self.society):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": self.society,
                "custom_is_sla": 1,
                "supplier_group": "All Supplier Groups"
            }).insert(ignore_permissions=True)

        # 2. Setup Gender
        self.gender = "Male"
        if not frappe.db.exists("Gender", self.gender):
            frappe.get_doc({"doctype": "Gender", "gender": self.gender}).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_farmer_registration(self):
        """
        CASE 1: Successful creation of Farmer Registration.
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation", # Correcting your typo from JSON
            "naming_series": "FARMER-.YYYY.-",
            "farmer_id": "F-1001",
            "farmer_name": "Suresh Kumar",
            "gender": self.gender,
            "source": "Nafed(Manual)",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "123456789012" # Valid 12 digit
        })
        farmer.insert()
        
        self.assertTrue(frappe.db.exists("Farmer Registation", farmer.name))
        print(f"\n[Positive Test] SUCCESS! Created Farmer ID: {farmer.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Aadhaar Length Gap
    # ---------------------------------------------------------
    def test_2_invalid_aadhaar_length_gap(self):
        """
        GAP CHECK: Does the system allow Aadhaar numbers that are not 12 digits?
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation",
            "farmer_id": "F-ERR-1",
            "farmer_name": "Invalid Aadhaar",
            "gender": self.gender,
            "source": "Other",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "123" # INVALID: Only 3 digits
        })

        try:
            farmer.insert()
            # If saved, it's a security/identity gap
            print(f"\n[GAP FOUND] System allowed invalid Aadhaar length: {farmer.aadhaar_no}")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid Aadhaar length.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Duplicate Registration Gap
    # ---------------------------------------------------------
    def test_3_duplicate_aadhaar_gap(self):
        """
        GAP CHECK: Can two farmers be registered with the same Aadhaar?
        """
        aadhaar = "999988887777"
        data = {
            "doctype": "Farmer Registation",
            "farmer_id": "F-DUP-1",
            "farmer_name": "Farmer A",
            "gender": self.gender,
            "source": "E-samrdhi",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": aadhaar
        }
        frappe.get_doc(data).insert()

        # Try to register another farmer with same Aadhaar
        duplicate = frappe.get_doc(data)
        duplicate.farmer_id = "F-DUP-2"
        duplicate.farmer_name = "Farmer B"

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Aadhaar registration!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate Aadhaar.")

    # ---------------------------------------------------------
    # 4. Mandatory Field Gap
    # ---------------------------------------------------------
    def test_4_missing_gender_gap(self):
        """
        GAP CHECK: Is gender strictly enforced on the backend?
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation",
            "farmer_name": "No Gender Farmer",
            "source": "E-pravha",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "111122223333"
            # Missing gender
        })

        try:
            farmer.insert()
            print("\n[GAP FOUND] System allowed Farmer Registration WITHOUT Gender!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked missing gender.")

	# ---------------------------------------------------------
    # 5. Negative Test Case: Mobile Number Length (< 10 digits)
    # ---------------------------------------------------------
    def test_5_mobile_too_short_gap(self):
        """
        GAP CHECK: System should block mobile numbers less than 10 digits.
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation",
            "farmer_name": "Short Mobile Test",
            "gender": self.gender,
            "source": "Nafed(Manual)",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "111122223333",
            "mobile_no": "98765" # INVALID: Only 5 digits
        })

        try:
            farmer.insert()
            print(f"\n[GAP FOUND] System allowed SHORT Mobile No: {farmer.mobile_no}")
        except ValidationError:
            print("\n[SUCCESS] System blocked short mobile number.")

    # ---------------------------------------------------------
    # 6. Negative Test Case: Mobile Number Length (> 10 digits)
    # ---------------------------------------------------------
    def test_6_mobile_too_long_gap(self):
        """
        GAP CHECK: System should block mobile numbers more than 10 digits.
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation",
            "farmer_name": "Long Mobile Test",
            "gender": self.gender,
            "source": "Nafed(Manual)",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "444455556666",
            "mobile_no": "9876543210123" # INVALID: 13 digits
        })

        try:
            farmer.insert()
            print(f"\n[GAP FOUND] System allowed LONG Mobile No: {farmer.mobile_no}")
        except ValidationError:
            print("\n[SUCCESS] System blocked long mobile number.")

    # ---------------------------------------------------------
    # 7. Negative Test Case: Invalid Email Format
    # ---------------------------------------------------------
    def test_7_invalid_email_format_gap(self):
        """
        GAP CHECK: System should block invalid email formats.
        """
        farmer = frappe.get_doc({
            "doctype": "Farmer Registation",
            "farmer_name": "Email Format Test",
            "gender": self.gender,
            "source": "Nafed(Manual)",
            "registered_by_society": self.society,
            "registration_date": today(),
            "aadhaar_no": "777788889999",
            "email_id": "invalid-email-at-com" # INVALID: No @ or dot
        })

        try:
            farmer.insert()
            print(f"\n[GAP FOUND] System allowed INVALID Email Format: {farmer.email_id}")
        except ValidationError:
            print("\n[SUCCESS] System blocked incorrect email format.")

    def tearDown(self):
        frappe.db.rollback()