import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "State",
            "fieldname": "state",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Total Nominations",
            "fieldname": "total_nominations",
            "fieldtype": "Int",
            "width": 180
        }
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
            state,
            COUNT(name) AS total_nominations
        FROM `tabNominee  Form`
        {where_clause}
        GROUP BY state
        ORDER BY state
    """, values, as_dict=True)

    return columns, data