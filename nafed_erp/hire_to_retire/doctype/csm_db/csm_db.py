from frappe.model.document import Document
import frappe
import csv
from io import StringIO
from frappe.utils import get_datetime

class CSMDb(Document):
    def on_submit(self):
        process_attendance_upload(self, None)


def process_attendance_upload(doc, method):
    file_url = getattr(doc, "file", None)
    if not file_url:
        frappe.throw("Please attach a CSV file in the File field.")

    try:
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        content_str = file_doc.get_content()
    except Exception as e:
        frappe.throw(f"Failed to read file: {str(e)}")

    delimiter = '\t' if '\t' in content_str else ','
    csv_reader = csv.DictReader(StringIO(content_str), delimiter=delimiter)

    for row in csv_reader:
        employee_number = row.get("UserId") or row.get("EmployeeId")
        log_date = row.get("LogDate")
        device_id = row.get("DeviceId") or ""

        if not employee_number or not log_date:
            continue

        # Determine IN/OUT
        att_dir = (row.get("AttDirection") or "").upper()
        if att_dir in ["NULL", "", None]:  # fallback to C1/C2/C3...
            for c in ['C1','C2','C3','C4','C5','C6','C7']:
                val = row.get(c, "").strip().lower()
                if val == "in":
                    att_dir = "IN"
                    break
                elif val == "out":
                    att_dir = "OUT"
                    break
        if att_dir not in ["IN","OUT"]:
            frappe.log_error(f"Cannot determine direction for row: {row}", "Attendance Upload")
            continue

        # Convert log date to datetime
        try:
            log_datetime = get_datetime(log_date)
        except Exception as e:
            frappe.log_error(f"Invalid date for {employee_number}: {log_date}", "Attendance Upload")
            continue

        # Map to Employee
        emp_name = frappe.db.get_value("Employee", {"employee_number": employee_number}, "name")
        if not emp_name:
            frappe.log_error(f"Employee not found: {employee_number}", "Attendance Upload")
            continue

        # Check joining date
        joining_date = frappe.db.get_value("Employee", emp_name, "date_of_joining")
        if joining_date and log_datetime.date() < joining_date:
            frappe.log_error(
                f"Attendance date {log_datetime.date()} cannot be less than employee {employee_number}'s joining date: {joining_date}",
                "Attendance Upload"
            )
            continue

        # Insert Employee Checkin
        try:
            frappe.get_doc({
                "doctype": "Employee Checkin",
                "employee": emp_name,
                "log_type": att_dir,
                "time": log_datetime,
                "device_id": device_id
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error inserting checkin for {employee_number}: {str(e)}", "Attendance Upload")


import frappe
from hrms.hr.doctype.attendance.attendance import mark_attendance
from frappe.utils import getdate

@frappe.whitelist()
def generate_attendance_for_checkins(docname):
    doc = frappe.get_doc("CSM Db", docname)

    # Collect all employees/dates from Employee Checkin linked to this upload
    file_url = getattr(doc, "file", None)
    if not file_url:
        frappe.throw("No file attached to generate attendance.")

    file_doc = frappe.get_doc("File", {"file_url": file_url})
    content_str = file_doc.get_content()
    delimiter = '\t' if '\t' in content_str else ','
    import csv
    from io import StringIO
    csv_reader = csv.DictReader(StringIO(content_str), delimiter=delimiter)

    employee_dates = {}

    for row in csv_reader:
        employee_number = row.get("UserId") or row.get("EmployeeId")
        log_date = row.get("LogDate")
        if not employee_number or not log_date:
            continue

        emp_name = frappe.db.get_value("Employee", {"employee_number": employee_number}, "name")
        if not emp_name:
            continue

        log_datetime = frappe.utils.get_datetime(log_date)
        if emp_name not in employee_dates:
            employee_dates[emp_name] = set()
        employee_dates[emp_name].add(log_datetime.date())

    # Now generate attendance
    for emp, dates in employee_dates.items():
        for att_date in dates:
            try:
                mark_attendance(emp, att_date, "Present")
            except Exception as e:
                frappe.log_error(f"Error generating attendance for {emp} on {att_date}: {str(e)}")

    return "Attendance generation completed."
