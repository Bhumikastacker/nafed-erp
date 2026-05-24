# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestAutoGenerateRenewalDocuments(FrappeTestCase):
# 	pass

# ===========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today, add_days

class TestAutoGenerateRenewalDocuments(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Agreement Type -> Division -> Contract CRN -> Renewal.
        """
        # 1. Setup Agreement Type
        self.agreement_type = "Renewal Agreement"
        if not frappe.db.exists("Agreement Type", self.agreement_type):
            frappe.get_doc({"doctype": "Agreement Type", "agreement_type": self.agreement_type}).insert(ignore_permissions=True)

        # 2. Setup Division (Handling your system typo: divsion_name)
        self.division = "Legal Division"
        if not frappe.db.exists("Division", self.division):
            frappe.get_doc({
                "doctype": "Division",
                "divsion_name": self.division,
                "name": self.division
            }).insert(ignore_permissions=True)

        # 3. Create a parent Contract CRN to be renewed
        self.contract = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "agreement_type": self.agreement_type,
            "agreement_title": "Contract to be Renewed",
            "expiry_date": add_days(today(), -1), # Expired yesterday
            "division__branch": self.division
        }).insert(ignore_permissions=True)

        # 4. Setup Terms and Conditions Template
        self.template = "Standard Renewal Template"
        if not frappe.db.exists("Terms and Conditions", self.template):
            frappe.get_doc({
                "doctype": "Terms and Conditions",
                "title": self.template,
                "terms": "Renewal terms applied."
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_renewal_generation(self):
        """
        CASE 1: Successful creation of a Renewal Document.
        """
        renewal = frappe.get_doc({
            "doctype": "Auto-Generate Renewal Documents",
            "naming_series": "Auto-Renewal-Doc-",
            "contract_id": self.contract.name,
            "template_used": self.template,
            "generated_date": today(),
            "approval_status": "Open"
        })
        renewal.insert()
        
        self.assertTrue(frappe.db.exists("Auto-Generate Renewal Documents", renewal.name))
        print(f"\n[Positive Test] SUCCESS! Created Renewal ID: {renewal.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Mandatory Field Gap
    # ---------------------------------------------------------
    def test_2_missing_contract_link_gap(self):
        """
        GAP CHECK: Can we generate a renewal without linking a Contract?
        """
        renewal = frappe.get_doc({
            "doctype": "Auto-Generate Renewal Documents",
            "template_used": self.template,
            "generated_date": today()
            # Missing contract_id
        })

        try:
            renewal.insert()
            print("\n[GAP FOUND] System allowed Renewal WITHOUT a Contract ID!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked renewal without Contract.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Missing Template Gap
    # ---------------------------------------------------------
    def test_3_missing_template_gap(self):
        """
        GAP CHECK: Can we renew a contract without selecting a Template?
        """
        renewal = frappe.get_doc({
            "doctype": "Auto-Generate Renewal Documents",
            "contract_id": self.contract.name,
            "generated_date": today()
            # Missing template_used
        })

        try:
            renewal.insert()
            print("\n[GAP FOUND] System allowed Renewal WITHOUT a Template!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked renewal without Template.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Renewal of Valid (Not Expired) Contract
    # ---------------------------------------------------------
    def test_4_renew_active_contract_gap(self):
        """
        GAP CHECK: Does the system allow renewing a contract that hasn't expired yet?
        """
        active_contract = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "agreement_type": self.agreement_type,
            "expiry_date": add_days(today(), 365), # Valid for a year
            "division__branch": self.division
        }).insert(ignore_permissions=True)

        renewal = frappe.get_doc({
            "doctype": "Auto-Generate Renewal Documents",
            "contract_id": active_contract.name,
            "template_used": self.template,
            "generated_date": today()
        })

        try:
            renewal.insert()
            # If it saves, it's a gap. Normally only expiring/expired contracts need renewal.
            print(f"\n[INFO] System allowed renewing an ACTIVE contract ({active_contract.name}).")
        except ValidationError:
            print("\n[SUCCESS] System blocked premature renewal.")

    def tearDown(self):
        frappe.db.rollback()
