# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestCourse(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestCourseGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure a clean state for Course testing.
        """
        self.course_name = "Python Advanced Programming"
        
        # Cleanup existing record to avoid naming conflicts during the positive test
        if frappe.db.exists("Course", self.course_name):
            frappe.delete_doc("Course", self.course_name)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_course_creation(self):
        """
        CASE 1: Verify successful creation of a Course with valid name and type.
        """
        course = frappe.get_doc({
            "doctype": "Course",
            "course_name": self.course_name,
            "course_type": "Core"
        })
        course.insert()
        self.assertTrue(frappe.db.exists("Course", course.name))
        print(f"\n[Positive Test] SUCCESS! Course Created: {course.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Duplicate Name Integrity
    # ---------------------------------------------------------
    def test_gap_1_duplicate_course_name(self):
        """
        GAP CHECK: Since 'course_name' is used for the ID and marked UNIQUE,
        the system must strictly block duplicate names.
        """
        # Create the first record
        self.test_1_positive_course_creation()

        # Attempt to create a second record with the exact same name
        duplicate = frappe.get_doc({
            "doctype": "Course",
            "course_name": self.course_name,
            "course_type": "Elective"
        })

        try:
            duplicate.insert()
            # If execution reaches here, the database allowed a duplicate ID
            print("\n[GAP FOUND] System allowed DUPLICATE Course Names!")
        except Exception:
            # Successfully blocked by the primary key/unique constraint
            print("\n[SECURE] System correctly blocked duplicate Course Name.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Empty/Blank Name Bypass
    # ---------------------------------------------------------
    def test_gap_2_empty_course_name(self):
        """
        GAP CHECK: Verify if the system allows saving a course with a blank or whitespace name.
        """
        course = frappe.get_doc({
            "doctype": "Course",
            "course_name": "   ", # Only whitespace
            "course_type": "Core"
        })

        try:
            course.insert()
            # If saved, it creates a "hidden" or unreachable record
            if not course.course_name.strip():
                print("\n[GAP FOUND] System allowed saving a Course with a BLANK/WHITESPACE name!")
        except Exception:
            print("\n[SECURE] System blocked blank course name.")

    def tearDown(self):
        """
        Rollback changes to keep the database clean.
        """
        frappe.db.rollback()
