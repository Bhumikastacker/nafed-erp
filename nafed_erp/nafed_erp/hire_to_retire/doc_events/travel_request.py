import re
import frappe
from frappe.utils import nowdate
from frappe.utils import add_years, getdate
from frappe.model.mapper import get_mapped_doc

def fill_submission_date(doc,method):
        # set the custom submission date
        doc.custom_submission_date = nowdate()

        # save the value in database
        doc.db_set("custom_submission_date", nowdate())


# Server Script: Travel Request (Event: Validate)

def parse_duration_to_minutes(duration):
    if not duration:
        return 0

    s = str(duration).strip().lower()
    s = s.replace(u"\u00A0", " ").replace("\t", " ").strip()

    # 24h 0m -> match hours and minutes
    hours = 0
    minutes = 0

    h = re.search(r"(\d+)\s*h", s)
    if h:
        hours = int(h.group(1))

    m = re.search(r"(\d+)\s*m", s)
    if m:
        minutes = int(m.group(1))

    return hours * 60 + minutes


def convert_minutes_to_duration(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m"


def set_total_minutes(doc, method):
    total_minutes = 0

    for row in doc.itinerary:
        if row.custom_travel_duration:
            total_minutes += parse_duration_to_minutes(row.custom_travel_duration)

    doc.custom_total_travel_duration = convert_minutes_to_duration(total_minutes)

def validate_travel_request_ltc_period(doc, method):
    """
    Prevents an employee from creating more than one Travel Request
    within the LTC Period corresponding to the travel_category and posting_date.
    """

    if not doc.employee or not doc.custom_travel_category or not doc.custom_posting_date:
        return  # basic checks

    travel_date = getdate(doc.custom_posting_date)

    # 1️⃣ Get the LTC Period for this travel_category where the travel_date falls within the period
    ltc_period = frappe.get_all(
        "LTC Period",
        filters=[
            ["travel_category", "=", doc.custom_travel_category],
            ["period_start", "<=", travel_date],
            ["period_end", ">=", travel_date]
        ],
        fields=["name", "period_start", "period_end"],
        limit=1
    )

    if not ltc_period:
        frappe.throw(
            f"No LTC Period found for Travel Category '{doc.custom_travel_category}' "
            f"covering the posting date {travel_date}"
        )

    period_start = getdate(ltc_period[0].period_start)
    period_end = getdate(ltc_period[0].period_end)

    # 2️⃣ Check if employee already has a submitted Travel Request in this LTC period
    existing_tr = frappe.get_all(
        "Travel Request",
        filters=[
            ["employee", "=", doc.employee],
            ["custom_travel_category", "=", doc.custom_travel_category],
            ["docstatus", "=", 1],
            ["custom_posting_date", ">=", period_start],
            ["custom_posting_date", "<=", period_end]
        ],
        fields=["name"],
        limit=1
    )

    if existing_tr:
        frappe.throw(
            f"Employee {doc.employee} has already submitted a Travel Request "
            f"for '{doc.custom_travel_category}' in this LTC Period ({period_start} - {period_end})."
        )

def validate_advance_amount(doc,method): 
    if doc.custom_total_advance_amount > doc.custom_total_travel_amount: 
        frappe.throw("Toatal Advance Amount cannot be more than Total Amount.")

@frappe.whitelist()
def create_employee_advance_from_tr(travel_request):
    tr = frappe.get_doc("Travel Request", travel_request)

    # Extra safety: DB check
    existing = frappe.db.exists(
        "Employee Advance",
        {"custom_travel_request": tr.name, "docstatus": ["!=", 2]}
    )
    if existing:
        frappe.throw("Employee Advance already exists for this Travel Request.")

    ea = frappe.new_doc("Employee Advance")
    ea.employee = tr.employee
    ea.exchange_rate = 1  # VERY IMPORTANT
    ea.advance_amount = tr.custom_total_advance_amount
    ea.purpose = f"Travel Advance - {tr.name}"
    ea.custom_travel_request = tr.name
    ea.insert(ignore_permissions=True)
    ea.submit()

    # Save reference back to Travel Request
    frappe.db.set_value(
        "Travel Request",
        tr.name,
        "custom_employee_advance",
        ea.name
    )

    return ea.name


def cancel_linked_employee_advance(doc, method):
    print("Hello world")
    if not doc.custom_employee_advance:
        return

    ea = frappe.get_doc("Employee Advance", doc.custom_employee_advance)
    print("Cancelling employee advance!!")
    # Cancel Employee Advance first
    if ea.docstatus == 1:
        ea.cancel()

    # Clear reference in Travel Request (allowed in on_cancel)
    frappe.db.set_value(
        "Travel Request",
        doc.name,
        "custom_employee_advance",
        None
    )


@frappe.whitelist()
def make_expense_claim_from_travel_request(source_name, target_doc=None):

    def postprocess(source, target, source_parent):
        target.employee = source.employee
        target.custom_travel_request_ = source.name
        target.expense_approver = source.custom_expense_approver
        target.remarks = f"Travel reimbursement for {source.name}"

    def map_costings(source_row, target_row, source_parent):
        target_row.expense_type = source_row.expense_type
        target_row.amount = source_row.total_amount
        target_row.sanctioned_amount = source_row.total_amount

    return get_mapped_doc(
        "Travel Request",
        source_name,
        {
            "Travel Request": {
                "doctype": "Expense Claim",
                "postprocess": postprocess
            },
            "Travel Request Costing": {
                "doctype": "Expense Claim Detail",
                "postprocess": map_costings
            }
        },
        target_doc
    )