# Copyright (c) 2026, CSM Technologies Pvt Ltd
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


# =====================================================
# Legal Case Link DocType Logic
# =====================================================

class LegalCaseLink(Document):

    def before_insert(self):
        self.linked_by = frappe.session.user
        self.link_date = now()
        self.status = self.status or "Active"

    def validate(self):
        self.validate_no_self_link()
        self.validate_no_circular_link()

    def validate_no_self_link(self):
        if self.parent_case == self.child_case:
            frappe.throw("Parent Case and Child Case cannot be the same")

    def validate_no_circular_link(self):
        if is_descendant(self.child_case, self.parent_case):
            frappe.throw(
                f"Circular linkage detected. {self.parent_case} is already a child of {self.child_case}"
            )


# =====================================================
# Utility Functions (MODULE LEVEL)
# =====================================================

def is_descendant(start, target):
    """
    DFS search to detect circular hierarchy
    """
    visited = set()
    stack = [start]

    while stack:
        current = stack.pop()
        if current == target:
            return True
        if current in visited:
            continue
        visited.add(current)

        children = frappe.get_all(
            "Legal Case Link",
            filters={
                "parent_case": current,
                "status": "Active"
            },
            pluck="child_case"
        )
        stack.extend(children)

    return False


def get_related_cases(case_id):
    """
    Get parent + child cases for aggregation
    """
    cases = set([case_id])

    parent = frappe.db.get_value(
        "Legal Case Link",
        {"child_case": case_id, "status": "Active"},
        "parent_case"
    )
    if parent:
        cases.add(parent)

    children = frappe.get_all(
        "Legal Case Link",
        filters={
            "parent_case": case_id,
            "status": "Active"
        },
        pluck="child_case"
    )

    cases.update(children)
    return list(cases)


# =====================================================
# Case Hierarchy
# =====================================================

@frappe.whitelist()
def get_case_hierarchy(case_id):
    parent = frappe.db.get_value(
        "Legal Case Link",
        {"child_case": case_id, "status": "Active"},
        "parent_case"
    )

    children = frappe.get_all(
        "Legal Case Link",
        filters={
            "parent_case": case_id,
            "status": "Active"
        },
        fields=[
            "child_case as case_id",
            "link_type"
        ]
    )

    return {
        "parent": parent,
        "children": children
    }


@frappe.whitelist()
def get_case_timeline(case_id, view_mode="Individual"):
    cases = [case_id]

    if view_mode == "Aggregated":
        cases = get_related_cases(case_id)

    return frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Legal Case Registration",
            "reference_name": ["in", cases]
        },
        fields=[
            "reference_name as case_id",
            "communication_type",
            "subject",
            "content",
            "creation"
        ],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_case_documents(case_id, view_mode="Individual"):
    cases = [case_id]

    if view_mode == "Aggregated":
        cases = get_related_cases(case_id)

    return frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Legal Case Registration",
            "attached_to_name": ["in", cases]
        },
        fields=[
            "file_name",
            "file_url",
            "attached_to_name",
            "creation"
        ],
        order_by="creation desc"
    )
