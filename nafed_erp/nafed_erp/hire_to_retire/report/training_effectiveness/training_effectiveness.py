import frappe

def execute(filters=None):
    columns = [
        {"label":"Meeting","fieldname":"meeting","fieldtype":"Link","options":"Nafed Training Meeting","width":200},
        {"label":"Trainer","fieldname":"trainer","fieldtype":"Data","width":150},
        {"label":"Date","fieldname":"meeting_date","fieldtype":"Date","width":120},
        {"label":"Aggregated Score","fieldname":"custom_aggregated_score","fieldtype":"Float","width":150},
    ]

    data = frappe.db.sql("""
        SELECT
            name AS meeting,
            trainer AS trainer,
            meeting_date,
            custom_aggregated_score
        FROM `tabNafed Training Meeting`
        WHERE docstatus = 1
        ORDER BY meeting_date DESC
    """, as_dict=1)

    return columns, data
