import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestSkillGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure a clean state for Skill testing.
        """
        self.skill_name = "Advanced Data Analysis"
        
        # Cleanup existing record to avoid naming conflicts
        if frappe.db.exists("Skill", self.skill_name):
            frappe.delete_doc("Skill", self.skill_name)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_skill_creation(self):
        """
        CASE 1: Verify successful creation of a Skill with valid name and proficiency.
        """
        skill = frappe.get_doc({
            "doctype": "Skill",
            "skill_name": self.skill_name,
            "description": "Ability to analyze complex datasets.",
            "custom_proficiency": 4,
            "custom_evaluation_date": today()
        })
        skill.insert()
        self.assertTrue(frappe.db.exists("Skill", skill.name))
        print(f"\n[Positive Test] SUCCESS! Skill Created: {skill.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Duplicate Skill Name Integrity
    # ---------------------------------------------------------
    def test_gap_1_duplicate_skill_name(self):
        """
        GAP CHECK: Verify if the system allows duplicate skill names.
        Since 'skill_name' is the ID source and unique, it should be blocked.
        """
        # Create first record
        self.test_1_positive_skill_creation()

        # Attempt to create a duplicate
        duplicate = frappe.get_doc({
            "doctype": "Skill",
            "skill_name": self.skill_name,
            "custom_proficiency": 2
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Skill Names!")
        except Exception:
            print("\n[SECURE] System correctly blocked duplicate Skill Name.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Future Evaluation Date
    # ---------------------------------------------------------
    def test_gap_2_future_evaluation_date(self):
        """
        GAP CHECK: Does the system allow an 'Evaluation Date' in the future?
        Logically, a skill evaluation cannot happen in the future.
        """
        future_date = add_days(today(), 365) # 1 year later
        skill = frappe.get_doc({
            "doctype": "Skill",
            "skill_name": "Future Skill Test",
            "custom_evaluation_date": future_date # INVALID
        })

        try:
            skill.insert()
            # If saved, it indicates a logic gap regarding temporal consistency
            print(f"\n[GAP FOUND] System allowed a FUTURE Evaluation Date ({future_date})!")
        except ValidationError:
            print("\n[SECURE] System correctly blocked future evaluation date.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Impossible Rating Value
    # ---------------------------------------------------------
    def test_gap_3_invalid_proficiency_rating(self):
        """
        GAP CHECK: Ratings are usually between 1-5. 
        Does the system allow an impossible value like 99?
        """
        skill = frappe.get_doc({
            "doctype": "Skill",
            "skill_name": "Rating Gap Test",
            "custom_proficiency": 99 # IMPOSSIBLE RATING
        })

        try:
            skill.insert()
            if skill.custom_proficiency > 5:
                print(f"\n[GAP FOUND] System allowed an impossible Proficiency Rating ({skill.custom_proficiency})!")
        except ValidationError:
            print("\n[SECURE] System correctly validated the rating range.")

    def tearDown(self):
        """
        Cleanup: Rollback dummy data.
        """
        frappe.db.rollback()