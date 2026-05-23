import frappe
from frappe.utils import get_datetime, nowdate


def fetch_and_create_employee_checkin():

    # Safe Import
    try:
        import pyodbc
    except ImportError:
        frappe.log_error(
            "pyodbc module not installed",
            "Attendance Sync Error"
        )
        return

    conn = None
    cursor = None
    empl_list = []

    try:

        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=182.74.122.83;"
            "DATABASE=etimetracklite2;"
            "UID=erp;"
            "PWD=Nafed@110011;"
            "TrustServerCertificate=yes;"
        )

        cursor = conn.cursor()

        today = nowdate()

        query = """
            SELECT
                [LogId],
                [EmployeeCode],
                [LogDateTime],
                [DownloadDatenTime],
                [Direction],
                [serialNumber]
            FROM [dbo].[AttendanceLogs2]
            WHERE CAST([LogDateTime] AS DATE) = ?
            ORDER BY [LogId] ASC
        """

        cursor.execute(query, today)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        for row in rows:

            data = dict(zip(columns, row))

            log_id = data["LogId"]
            employee_code = str(data["EmployeeCode"]).strip()
            log_time = get_datetime(data["LogDateTime"])
            device_id = str(data["serialNumber"]).strip()

            direction = str(data["Direction"]).strip().lower()

            log_type = (
                "IN"
                if direction == "in"
                else "OUT"
                if direction == "out"
                else ""
            )

            # Skip invalid direction
            if not log_type:
                continue

            # Employee Validation
            employee = frappe.db.get_value(
                "Employee",
                {
                    "employee_number": employee_code,
                    "status": "Active"
                },
                "name",
            )

            if not employee:
                empl_list.append(employee_code)
                continue

            # Duplicate Check
            if frappe.db.exists(
                "Employee Checkin",
                {
                    "employee": employee,
                    "time": log_time,
                    "device_id": device_id,
                    "log_type": log_type,
                },
            ):
                continue

            raw_details = (
                f"LogId: {log_id}\n"
                f"EmployeeCode: {employee_code}\n"
                f"LogDateTime: {data.get('LogDateTime')}\n"
                f"Direction: {data.get('Direction')}\n"
                f"Serial Number: {device_id}"
            )

            checkin = frappe.new_doc("Employee Checkin")

            checkin.custom_logid = log_id
            checkin.employee = employee
            checkin.time = log_time
            checkin.device_id = device_id
            checkin.log_type = log_type
            checkin.custom_raw_details = raw_details

            print("Creating Checkin For:", employee)

            checkin.insert(ignore_permissions=True)

        # Log Missing Employees
        if empl_list:

            unique_missing = list(set(empl_list))

            frappe.log_error(
                message=f"Employee not found for employee_numbers: {unique_missing}",
                title="Attendance Sync Missing Employees",
            )

        frappe.db.commit()

    except Exception:

        frappe.log_error(
            title="Attendance Sync Failed",
            message=frappe.get_traceback(),
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
