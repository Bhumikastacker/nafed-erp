# import frappe
# from frappe.utils import flt

# def fetch_employee_deductions(doc, method):
#     """
#     Fetch deductions from Employee's custom_deduction table
#     and populate in Salary Slip's custom_deductions table
#     """
#     if not doc.employee:
#         return
    
#     # Get employee document
#     employee = frappe.get_doc("Employee", doc.employee)
    
#     # Check if employee has custom_deduction table with data
#     if not employee.get("custom_deduction"):
#         return
    
#     # Clear existing deductions in salary slip
#     doc.set("custom_additional_deductions", [])
    
#     # Copy deductions from employee to salary slip
#     count = 0
#     for row in employee.custom_deduction:
#         if row.get("deduction") and row.get("amount"):
#             doc.append("custom_additional_deductions", {
#                 "deduction": row.deduction,
#                 "amount": row.amount
#             })
#             count += 1
    
#     # Recalculate totals
#     recalculate_totals(doc)
    
#     if count > 0:
#         frappe.msgprint(f"✅ Loaded {count} deduction(s) from employee {employee.employee_name}")
#         from frappe.utils import flt

# def fix_ytd_mtd_after_submit(doc, method):

#     from frappe.utils import flt

#     # total custom deduction
#     custom_total = sum([
#         flt(d.amount) for d in doc.get("custom_additional_deductions", [])
#     ])

#     if not custom_total:
#         return

#     # ✅ set correct values = Net Pay
#     doc.db_set("year_to_date", flt(doc.net_pay))
#     doc.db_set("month_to_date", flt(doc.net_pay))

# def recalculate_totals(doc):
#     """
#     Simple recalculation of total deduction and net pay
#     """
#     # Get standard deductions total
#     standard_deduction_total = sum([d.amount for d in doc.get("deductions", [])])
    
#     # Get custom deductions total
#     custom_deduction_total = sum([d.amount for d in doc.get("custom_additional_deductions", [])])
    
#     # Calculate total deduction (standard + custom)
#     # total_deduction = standard_deduction_total + custom_deduction_total
#     # ✅ INCLUDE LOAN HERE
#     loan_repayment = flt(doc.get("total_loan_repayment"))
    
#     total_deduction = (
#         standard_deduction_total
#         + custom_deduction_total
#         + loan_repayment
#     )
#     # Get gross pay (from earnings)
#     gross_pay = sum([e.amount for e in doc.get("earnings", [])])
    
#     # Calculate net pay
#     net_pay = gross_pay - total_deduction
    
#     # Update the document fields
#     doc.total_deduction = total_deduction
#     doc.net_pay = net_pay
#     doc.rounded_total = net_pay
    
#     # Update base fields if they exist (for multi-currency)
#     if hasattr(doc, 'base_total_deduction'):
#         doc.base_total_deduction = total_deduction
#     if hasattr(doc, 'base_net_pay'):
#         doc.base_net_pay = net_pay
#     if hasattr(doc, 'base_rounded_total'):
#         doc.base_rounded_total = net_pay
    
#     # Update total in words if available
#     if hasattr(doc, 'total_in_words') and doc.total_in_words:
#         from frappe.utils import money_in_words
#         doc.total_in_words = money_in_words(net_pay, doc.currency)

import frappe
from frappe.utils import flt, money_in_words


def fetch_employee_deductions(doc, method):

    if not doc.employee:
        return

    employee = frappe.get_doc("Employee", doc.employee)

    # -------------------------
    # CUSTOM DEDUCTIONS
    # -------------------------

    doc.set("custom_additional_deductions", [])

    deduction_count = 0

    if employee.get("custom_deduction"):

        for row in employee.custom_deduction:

            if row.deduction and row.amount:

                doc.append(
                    "custom_additional_deductions",
                    {
                        "deduction": row.deduction,
                        "amount": row.amount
                    }
                )

                deduction_count += 1


    # -------------------------
    # CUSTOM EARNINGS
    # using your field:
    # custom_salary_earning
    # -------------------------

    doc.set("custom_salary_earning", [])

    earning_count = 0

    if employee.get("custom_salary_earning"):

        for row in employee.custom_salary_earning:

            if row.earning and row.amount:

                doc.append(
                    "custom_salary_earning",
                    {
                        "earning": row.earning,
                        "amount": row.amount
                    }
                )

                earning_count += 1


    # -------------------------
    # RECALCULATE
    # -------------------------

    recalculate_totals(doc)


    if deduction_count or earning_count:

        frappe.msgprint(
            f"Loaded {deduction_count} deductions "
            f"and {earning_count} earnings"
        )


def recalculate_totals(doc):

    # -------------------------
    # STANDARD EARNINGS
    # -------------------------

    standard_earnings_total = sum(
        flt(e.amount)
        for e in doc.get("earnings", [])
    )


    # -------------------------
    # CUSTOM EARNINGS
    # using custom_salary_earning
    # -------------------------

    custom_earnings_total = sum(
        flt(e.amount)
        for e in doc.get("custom_salary_earning", [])
    )


    gross_pay = (
        standard_earnings_total
        + custom_earnings_total
    )


    # -------------------------
    # STANDARD DEDUCTIONS
    # -------------------------

    standard_deduction_total = sum(
        flt(d.amount)
        for d in doc.get("deductions", [])
    )


    # -------------------------
    # CUSTOM DEDUCTIONS
    # -------------------------

    custom_deduction_total = sum(
        flt(d.amount)
        for d in doc.get("custom_additional_deductions", [])
    )


    # -------------------------
    # LOAN REPAYMENT
    # -------------------------

    loan_repayment = flt(
        doc.get("total_loan_repayment")
    )


    total_deduction = (
        standard_deduction_total
        + custom_deduction_total
        + loan_repayment
    )


    # -------------------------
    # NET PAY
    # -------------------------

    net_pay = gross_pay - total_deduction


    doc.gross_pay = gross_pay
    doc.total_deduction = total_deduction
    doc.net_pay = net_pay
    doc.rounded_total = net_pay


    if hasattr(doc, "base_total_deduction"):
        doc.base_total_deduction = total_deduction

    if hasattr(doc, "base_net_pay"):
        doc.base_net_pay = net_pay

    if hasattr(doc, "base_rounded_total"):
        doc.base_rounded_total = net_pay


    if hasattr(doc, "total_in_words"):
        doc.total_in_words = money_in_words(
            net_pay,
            doc.currency
        )


# def fix_ytd_mtd_after_submit(doc, method):

#     value = flt(doc.net_pay)

#     # force correct values
#     doc.db_set("year_to_date", value, update_modified=False)
#     doc.db_set("month_to_date", value, update_modified=False)

#     # also update in memory
#     doc.year_to_date = value
#     doc.month_to_date = value