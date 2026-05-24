import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 200
        },
        {
            "label": "Employee ID",
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 140
        },
        {
            "label": "Employee Name",
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "From Date",
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "To Date",
            "fieldname": "end_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "PF Amount",
            "fieldname": "pf_amount",
            "fieldtype": "Currency",
            "width": 140
        }
    ]


def get_data(filters):
    conditions = ""
    values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }

    if filters.get("company"):
        companies = filters.get("company")
        conditions += " AND ss.company IN %(companies)s"
        values["companies"] = tuple(companies)

    return frappe.db.sql(
        f"""
        SELECT
            ss.company,
            ss.employee,
            ss.employee_name,
            ss.start_date,
            ss.end_date,
            SUM(sd.amount) AS pf_amount
        FROM
            `tabSalary Slip` ss
        JOIN
            `tabSalary Detail` sd
            ON sd.parent = ss.name
        WHERE
            ss.docstatus = 1
            AND sd.salary_component IN ('Provident Fund')
            AND ss.start_date >= %(from_date)s
            AND ss.end_date <= %(to_date)s
            {conditions}
        GROUP BY
            ss.company,
            ss.employee,
            ss.employee_name,
            ss.start_date,
            ss.end_date
        ORDER BY
            ss.employee_name
        """,
        values,
        as_dict=True
    )
