import frappe
from frappe.query_builder.functions import Count
import frappe.permissions

# ---------------
# Halper function
# ---------------


def count_matrix_children(parent,company):
    return frappe.db.count(
        "employee child table",
        {
            "parentfield": "custom_other_reports_to_employee_id",
            "parenttype": "Employee",
            "employee": parent,

        },
    )

def count_reports_to_children(parent,company):
    return frappe.db.count(
        "Employee",
        {
            "reports_to": parent,
            "status": "Active",
            "company":company
        },
    )

def get_total_connections(emp_id):
    return (
        count_matrix_children(emp_id)
        + count_reports_to_children(emp_id)
    )





# ---------------
# Default methood
# ---------------



@frappe.whitelist()
def get_children(parent=None, company=None, exclude_node=None):
    result = []
    user = frappe.session.user

    logged_employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
 

    if not parent:
        if user == "Administrator":
            customfilter = {
                "company": company,
                "status": "Active",
                "reports_to": None,
            }
        else:
            customfilter = {
                "company": company,
                "status": "Active",
                # "reports_to": None,
                "name": logged_employee,
            }

        employees = frappe.get_all(
            "Employee",
            filters=customfilter,
            fields=[
                "name as id",
                "employee_name as name",
                "designation as title",
                "department",
                "image",
                "grade",
            ],
        )

        # print("employees",employees)

        for emp in employees:
            matrix_count = count_matrix_children(emp["id"],company)
            reports_to_count = count_reports_to_children(emp["id"],company)

            total_connections = matrix_count + reports_to_count

            result.append({
                "id": emp["id"],
                "name": emp["name"],
                "title": emp["title"],
                "department":emp["department"],
                "image": emp["image"],
                "grade":emp["grade"],
                "reports_to": None,
                "connections": total_connections,
                "expandable": bool(total_connections),
                "lft": 2,
                "rgt": 8,
            })

        return result

    
    child_ids = list(set(
        frappe.get_all(
            "employee child table",
            filters={
                "parentfield": "custom_other_reports_to_employee_id",
                "parenttype": "Employee",
                "employee": parent,
            },
            pluck="parent",
        )
    ))

    child_ids2 = list(set(
        frappe.get_all(
            "Employee",
            filters={
                "company": company,
                "reports_to": parent,
            },
            pluck="name",
        )
    ))

    
    merged_child_ids = list(child_ids + child_ids2)
    


    if not merged_child_ids:
        return []

    employees = frappe.get_all(
        "Employee",
        filters={
            "company": company,
            "name": ["in", merged_child_ids],
            "status": "Active",
        },
        fields=[
            "name as id",
            "employee_name as name",
            "designation as title",
            "department",
            "image",
            "grade"
        ],
    )

    for emp in employees:
        matrix_count = count_matrix_children(emp["id"],company)
        reports_to_count = count_reports_to_children(emp["id"],company)

        total_connections = matrix_count + reports_to_count

        result.append({
            "id": emp["id"],
            "name": emp["name"],
            "title": emp["title"],
            "department":emp["department"],
            "image": emp["image"],
            "grade":emp["grade"],
            "reports_to": parent,  
            "connections": total_connections,
            "expandable": bool(total_connections),
            "lft": 2,
            "rgt": 8,
        })

    return result
    
    



# ----------
# Expand_all
# ----------


@frappe.whitelist()
def get_children_expand_all(company):
    """
    Fully expanded organizational tree.
    - Handles reports_to + matrix reporting
    - Prevents duplicates
    - Prevents circular loops
    """

    # Cache children lookups for performance
    children_cache = {}

    def get_direct_children(parent):
        if parent in children_cache:
            return children_cache[parent]

        matrix_ids = frappe.get_all(
            "employee child table",
            filters={
                "parentfield": "custom_other_reports_to_employee_id",
                "parenttype": "Employee",
                "employee": parent,
            },
            pluck="parent",
        )

        reports_to_ids = frappe.get_all(
            "Employee",
            filters={
                "reports_to": parent,
                "status": "Active",
            },
            pluck="name",
        )

        children = list(set(matrix_ids) | set(reports_to_ids))
        children_cache[parent] = children
        return children

    def build_tree(parent=None, visited=None):
        if visited is None:
            visited = set()

        result = []

        # ---------------- ROOT LEVEL ----------------
        if parent is None:
            employees = frappe.get_all(
                "Employee",
                filters={
                    "company": company,
                    "status": "Active",
                    "reports_to": None,
                },
                fields=[
                    "name as id",
                    "employee_name as name",
                    "designation as title",
                    "department",
                    "image",
                    "grade",
                ],
            )
        else:
            child_ids = get_direct_children(parent)
            if not child_ids:
                return []

            employees = frappe.get_all(
                "Employee",
                filters={
                    "name": ["in", child_ids],
                    "status": "Active",
                },
                fields=[
                    "name as id",
                    "employee_name as name",
                    "designation as title",
                    "department",
                    "image",
                    "grade",
                ],
            )

        for emp in employees:
            emp_id = emp["id"]

            #  Prevent circular loop (NOT duplication logic)
            if emp_id in visited:
                continue

            next_visited = visited | {emp_id}

            children = build_tree(emp_id, next_visited)

            total_connections = (
                count_matrix_children(emp_id,company)
                + count_reports_to_children(emp_id,company)
            )

            result.append({
                "id": emp_id,
                "name": emp["name"],
                "title": emp["title"],
                "department": emp["department"],
                "image": emp["image"],
                "grade": emp["grade"],
                "reports_to": parent,
                "children": children,
                "connections": total_connections,
                "expandable": bool(total_connections),
            })

        return result

    return build_tree(None)
