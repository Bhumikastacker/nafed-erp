import frappe
from frappe.utils import today, getdate

def get_department_head_user(department):
    """
    Try to read a custom field `department_head` from Department doctype.
    If not present, fallback to any User with role 'Department Head' (first found).
    """
    try:
        head = frappe.get_value('Department', department, 'department_head')
        if head:
            return head
    except Exception:
        pass

    rows = frappe.get_all('Has Role', filters={'role':'Department Head'}, fields=['parent'])
    if rows:
        return rows[0].parent
    return None

def get_utilization(department, category, date_from, date_to):
    """
    Simple GL-based utilization. IMPORTANT: adapt this SQL to your ERPNext GL schema.
    By default we attempt to sum debit for expense accounts linked to a cost_center == department.
    """
    if not date_from:
        date_from = '1970-01-01'
    if not date_to:
        date_to = today()

    # Adjust this SQL -> many ERPNext installs use `tabGL Entry` or `tabAccount` differenly.
    # Most robust approach: use cost_center field mapping. If you use cost_center for department,
    # replace 'cost_center' filter accordingly.
    try:
        res = frappe.db.sql("""
            SELECT COALESCE(SUM(debit - credit), 0) AS utilized
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %(from)s AND %(to)s
            AND IFNULL(cost_center, '') = %(dept)s
        """, {"from": date_from, "to": date_to, "dept": department}, as_dict=1)
        utilized = res[0].utilized if res else 0.0
    except Exception:
        # Fallback: no GL Entry table or different schema
        utilized = 0.0

    return float(utilized)

def create_budget_allocation(budget_request_name):
    """
    Create Budget Allocation doc from Budget Request.
    If allocation exists, do nothing.
    """
    br = frappe.get_doc('Budget Request', budget_request_name)
    # avoid duplicates
    exists = frappe.db.exists('Budget Allocations', {'budget_request': br.name})
    if exists:
        return exists

    alloc = frappe.new_doc('Budget Allocations')
    alloc.budget_request = br.name
    alloc.department = br.department
    alloc.category = br.category
    alloc.allocated_amount = flt(br.approved_amount or br.amount, 2)
    alloc.allocation_date = today()
    alloc.utilized_amount = get_utilization(br.department, br.category, br.start_date, br.end_date)
    alloc.remaining_amount = alloc.allocated_amount - alloc.utilized_amount
    alloc.insert()
    alloc.submit() if hasattr(alloc, 'submit') else alloc.save()
    return alloc.name

def flt(val, precision=2):
    try:
        return round(float(val), precision)
    except:
        return 0.0
