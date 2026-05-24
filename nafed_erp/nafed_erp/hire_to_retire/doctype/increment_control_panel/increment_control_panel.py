import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate
from frappe.utils import nowdate, getdate
from frappe.utils.xlsxutils import make_xlsx
class IncrementControlPanel(Document):
	pass

@frappe.whitelist()
def get_employees(company, effective_date, increment_month):

    if not company or not effective_date or not increment_month:
        return []

    increment_year = getdate(effective_date).year

    employees = frappe.get_all(
        "Employee",
        filters={
            "company": company,
            "status": "Active"
        },
        fields=["name", "employee_name", "custom_basic_pay", "grade"]
    )

    data = []

    for emp in employees:

        # -----------------------------
        # ❌ SKIP IF INCREMENT STOPPED
        # -----------------------------
        if is_increment_stopped(emp.name, increment_month, increment_year):
            continue


        # -----------------------------
        # ❌ SKIP IF ALREADY INCREMENTED
        # -----------------------------
        already_done = frappe.db.exists(
            "Increment Log",
            {
                "employee": emp.name,
                "increment_month": increment_month,
                "increment_year": increment_year,
                "docstatus": 1
            }
        )

        if already_done:
            continue


        # -----------------------------
        # CURRENT BASIC
        # -----------------------------
        current_basic = flt(emp.custom_basic_pay)


        # -----------------------------
        # LAST INCREMENT
        # -----------------------------
        last_increment = frappe.db.get_value(
            "Increment Log",
            {
                "employee": emp.name,
                "docstatus": 1,
                "effective_date": ("<", effective_date)
            },
            "increment_amount",
            order_by="effective_date desc"
        ) or 0


        # -----------------------------
        # GRADE BASED OPTIONS
        # -----------------------------
        basic_pay_options = []

        if emp.grade:
            grade_doc = frappe.get_doc("Employee Grade", emp.grade)

            for d in grade_doc.custom_basic_pays:
                basic = flt(d.basic_pay)

                if basic > current_basic:
                    basic_pay_options.append(basic)


        # -----------------------------
        # FINAL DATA
        # -----------------------------
        data.append({
            "employee": emp.name,
            "employee_name": emp.employee_name,
            "current_basic": current_basic,
            "last_increment": last_increment,
            "new_basic": current_basic,
            "basic_pay_options": sorted(basic_pay_options)
        })

    return data


@frappe.whitelist()
def apply_increment(employees, effective_date, increment_month):

    employees = frappe.parse_json(employees)
    increment_year = getdate(effective_date).year
    success = []
    failed = []

    for row in employees:
        try:
            employee = row.get("employee")
            current_basic = flt((row.get("current_basic") or 0))
            new_basic = flt((row.get("new_basic") or 0))

            if not employee:
                continue

            if not new_basic:
                continue

            if new_basic <= current_basic:
                failed.append({
                    "employee": employee,
                    "error": "New Basic must be greater than Current Basic"
                })
                continue

            # ❌ duplicate increment check
            if already_incremented(employee, increment_month, increment_year):
                failed.append({
                    "employee": employee,
                    "error": "Already incremented for this cycle"
                })
                continue

            # -----------------------------
            # CALCULATE (Backend truth)
            # -----------------------------
            increment_amount = new_basic - current_basic

            if increment_amount <= 0:
                failed.append({
                    "employee": employee,
                    "error": "Invalid increment amount"
                })
                continue
            # -----------------------------
            # LOG
            # -----------------------------
            create_increment_log(
                employee=employee,
                effective_date=effective_date,
                old_basic=current_basic,
                new_basic=new_basic,
                increment_amount=increment_amount,
                increment_month=increment_month,
                increment_year=increment_year
            )

            success.append(employee)

        except Exception as e:
            failed.append({
                "employee": row.get("employee"),
                "error": str(e)
            })

    return {
        "success": success,
        "failed": failed
    }


def already_incremented(employee, increment_month, increment_year):

    return frappe.db.exists(
        "Increment Log",
        {
            "employee": employee,
            "increment_month": increment_month,
            "increment_year": increment_year,
            "docstatus":1
        }
    )

def create_increment_log(
    employee,
    effective_date,
    old_basic,
    new_basic,
    increment_amount,
    increment_month,
    increment_year
):

    company = frappe.db.get_value("Employee", employee, "company")

    doc = frappe.get_doc({
        "doctype": "Increment Log",
        "company": company,
        "employee": employee,
        "effective_date": effective_date,
        "increment_month": increment_month,
        "increment_year": increment_year,
        "old_basic": old_basic,
        "increment_amount": increment_amount,
        "new_basic": new_basic
    })

    doc.insert(ignore_permissions=True)
    doc.submit()
    

def is_increment_stopped(employee, increment_month, increment_year):

    return frappe.db.exists(
        "Stop Increment Log",
        {
            "employee": employee,
            "increment_month": increment_month,
            "increment_year": increment_year,
            "docstatus": 1
        }
    )

@frappe.whitelist()
def export_increment_report(employees, increment_month, effective_date):

    employees = frappe.parse_json(employees)
    # ✅ Get current year
    current_year = getdate(effective_date).year

    data = []

    # Header
    data.append([
        "Employee Code",
        "Employee Name",
        "Current Basic",
        "New Basic",
        "Increment"
    ])

    for emp in employees:
        current_basic = float(emp.get("current_basic") or 0)
        new_basic = float(emp.get("new_basic") or 0)

        data.append([
            emp.get("employee"),
            emp.get("employee_name"),
            current_basic,
            new_basic,
            new_basic - current_basic
        ])

    # ✅ Dynamic file name
    month = increment_month or "Month"
    file_name = f"Increment_Report_{month}_{current_year}.xlsx"

    xlsx_file = make_xlsx(data, "Increment Report")

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": xlsx_file.getvalue(),
        "is_private": 1
    })
    file_doc.save(ignore_permissions=True)

    return file_doc.file_url