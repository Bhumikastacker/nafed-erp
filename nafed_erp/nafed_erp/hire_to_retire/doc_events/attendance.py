import frappe
from frappe.utils import getdate, get_first_day, cint
from datetime import datetime, time, timedelta
from frappe.utils import add_days


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def convert_to_time(value):
    """Convert timedelta or datetime.time to time."""
    if isinstance(value, time):
        return value

    if isinstance(value, timedelta):
        total = int(value.total_seconds())
        return time(
            hour=total // 3600,
            minute=(total % 3600) // 60,
            second=total % 60
        )

    return value


def get_compensated_end_datetime(attendance, shift):
    """Return compensated cutoff datetime for comparison."""
    compensated = shift.custom_compensated_late_end_time
    if not compensated:
        return None

    comp_time = convert_to_time(compensated)

    # Shift start may also be timedelta
    start_time = convert_to_time(shift.start_time)

    start_dt = datetime.combine(attendance.attendance_date, start_time)
    compensated_dt = datetime.combine(attendance.attendance_date, comp_time)

    # If shift uses timedelta compensation => add to shift start
    if isinstance(compensated, timedelta):
        compensated_dt = start_dt + compensated

    return compensated_dt


def process_leave_rules(doc, method):
    # doc = frappe._dict(doc)  # important
    try:
        # --- Early exits ---
        if not doc.late_entry:
            return
        if not doc.shift:
            return
        if not doc.out_time:
            return

        # Employee company
        emp_company = frappe.db.get_value("Employee", doc.employee, "company")
        if not emp_company:
            return

        # Load shift
        shift = frappe.get_doc("Shift Type", doc.shift)

        # Final cutoff datetime
        cutoff_dt = get_compensated_end_datetime(doc, shift)
        if not cutoff_dt:
            return

        # Employee already compensated → skip
        if doc.out_time >= cutoff_dt:
            return

        # Fetch active rules
        leave_rules = frappe.get_all(
            "Leave Rule",
            filters=dict(
                enable=1,
                company=emp_company,
                shift_type=doc.shift,
                docstatus=1
            ),
            fields=["name", "violations", "leave_type", "deduction_unit"]
        )

        for rule in leave_rules:
                _process_single_rule(doc, rule, cutoff_dt)
    except Exception as e:
        frappe.log_error("Leave Rule Failed", frappe.get_traceback())
        frappe.db.rollback()


# ---------------------------------------------------------
# RULE PROCESSING
# ---------------------------------------------------------

def _process_single_rule(attendance, rule, cutoff_dt):
    """
    Optimized rule processor:
    - Uses cutoff datetime
    - Uses attendance_date instead of month_key
    """
    
    att_date = getdate(attendance.attendance_date)
    month_start = get_first_day(att_date)


    # 1️⃣ Count VALID LATE ENTRIES up to this attendance date
    late_count = frappe.db.count(
        "Attendance",
        filters={
            "employee": attendance.employee,
            "company": attendance.company,
            "docstatus": 1,
            "late_entry": 1,
            "attendance_date": ("between", [month_start, att_date]),
            "out_time": ("<", cutoff_dt),
        }
    )
    frappe.log_error(title="Late Count Debug", message=str(late_count))

    # 2️⃣ Count existing logs within the same month BEFORE this attendance date
    existing = frappe.db.count(
            "Leave Deduction Log",
            filters={
                "employee": attendance.employee,
                "rule": rule.name,
                "company": attendance.company,
                "docstatus": 1,
                "date": ("between", [month_start, add_days(attendance.attendance_date, -1)]),
            }
        )


    # 3️⃣ Determine new logs required
    violations_required = cint(rule.violations)
    expected = late_count // violations_required
    to_create = expected - existing

    if to_create <= 0:
        return

    # 4️⃣ Create missing logs with EXACT attendance_date
    for _ in range(to_create):
        create_leave_deduction_log(attendance, rule)


def create_leave_deduction_log(doc, rule):
    frappe.logger().info("Creating Leave Deduction Log")

    # Fetch company from Employee
    company = frappe.db.get_value("Employee", doc.employee, "company")

    if not rule.deduction_unit:
        frappe.log_error("Missing Deduction Unit", f"Rule: {rule.name}")
        return

    deduction_value = -1 * float(rule.deduction_unit)

    leave_deduction_log = frappe.get_doc({
        "doctype": "Leave Deduction Log",
        "employee": doc.employee,
        "company": company,
        "leave_type": rule.leave_type,
        "rule": rule.name,
        "date": doc.attendance_date,
        "deduction_unit": deduction_value,
        "description": (
            f"Auto deduction triggered due to late entry without compensation. "
            f"IN: {doc.in_time}, OUT: {doc.out_time}"
        ),
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
    })

    try:
        leave_deduction_log.insert(ignore_permissions=True)
        leave_deduction_log.submit()
    except Exception:
        frappe.log_error("Leave Deduction Log Submit Failed", frappe.get_traceback())
