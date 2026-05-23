import frappe
from frappe.model.document import Document

class LearningPath(Document):

    # ---------------------------------------
    # VALIDATION — UC-TR-03
    # ---------------------------------------
    def validate(self):

        # Requisition required
        if not self.requisition:
            frappe.throw("Training Requisition is required")

        # Requisition must be Approved
        status = frappe.db.get_value("Training Requisition", self.requisition, "status")
        if status != "Approved":
            frappe.throw("Learning Path can only be created when Training Requisition is Approved")

        # Validate Core Courses
        for c in self.core_courses:
            if not frappe.db.exists("Course", c.course):
                frappe.throw(f"Invalid or Retired Course Selected: {c.course}")

        # Validate Elective Courses
        for e in self.elective_courses:
            if not frappe.db.exists("Course", e.course):
                frappe.throw(f"Invalid or Retired Course Selected: {e.course}")

        # Duplicate sequence check
        order_list = []
        for row in (self.core_courses + self.elective_courses):
            if row.order_no in order_list:
                frappe.throw("Duplicate Course Sequence (UC-TR-03 E2)")
            order_list.append(row.order_no)


    # ---------------------------------------
    # ON UPDATE — Approval handler
    # ---------------------------------------
    def on_update(self):
        if self.status == "Approved":
            self.approval_date = frappe.utils.today()
            frappe.db.set_value(self.doctype, self.name, "approval_date", self.approval_date)
            frappe.msgprint("Learning Path Approved")
