import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Travel Request"),
            "fieldname": "travel_request",
            "fieldtype": "Link",
            "options": "Travel Request",
            "width": 200
        },
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 200
        },
        {
            "label": _("Payment Type"),
            "fieldname": "payment_type",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Employee Advance"),
            "fieldname": "employee_advance",
            "fieldtype": "Link",
            "options": "Employee Advance",
            "width": 200
        },
        {
            "label": _("Total Advance Amount"),
            "fieldname": "advance_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Advance Paid Amount"),
            "fieldname": "advance_paid_amount",
            "fieldtype": "Currency",
            "width": 220
        },
        {
            "label": _("Total Advance Outstanding"),
            "fieldname": "advance_outstanding",
            "fieldtype": "Currency",
            "width": 220
        },
        {
            "label": _("Advance Payment Status"),
            "fieldname": "advance_payment_status",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Expense Claim"),
            "fieldname": "expense_claim",
            "fieldtype": "Link",
            "options": "Expense Claim",
            "width": 200
        },
        {
            "label": _("Total Claimed Amount"),
            "fieldname": "claimed_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Sanctioned Amount"),
            "fieldname": "sanctioned_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Payable Amount"),
            "fieldname": "payable_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Expense Reimbursed"),
            "fieldname": "expense_reimbursed",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Expense Outstanding"),
            "fieldname": "expense_outstanding",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Expense Payment Status"),
            "fieldname": "expense_payment_status",
            "fieldtype": "Data",
            "width": 200
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    travel_requests = frappe.db.sql(
        f"""
        SELECT
            tr.name,
            tr.employee,
            tr.custom_payment_type,
            tr.custom_employee_advance,
            tr.custom_expense_claim
        FROM `tabTravel Request` tr
        WHERE tr.docstatus = 1
        {conditions}
        ORDER BY tr.creation DESC
        """,
        filters,
        as_dict=True
    )

    data = []

    for tr in travel_requests:
        row = {
            "travel_request": tr.name,
            "employee": tr.employee,
            "payment_type": tr.custom_payment_type
        }

        # -------------------------------
        # Employee Advance
        # -------------------------------
        if tr.custom_employee_advance:
            ea = frappe.db.get_value(
                "Employee Advance",
                tr.custom_employee_advance,
                ["advance_amount","paid_amount"],
                as_dict=True
            )

            if ea:
                pending_advance_amount=ea.advance_amount-ea.paid_amount
                row.update({
                    "employee_advance": tr.custom_employee_advance,
                    "advance_amount": ea.advance_amount,
                    "advance_paid_amount": ea.paid_amount,
                    "advance_outstanding": pending_advance_amount
                })

        # -------------------------------
        # Expense Claim
        # -------------------------------
        if tr.custom_expense_claim:
            ec = frappe.db.get_value(
                "Expense Claim",
                tr.custom_expense_claim,
                [
                    "total_claimed_amount",
                    "total_sanctioned_amount",
                    "total_amount_reimbursed",
                    "grand_total"
                ],
                as_dict=True
            )

            if ec:
                outstanding_amount=ec.grand_total-ec.total_amount_reimbursed
                row.update({
                    "expense_claim": tr.custom_expense_claim,
                    "claimed_amount": ec.total_claimed_amount,
                    "sanctioned_amount": ec.total_sanctioned_amount,
                    "payable_amount": ec.grand_total,
                    "expense_outstanding": outstanding_amount,
                    "expense_reimbursed": ec.total_amount_reimbursed
                })

        # -------------------------------
        # Derived Payment Status
        # -------------------------------
        row["advance_payment_status"] = get_advance_payment_status(row)
        row["expense_payment_status"] = get_expense_payment_status(row)


        data.append(row)

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("employee"):
        conditions += " AND tr.employee = %(employee)s"

    if filters.get("payment_type"):
        conditions += " AND tr.custom_payment_type = %(payment_type)s"

    return conditions


def get_advance_payment_status(row):
    if not row.get("employee_advance"):
        return ""

    total = row.get("advance_amount", 0) or 0
    pending = row.get("advance_outstanding", 0) or 0

    if total == 0:
        return "Not Initiated"

    if pending == total:
        return "Not Paid"

    if pending > 0:
        return "Partially Paid"

    return "Paid"


def get_expense_payment_status(row):
    if not row.get("expense_claim"):
        return ""

    reimbursed = row.get("expense_reimbursed", 0) or 0
    payable = row.get("payable_amount", 0) or 0

    if payable == 0:
        return "Not Initiated"

    if reimbursed == 0:
        return "Not Paid"

    if reimbursed < payable:
        return "Partially Paid"

    return "Paid"