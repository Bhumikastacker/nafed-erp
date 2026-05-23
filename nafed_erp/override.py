import frappe


@frappe.whitelist()
def switch_theme(theme):
	if theme in ["Dark", "Light", "Automatic", "Nafed_erp_theme"]:
		frappe.db.set_value("User", frappe.session.user, "desk_theme", theme)


import frappe
from frappe import _
from frappe.query_builder.functions import Count

@frappe.whitelist()
def get_children1(parent=None, company=None, exclude_node=None):
    filters = [["status", "=", "Active"]]

    if company and company != "All Companies":
        filters.append(["company", "=", company])

    if parent and company and parent != company:
        filters.append(["reports_to", "=", parent])
    else:
        filters.append(["reports_to", "=", ""])

    if exclude_node:
        filters.append(["name", "!=", exclude_node])

    employees = frappe.get_all(
        "Employee",
        fields=[
            "employee_name as name",
            "name as id",
            "lft",
            "rgt",
            "reports_to",
            "image",
            "designation as title",
            "custom_division",
            "grade"
        ],
        filters=filters,
        order_by="name",
    )

    for employee in employees:
        employee["connections"] = get_connections(employee["id"], employee["lft"], employee["rgt"])
        employee["expandable"] = bool(employee["connections"])
        # employee["custom_division"] = employee["custom_division"]
        # employee["grade"] = employee["grade"]
        

    return employees


def get_connections(employee: str, lft: int, rgt: int) -> int:
    Employee = frappe.qb.DocType("Employee")
    query = (
        frappe.qb.from_(Employee)
        .select(Count(Employee.name))
        .where(
            (Employee.lft > lft)
            & (Employee.rgt < rgt)
            & (Employee.status == "Active")
        )
    ).run()

    return query[0][0]


import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_all_nodes1(method, company=None):
    """Recursively gets all nodes with custom fields from Employee table"""

    # Get the method dynamically
    method = frappe.get_attr(method)

    if method not in frappe.whitelisted:
        frappe.throw(_("Not Permitted"), frappe.PermissionError)

    result = []
    nodes_to_expand = []

    # Fetch root nodes (parent=None)
    root_nodes = method(parent=None, company=company)

    for root in root_nodes:
        parent_id = root.get("id")
        # Fetch children nodes dynamically
        children = method(parent=parent_id, company=company) if parent_id else []

        # Inject custom fields
        for child in children:
            # Fetch Employee doc for this node to get actual custom fields
            try:
                emp_doc = frappe.get_doc("Employee", child.get("id"))
                child["custom_division"] = emp_doc.custom_division or "N/A"
                child["grade"] = emp_doc.grade or "N/A"
                child["reports_to"] = emp_doc.reports_to or "N/A"
            except frappe.DoesNotExistError:
                child["custom_division"] = "N/A"
                child["grade"] = "N/A"
                child["reports_to"] = "N/A"

            # Mark expandable if they have children
            child["expandable"] = bool(child.get("connections", 0))

        result.append({
            "parent": parent_id,
            "parent_name": root.get("name"),
            "data": children
        })

        # Add expandable nodes to queue for recursive expansion
        nodes_to_expand.extend([{"id": d.get("id"), "name": d.get("name")} for d in children if d.get("expandable")])

    # Recursively expand all nodes
    while nodes_to_expand:
        parent = nodes_to_expand.pop(0)
        parent_id = parent.get("id")
        children = method(parent=parent_id, company=company)

        for child in children:
            try:
                emp_doc = frappe.get_doc("Employee", child.get("id"))
                child["custom_division"] = emp_doc.custom_division or "N/A"
                child["grade"] = emp_doc.grade or "N/A"
                child["reports_to"] = emp_doc.reports_to or "N/A"
            except frappe.DoesNotExistError:
                child["custom_division"] = "N/A"
                child["grade"] = "N/A"
                child["reports_to"] = "N/A"

            child["expandable"] = bool(child.get("connections", 0))

        result.append({
            "parent": parent_id,
            "parent_name": parent.get("name"),
            "data": children
        })

        nodes_to_expand.extend([{"id": d.get("id"), "name": d.get("name")} for d in children if d.get("expandable")])

    return result

@frappe.whitelist(allow_guest=True)
def get_link_title_guest(doctype, docname):
    if not frappe.db.exists(doctype, docname):
        return ""

    return frappe.db.get_value(doctype, docname, "name")