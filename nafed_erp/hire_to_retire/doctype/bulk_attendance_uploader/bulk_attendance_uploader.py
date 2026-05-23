# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
from frappe.model.document import Document
import frappe
import csv
from io import StringIO
from frappe.utils import get_datetime, now_datetime


class BulkAttendanceUploader(Document):
    def on_submit(self):
        start_time = now_datetime()
        try:
            process_attendance_upload(self, None)

            # ---------------------------
            # EXTRA LOGIC (NEW)
            # ---------------------------
            duration = (now_datetime() - start_time).total_seconds()

            self.db_set("status", "File Uploaded Successfully")
            self.db_set("duration", duration)
            self.db_set("uploaded_by", frappe.session.user)
            # ---------------------------

        except Exception as e:
            self.db_set("status", f"Error: {str(e)}")
            self.db_set("uploaded_by", frappe.session.user)
            frappe.log_error(f"Bulk upload failed: {str(e)}")
            raise


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

        att_dir = (row.get("AttDirection") or "").upper()
        if att_dir in ["NULL", "", None]:
            for c in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']:
                val = row.get(c, "").strip().lower()
                if val == "in":
                    att_dir = "IN"
                    break
                elif val == "out":
                    att_dir = "OUT"
                    break

        if att_dir not in ["IN", "OUT"]:
            frappe.log_error(f"Cannot determine direction for row: {row}", "Attendance Upload")
            continue

        try:
            log_datetime = get_datetime(log_date)
        except Exception:
            frappe.log_error(f"Invalid date for {employee_number}: {log_date}", "Attendance Upload")
            continue

        emp_name = frappe.db.get_value("Employee", {"employee_number": employee_number}, "name")
        if not emp_name:
            frappe.log_error(f"Employee not found: {employee_number}", "Attendance Upload")
            continue

        joining_date = frappe.db.get_value("Employee", emp_name, "date_of_joining")
        if joining_date and log_datetime.date() < joining_date:
            frappe.log_error(
                f"Attendance date {log_datetime.date()} cannot be before joining date {joining_date}",
                "Attendance Upload"
            )
            continue

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


# -------------------------------------------------------------------------
# ATTENDANCE GENERATION LOGIC (FIXED INDENTATION)
# -------------------------------------------------------------------------
@frappe.whitelist()
def generate_attendance_for_checkins(docname):
    from hrms.hr.doctype.attendance.attendance import mark_attendance

    doc = frappe.get_doc("Bulk Attendance Uploader", docname)

    file_url = getattr(doc, "file", None)
    if not file_url:
        frappe.throw("No file attached to generate attendance.")

    try:
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        content_str = file_doc.get_content()
    except:
        frappe.throw("Cannot read file.")

    delimiter = '\t' if '\t' in content_str else ','
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

    for emp, dates in employee_dates.items():
        for att_date in dates:

            checkins = frappe.get_all(
                "Employee Checkin",
                filters={
                    "employee": emp,
                    "time": ["between", [
                        f"{att_date} 00:00:00",
                        f"{att_date} 23:59:59"
                    ]]
                },
                fields=["log_type", "time"],
                order_by="time asc"
            )

            if not checkins:
                frappe.log_error(f"No checkins for {emp} on {att_date}", "Attendance Gen")
                continue

            first_in = None
            last_out = None

            for c in checkins:
                if c.log_type == "IN" and first_in is None:
                    first_in = c.time
                if c.log_type == "OUT":
                    last_out = c.time

            try:
                att = frappe.get_doc({
                    "doctype": "Attendance",
                    "employee": emp,
                    "attendance_date": att_date,
                    "status": "Present",
                    "in_time": first_in,
                    "out_time": last_out
                })

                att.insert(ignore_permissions=True)
                att.submit()

            except Exception as e:
                frappe.log_error(
                    f"Error generating attendance for {emp} on {att_date}: {str(e)}",
                    "Attendance Gen"
                )

    return "Attendance generation completed."
