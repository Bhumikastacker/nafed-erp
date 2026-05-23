# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt



import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


# ✅ Select Columns Based on Checkbox
def get_columns(filters):
    if filters and filters.get("show_details"):
        return get_detail_columns()
    else:
        return get_summary_columns()


# ✅ ✅ ✅ SUMMARY VIEW (DEFAULT)
def get_summary_columns():
    return [
        {"label": "Job Requisition", "fieldname": "job_requisition", "width": 160},
        {"label": "Designation", "fieldname": "designation", "width": 140},
        {"label": "Department", "fieldname": "department", "width": 140},
        {"label": "No of Positions", "fieldname": "no_of_positions", "width": 120},
        {"label": "Company", "fieldname": "company", "width": 140},

        {"label": "Total Job Openings", "fieldname": "total_openings", "width": 140},
        {"label": "Total Applicants", "fieldname": "total_applicants", "width": 140},
        {"label": "Interview Cleared", "fieldname": "interview_cleared", "width": 140},
        {"label": "Interview Rejected", "fieldname": "interview_rejected", "width": 140},
        {"label": "Converted to Employee", "fieldname": "converted_employee", "width": 160},
    ]


# ✅ ✅ ✅ FULL DETAIL VIEW
def get_detail_columns():
    return [
        {"label": "Job Requisition", "fieldname": "job_requisition", "fieldtype": "Link", "options": "Job Requisition", "width": 150},
        {"label": "Designation", "fieldname": "designation", "width": 120},
        {"label": "Department", "fieldname": "department", "width": 120},
        {"label": "Company", "fieldname": "company", "width": 120},

        {"label": "Job Opening", "fieldname": "job_opening", "fieldtype": "Link", "options": "Job Opening", "width": 150},
        {"label": "Job Opening Status", "fieldname": "job_opening_status", "width": 120},

        {"label": "Applicant Name", "fieldname": "applicant_name", "width": 140},
        {"label": "Applicant Email", "fieldname": "applicant_email", "width": 180},

        {"label": "Interview", "fieldname": "interview", "fieldtype": "Link", "options": "Interview", "width": 140},
        {"label": "Interview Status", "fieldname": "interview_status", "width": 140},

        {"label": "Job Offer", "fieldname": "job_offer", "fieldtype": "Link", "options": "Job Offer", "width": 140},
        {"label": "Job Offer Status", "fieldname": "job_offer_status", "width": 140},

        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "width": 140},
        {"label": "Date of Joining", "fieldname": "date_of_joining", "width": 120}
    ]


def get_data(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " AND jr.company = %(company)s"

    if filters.get("department"):
        conditions += " AND jr.department = %(department)s"

    if filters.get("designation"):
        conditions += " AND jr.designation = %(designation)s"

    # ✅ ✅ ✅ IMPORTANT: ONLY OPEN & APPROVED JOB REQUISITION
    conditions += " AND jr.status IN ('Open & Approved')"


    # ✅ ✅ ✅ SUMMARY QUERY
    if not filters.get("show_details"):
        query = f"""
            SELECT
                jr.name AS job_requisition,
                jr.designation,
                jr.department,
                jr.no_of_positions,
                jr.company,

                COUNT(DISTINCT jo.name) AS total_openings,
                COUNT(DISTINCT ja.name) AS total_applicants,

                SUM(CASE WHEN i.status = 'Cleared' THEN 1 ELSE 0 END) AS interview_cleared,
                SUM(CASE WHEN i.status = 'Rejected' THEN 1 ELSE 0 END) AS interview_rejected,

                COUNT(DISTINCT emp.name) AS converted_employee

            FROM `tabJob Requisition` jr
            LEFT JOIN `tabJob Opening` jo ON jo.job_requisition = jr.name
            LEFT JOIN `tabJob Applicant` ja ON ja.job_title = jo.name
            LEFT JOIN `tabInterview` i ON i.job_applicant = ja.name
            LEFT JOIN `tabEmployee` emp ON emp.job_applicant = ja.name

            WHERE 1=1 {conditions}

            GROUP BY jr.name
            ORDER BY jr.creation DESC
        """
        return frappe.db.sql(query, filters, as_dict=True)


    # ✅ ✅ ✅ FULL DETAIL QUERY
    else:
        query = f"""
            SELECT
                jr.name AS job_requisition,
                jr.designation,
                jr.department,
                jr.company,

                jo.name AS job_opening,
                jo.status AS job_opening_status,

                ja.applicant_name,
                ja.email_id AS applicant_email,

                i.name AS interview,
                i.status AS interview_status,

                jo2.name AS job_offer,
                jo2.status AS job_offer_status,

                emp.name AS employee,
                emp.employee_name,
                emp.date_of_joining

            FROM `tabJob Requisition` jr
            LEFT JOIN `tabJob Opening` jo ON jo.job_requisition = jr.name
            LEFT JOIN `tabJob Applicant` ja ON ja.job_title = jo.name
            LEFT JOIN `tabInterview` i ON i.job_applicant = ja.name
            LEFT JOIN `tabJob Offer` jo2 ON jo2.job_applicant = ja.name
            LEFT JOIN `tabEmployee` emp ON emp.job_applicant = ja.name

            WHERE 1=1 {conditions}

            ORDER BY jr.creation DESC
        """

        return frappe.db.sql(query, filters, as_dict=True)
