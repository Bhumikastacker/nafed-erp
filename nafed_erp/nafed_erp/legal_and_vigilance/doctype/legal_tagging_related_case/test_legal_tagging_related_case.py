# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalTaggingRelatedCase(FrappeTestCase):
# 	pass


# =====================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestLegalTaggingRelatedCase(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies with explicit ID naming for Masters.
        """
        self.jurisdiction = "Delhi High Court"
        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            frappe.get_doc({"doctype": "Jurisdiction", "name1": self.jurisdiction, "name": self.jurisdiction}).insert(ignore_permissions=True)

        self.branch = "Head Office"
        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({"doctype": "Branch", "branch_name": self.branch, "name": self.branch}).insert(ignore_permissions=True)

        # 1. Register Case
        self.case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": f"TAG-REF-{frappe.generate_hash(length=4)}",
            "party_name": "Tagging Test Party",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-TAG",
            "agreement_type": "A"
        }).insert(ignore_permissions=True)

        # 2. Setup Tag Type
        self.tag_type = "Criminal"
        if not frappe.db.exists("Tag Type", self.tag_type):
            frappe.get_doc({"doctype": "Tag Type", "name": self.tag_type}).insert(ignore_permissions=True)

        # 3. Setup Risk Category (Forcing ID as 'High')
        self.risk = "High"
        if not frappe.db.exists("Risk Category", self.risk):
            frappe.get_doc({
                "doctype": "Risk Category", 
                "name": self.risk,
                "risk_category": self.risk # assuming fieldname is same as doctype label
            }).insert(ignore_permissions=True)

        # 4. Setup Stage (Forcing ID as 'Initial')
        self.stage = "Initial"
        if not frappe.db.exists("Stage", self.stage):
            frappe.get_doc({
                "doctype": "Stage", 
                "name": self.stage,
                "stage": self.stage # assuming fieldname is same as doctype label
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_tagging_creation(self):
        """
        CASE 1: Successful creation of a Legal Tagging record.
        """
        tag = frappe.get_doc({
            "doctype": "Legal Tagging Related Case",
            "case_id": self.case.name,
            "tag_type": self.tag_type,
            "risk_category": self.risk,
            "applied_date": today(),
            "applied_by": frappe.session.user,
            "stage": self.stage
        })
        tag.insert()
        
        self.assertTrue(frappe.db.exists("Legal Tagging Related Case", tag.name))
        print(f"\n[Positive Test] SUCCESS! Created Tag ID: {tag.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Missing Mandatory Fields
    # ---------------------------------------------------------
    def test_2_missing_mandatory_masters_gap(self):
        """
        GAP CHECK: Can we save a tag without Risk Category or Stage?
        """
        tag = frappe.get_doc({
            "doctype": "Legal Tagging Related Case",
            "case_id": self.case.name,
            "tag_type": self.tag_type,
            "applied_date": today(),
            "applied_by": frappe.session.user
            # Missing risk_category and stage
        })

        try:
            tag.insert()
            print("\n[GAP FOUND] System allowed Tagging without Risk Category or Stage!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked tagging due to missing mandatory links.")

    # ---------------------------------------------------------
    # 3. Behavioral Test Case: Duplicate Tagging Gap
    # ---------------------------------------------------------
    def test_3_duplicate_tagging_gap(self):
        """
        GAP CHECK: Can the same case be tagged with the exact same Tag Type twice?
        """
        data = {
            "doctype": "Legal Tagging Related Case",
            "case_id": self.case.name,
            "tag_type": self.tag_type,
            "risk_category": self.risk,
            "applied_date": today(),
            "applied_by": frappe.session.user,
            "stage": self.stage
        }
        
        # First tag
        frappe.get_doc(data).insert()

        # Second tag attempt (Same Case, Same Type)
        duplicate = frappe.get_doc(data)
        try:
            duplicate.insert()
            # If saved, it's a gap. A case should usually have one record per tag type at a time.
            print("\n[GAP FOUND] System allowed DUPLICATE Tagging for the same Case and Type!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate tagging.")

    def tearDown(self):
        frappe.db.rollback()