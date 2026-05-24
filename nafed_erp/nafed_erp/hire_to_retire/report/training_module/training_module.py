import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


# ----------------------------------------
# COLUMNS
# ----------------------------------------
def get_columns(filters=None):
    filters = filters or {}

    columns = [
        # ------------------------------
        # Training Requisition
        # ------------------------------
        {
            "label": "Training Requisition",
            "fieldname": "training_requisition",
            "fieldtype": "Link",
            "options": "Training Requisition",
            "width": 160
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },

        # ------------------------------
        # 👉 Trainer (moved next to Status)
        # ------------------------------
        {
            "label": "Trainer",
            "fieldname": "trainer",
            "fieldtype": "Data",
            "width": 120
        },
    ]

    # ----------------------------------
    # 👉 Attendance Summary (next to Status)
    # ----------------------------------
    if not filters.get("expand"):
        columns += [
            {
                "label": "Total Attendees",
                "fieldname": "total_attendees",
                "fieldtype": "Int",
                "width": 120
            },
            {
                "label": "Total Present",
                "fieldname": "total_present",
                "fieldtype": "Int",
                "width": 120
            },
            {
                "label": "Total Absent",
                "fieldname": "total_absent",
                "fieldtype": "Int",
                "width": 120
            }
        ]

    # ------------------------------
    # Remaining Training Fields
    # ------------------------------
    columns += [
        # ------------------------------
        # Learning Path
        # ------------------------------
        {
            "label": "Learning Path",
            "fieldname": "learning_path",
            "fieldtype": "Link",
            "options": "Learning Path",
            "width": 140
        },

        # ------------------------------
        # Meeting
        # ------------------------------
        {
            "label": "Meeting",
            "fieldname": "meeting_id",
            "fieldtype": "Link",
            "options": "Nafed Training Meeting",
            "width": 140
        },
        {
            "label": "Meeting Title",
            "fieldname": "meeting_title",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Meeting Date",
            "fieldname": "meeting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Start Time",
            "fieldname": "start_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": "End Time",
            "fieldname": "end_time",
            "fieldtype": "Time",
            "width": 100
        },
    ]

    # ----------------------------------
    # EXPAND → Employee Level
    # ----------------------------------
    if filters.get("expand"):
        columns += [
            {
                "label": "Employee",
                "fieldname": "employee",
                "fieldtype": "Link",
                "options": "Employee",
                "width": 120
            },
            {
                "label": "Employee Name",
                "fieldname": "employee_name",
                "fieldtype": "Data",
                "width": 160
            },
            {
                "label": "Attendance Status",
                "fieldname": "attendance_status",
                "fieldtype": "Data",
                "width": 120
            },
            {
                "label": "Join Time",
                "fieldname": "join_time",
                "fieldtype": "Datetime",
                "width": 160
            }
        ]

    return columns

# ----------------------------------------
# DATA
# ----------------------------------------
def get_data(filters):
    conditions = ""

    if filters.get("training_requisition"):
        conditions += " AND tr.name = %(training_requisition)s"

    if filters.get("learning_path"):
        conditions += " AND lp.name = %(learning_path)s"

    # =====================================================
    # NON-EXPAND → MEETING SUMMARY
    # =====================================================
    if not filters.get("expand"):
        query = f"""
            SELECT
                tr.name AS training_requisition,
                tr.status,
                lp.name AS learning_path,

                ntm.name AS meeting_id,
                ntm.meeting_title,
                ntm.meeting_date,
                ntm.start_time,
                ntm.end_time,
                ntm.trainer,

                COUNT(nta.name) AS total_attendees,
                SUM(CASE WHEN nta.attendance_status = 'Present' THEN 1 ELSE 0 END) AS total_present,
                SUM(CASE WHEN nta.attendance_status = 'Absent' THEN 1 ELSE 0 END) AS total_absent

            FROM `tabTraining Requisition` tr
            LEFT JOIN `tabLearning Path` lp
                ON lp.requisition = tr.name
            LEFT JOIN `tabNafed Training Meeting` ntm
                ON ntm.learning_path = lp.name
            LEFT JOIN `tabNafed Training Attendee` nta
                ON nta.parent = ntm.name

            WHERE IFNULL(tr.external_type, '') != 'Study Tours'
            {conditions}

            GROUP BY
                tr.name,
                lp.name,
                ntm.name

            ORDER BY
                tr.creation DESC,
                ntm.meeting_date DESC
        """

        return frappe.db.sql(query, filters, as_dict=True)

    # =====================================================
    # EXPAND → EMPLOYEE LEVEL
    # =====================================================
    query = f"""
        SELECT
            tr.name AS training_requisition,
            tr.status,
            lp.name AS learning_path,

            ntm.name AS meeting_id,
            ntm.meeting_title,
            ntm.meeting_date,
            ntm.start_time,
            ntm.end_time,
            ntm.trainer,

            nta.employee,
            nta.employee_name,
            nta.attendance_status,
            nta.join_time

        FROM `tabTraining Requisition` tr
        LEFT JOIN `tabLearning Path` lp
            ON lp.requisition = tr.name
        LEFT JOIN `tabNafed Training Meeting` ntm
            ON ntm.learning_path = lp.name
        LEFT JOIN `tabNafed Training Attendee` nta
            ON nta.parent = ntm.name

        WHERE IFNULL(tr.external_type, '') != 'Study Tours'
        {conditions}

        ORDER BY
            tr.creation DESC,
            ntm.meeting_date DESC,
            ntm.start_time DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)
