import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestMomFromDivision(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Meeting -> Meeting MoM -> Division.
        """
        # 1. Safely get an existing Division ID (Handling typo: divsion_name)
        self.division = frappe.db.get_value("Division", {}, "name")
        if not self.division:
            self.division = "Test Division"
            frappe.db.sql("INSERT INTO `tabDivision` (name, divsion_name) VALUES (%s, %s)", 
                          (self.division, self.division))

        # 2. Get or Create a Meeting MoM ID
        self.mom_no = frappe.db.get_value("Meeting MoM", {}, "name")
        if not self.mom_no:
            # Create a meeting first
            meeting_name = "MEET-MOM-SETUP-001"
            if not frappe.db.exists("Board Meeting", meeting_name):
                frappe.db.sql("INSERT INTO `tabBoard Meeting` (name, status) VALUES (%s, %s)", (meeting_name, "Draft"))
            
            # Create MoM
            mom = frappe.get_doc({
                "doctype": "Meeting MoM",
                "meeting": meeting_name,
                "mom_content": "Main Meeting MoM Setup Content",
                "name": "MOM-SETUP-001"
            }).insert(ignore_permissions=True)
            self.mom_no = mom.name
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_division_mom_creation(self):
        """
        CASE 1: Successful creation of a Mom From Division record.
        """
        div_mom = frappe.get_doc({
            "doctype": "Mom From Division",
            "mom_no": self.mom_no,
            "division": self.division,
            "draft_agenda": "<p>Specific minutes regarding Division targets.</p>",
            "from_user": frappe.session.user
        })
        div_mom.insert()
        
        self.assertTrue(frappe.db.exists("Mom From Division", div_mom.name))
        print(f"\n[Positive Test] SUCCESS! Created Division MoM ID: {div_mom.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Content Gap
    # ---------------------------------------------------------
    def test_2_empty_minutes_content_gap(self):
        """
        GAP CHECK: Can we save division MoM without any text content?
        As per JSON, draft_agenda is reqd: 1.
        """
        div_mom = frappe.get_doc({
            "doctype": "Mom From Division",
            "mom_no": self.mom_no,
            "division": self.division,
            "draft_agenda": "" # INVALID: Empty content
        })

        try:
            div_mom.insert()
            print("\n[GAP FOUND] System allowed saving Mom From Division WITHOUT content!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty division MoM.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Mandatory Link Gap
    # ---------------------------------------------------------
    def test_3_missing_mandatory_links_gap(self):
        """
        GAP CHECK: Can we save without linking a Parent MoM or Division?
        """
        div_mom = frappe.get_doc({
            "doctype": "Mom From Division",
            "draft_agenda": "Minutes text without links"
            # Missing mom_no and division
        })

        try:
            div_mom.insert()
            print("\n[GAP FOUND] System allowed Mom From Division WITHOUT Mandatory Links!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record due to missing links.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Invalid MoM Reference
    # ---------------------------------------------------------
    def test_4_invalid_mom_no_link_gap(self):
        """
        GAP CHECK: Does the system block a non-existent MoM Number?
        """
        div_mom = frappe.get_doc({
            "doctype": "Mom From Division",
            "mom_no": "MOM-GHOST-ID", # INVALID
            "division": self.division,
            "draft_agenda": "Valid content"
        })

        try:
            div_mom.insert()
            print("\n[GAP FOUND] Allowed linking to a non-existent MoM No!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked invalid MoM link.")

    def tearDown(self):
        frappe.db.rollback()