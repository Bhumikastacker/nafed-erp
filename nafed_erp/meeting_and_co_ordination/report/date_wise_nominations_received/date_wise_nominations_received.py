import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Membership ID", "fieldname": "membership_id", "fieldtype": "Data", "width": 180},
        {"label": "Name", "fieldname": "name1", "fieldtype": "Data", "width": 200},
        {"label": "Contact", "fieldname": "contact", "fieldtype": "Data", "width": 150},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 150},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 150},
        {"label": "Application Received Date", "fieldname": "application_date", "fieldtype": "Date", "width": 180},
        {"label": "AGM Year", "fieldname": "agm_year", "fieldtype": "Data", "width": 120},
    ]

    conditions = []
    values = {}

    if filters.get("application_received_start"):
        conditions.append("application_date >= %(application_received_start)s")
        values["application_received_start"] = filters.get("application_received_start")

    if filters.get("application_received_end"):
        conditions.append("application_date <= %(application_received_end)s")
        values["application_received_end"] = filters.get("application_received_end")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT
            membership_id,
            name1,
            contact,
            state,
            district,
            application_date,
            agm_year
        FROM `tabNominee  Form`
        {where_clause}
        ORDER BY application_date DESC
    """, values, as_dict=True)

    return columns, data