# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestVendorRegistration(FrappeTestCase):
# 	pass

# ==============================================================================================================

import frappe
import re
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestVendorRegistration(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: State and Supplier Group.
        """
        self.state = "Delhi"
        if not frappe.db.exists("State", self.state):
            frappe.get_doc({"doctype": "State", "state_name": self.state}).insert(ignore_permissions=True)

        self.category = "Service Provider"
        if not frappe.db.exists("Supplier Group", self.category):
            frappe.get_doc({"doctype": "Supplier Group", "supplier_group_name": self.category}).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_vendor_registration(self):
        """
        CASE 1: Successful creation with all valid compliance data.
        """
        vendor = frappe.get_doc({
            "doctype": "Vendor Registration",
            "source": "Nafed(Manual)",
            "vendor_name": "CSM Technologies",
            "vendor_category": self.category,
            "gstin": "07AAAAA0000A1Z5", # Valid 15 digit format
            "pan": "AAAAA0000A",        # Valid 10 digit format
            "mobile_number": "9876543210",
            "email_id": "info@csm.com",
            "state": self.state
        })
        vendor.insert()
        self.assertTrue(frappe.db.exists("Vendor Registration", vendor.name))
        print(f"\n[Positive Test] SUCCESS! Created Vendor ID: {vendor.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: PAN Gaps
    # ---------------------------------------------------------
    def test_2_invalid_pan_gap(self):
        """
        GAP CHECK: Does the system allow invalid PAN length/format?
        """
        vendor = frappe.get_doc({
            "doctype": "Vendor Registration",
            "vendor_name": "Invalid PAN Test",
            "source": "Other",
            "pan": "123" # INVALID: Should be 10 characters
        })

        try:
            vendor.insert()
            print(f"\n[GAP FOUND] System allowed INVALID PAN: {vendor.pan}")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid PAN.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: GSTIN Gaps
    # ---------------------------------------------------------
    def test_3_invalid_gstin_gap(self):
        """
        GAP CHECK: Does the system allow invalid GSTIN?
        """
        vendor = frappe.get_doc({
            "doctype": "Vendor Registration",
            "vendor_name": "Invalid GSTIN Test",
            "source": "Other",
            "gstin": "GST123" # INVALID: Should be 15 characters
        })

        try:
            vendor.insert()
            print(f"\n[GAP FOUND] System allowed INVALID GSTIN: {vendor.gstin}")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid GSTIN.")

    # ---------------------------------------------------------
    # 4. Negative Test Case: Duplicate PAN/GSTIN Gap
    # ---------------------------------------------------------
    def test_4_duplicate_compliance_gap(self):
        """
        GAP CHECK: Can two vendors have the same PAN?
        """
        pan_no = "ABCDE1234F"
        data = {
            "doctype": "Vendor Registration",
            "vendor_name": "Vendor A",
            "source": "E-auction",
            "pan": pan_no
        }
        frappe.get_doc(data).insert()

        duplicate = frappe.get_doc(data)
        duplicate.vendor_name = "Vendor B"
        try:
            duplicate.insert()
            print(f"\n[GAP FOUND] System allowed DUPLICATE PAN: {pan_no}")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate PAN.")

    # ---------------------------------------------------------
    # 5. Negative Test Case: Mobile & Email Gaps
    # ---------------------------------------------------------
    def test_5_contact_info_gaps(self):
        """
        GAP CHECK: Short Mobile and Invalid Email format.
        """
        vendor = frappe.get_doc({
            "doctype": "Vendor Registration",
            "vendor_name": "Contact Gap Test",
            "source": "Other",
            "mobile_number": "12",          # INVALID
            "email_id": "wrong-email-format" # INVALID
        })

        try:
            vendor.insert()
            print(f"\n[GAP FOUND] System allowed invalid Mobile ({vendor.mobile_number}) and Email ({vendor.email_id})")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid contact info.")

    def tearDown(self):
        frappe.db.rollback()