import frappe
from frappe.utils import flt
from frappe.utils import getdate
from frappe.utils import today
from frappe.utils import nowdate
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
from frappe.utils import flt
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

def set_encashment_date(doc, method):
    doc.encashment_date = today()

@frappe.whitelist()
def get_component_amount(employee, salary_component):

    if not employee:
        return {"amount": 0}

    assignment = frappe.db.get_value(
        "Salary Structure Assignment",
        {"employee": employee, "docstatus": 1},
        ["name", "salary_structure", "from_date"],
        order_by="from_date desc",
    )

    if not assignment:
        return {"amount": 0}

    assignment_name, structure_name, from_date = assignment

    # Create dummy Salary Slip
    slip = frappe.new_doc("Salary Slip")
    slip.employee = employee
    slip.salary_structure = structure_name
    slip.start_date = from_date
    slip.end_date = from_date
    slip.posting_date = frappe.utils.nowdate()

    # ---- FIX: correctly unpack tuple ----
    data, dependent_components = slip.get_data_for_eval()

    # Find the component row
    structure = frappe.get_doc("Salary Structure", structure_name)

    row = None
    for e in structure.earnings:
        if e.salary_component == salary_component:
            row = e
            break

    if not row:
        return {"amount": 0}

    # Evaluate using ERPNext engine
    amount = slip.eval_condition_and_formula(row, data)

    return {"amount": flt(amount or 0)}


def set_encashment_amount(doc, method=None):
    """Calculate encashment amount before saving (stand-alone function)."""
    # --- DUPLICATE CHECK START ---
    seen_components = []
    if doc.custom_salary_component:
        for row in doc.custom_salary_component:
            if row.salary_component in seen_components:
                frappe.throw(f"Salary Component <b>{row.salary_component}</b> is already added. Duplicates are not allowed.")
            seen_components.append(row.salary_component)

    total_allowances = 0

    # child table = custom_salary_component
    # each row has an 'amount' field
    if doc.custom_salary_component:
        for row in doc.custom_salary_component:
            total_allowances += row.amount or 0

    if not doc.encashment_days:
        frappe.throw("Encashment Days is required to calculate Encashment Amount.")

    doc.encashment_amount = (total_allowances / 30) * doc.encashment_days



@frappe.whitelist()
def get_earnings_salary_components(doctype, txt, searchfield, start, page_len, filters):
    employee = filters.get("employee")
    if not employee:
        return []

    # fetch salary structure assignment for employee
    assignment = frappe.get_value(
        "Salary Structure Assignment",
        {"employee": employee, "docstatus": 1},
        "salary_structure"
    )
    if not assignment:
        return []

    # fetch salary structure earnings table
    earnings = frappe.get_all(
        "Salary Detail",
        filters={"parent": assignment, "parentfield": "earnings"},
        fields=["salary_component"]
    )

    out = []
    for e in earnings:
        out.append((e.salary_component,))

    return out


def set_encashment_year_on_save(doc, method=None):
    # Fetch leave type details
    leave_type = frappe.get_doc("Leave Type", doc.leave_type)

    # Only restrict for earned leaves
    if not leave_type.is_earned_leave:
        return

    # Determine the year from encashment_date
    year = getdate(doc.encashment_date).year

    # Store year (recommended: create hidden field encashment_year)
    doc.custom_encashment_year = year

    # Check if employee has already encashed earned leave this year
    existing = frappe.db.sql("""
        SELECT name
        FROM `tabLeave Encashment`
        WHERE employee = %s
          AND leave_type = %s
          AND custom_encashment_year = %s
          AND docstatus = 1
          AND name != %s
        LIMIT 1
    """, (doc.employee, doc.leave_type, year, doc.name))

    if existing:
        frappe.throw(
            f"Employee <b>{doc.employee}</b> has already encashed an Earned Leave of type {doc.leave_type} in <b>{year}</b>. "
            "Only one encashment is allowed per year."
        )

@frappe.whitelist()
def get_leave_balance(employee, leave_type):
    today = nowdate()
    return get_leave_balance_on(employee, leave_type, today)

