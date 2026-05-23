# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate
from frappe.utils.xlsxutils import make_xlsx

class StopIncrementPanel(Document):
	pass


@frappe.whitelist()
def get_employees(company, increment_month, effective_date):

    if not company:
        return []

    year = getdate(effective_date).year

    employees = frappe.get_all(
        "Employee",
        filters={
            "company": company,
            "status": "Active"
        },
        fields=["name", "employee_name"]
    )

    data = []

    for emp in employees:

        # ❌ skip already stopped
        if frappe.db.exists("Stop Increment Log", {
            "employee": emp.name,
            "increment_month": increment_month,
            "increment_year": year,
            "docstatus": 1
        }):
            continue

        data.append({
            "employee": emp.name,
            "employee_name": emp.employee_name,
            "stop_increment": 0,
            "reason": ""
        })

    return data


@frappe.whitelist()
def apply_stop_increment(employees, effective_date, increment_month):

    employees = frappe.parse_json(employees)
    year = getdate(effective_date).year

    success = []
    failed = []

    for row in employees:
        try:
            # 🔥 FIX: convert array → dict
            if isinstance(row, list):
                row = {
                    "employee": row[0],
                    "employee_name": row[1],
                    "stop_increment": row[2],
                    "reason": row[3]
                }

            # ✅ skip if not marked
            if not row.get("stop_increment"):
                continue

            employee = row.get("employee")

            # ❌ duplicate check
            if frappe.db.exists("Stop Increment Log", {
                "employee": employee,
                "increment_month": increment_month,
                "increment_year": year,
                "docstatus": 1
            }):
                failed.append({
                    "employee": employee,
                    "error": "Already stopped for this cycle"
                })
                continue

            company = frappe.db.get_value("Employee", employee, "company")

            # ✅ create log
            doc = frappe.get_doc({
                "doctype": "Stop Increment Log",
                "company": company,
                "employee": employee,
                "employee_name": row.get("employee_name"),
                "increment_month": increment_month,
                "increment_year": year,
                "effective_date": effective_date,
                "reason": row.get("reason")
            })

            doc.insert(ignore_permissions=True)
            doc.submit()

            success.append(employee)

        except Exception as e:
            failed.append({
                "employee": row[0] if isinstance(row, list) else row.get("employee"),
                "error": str(e)
            })

    return {
        "success": success,
        "failed": failed
    }

@frappe.whitelist()
def export_stop_increment_report(employees, increment_month=None, effective_date=None):

    employees = frappe.parse_json(employees)

    year = getdate(effective_date).year if effective_date else getdate().year

    data = []

    # 🔥 Header
    data.append([
        "Employee Code",
        "Employee Name",
        "Stop Increment",
        "Reason"
    ])

    for emp in employees:
        data.append([
            emp.get("employee"),
            emp.get("employee_name"),
            emp.get("stop_increment"),
            emp.get("reason") or ""
        ])

    # ⚠️ If no one selected
    if len(data) == 1:
        frappe.throw("No employees selected for stopping increment")

    # ✅ File name
    month = increment_month or "Month"
    file_name = f"Stop Increment Report {month} ({year}).xlsx"

    xlsx_file = make_xlsx(data, "Stop Increment")

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": xlsx_file.getvalue(),
        "is_private": 1
    })
    file_doc.save(ignore_permissions=True)

    return file_doc.file_url