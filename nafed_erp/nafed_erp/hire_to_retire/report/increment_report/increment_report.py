import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Employee Code", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 160},
        {"label": "Pay Scale", "fieldname": "payscale", "fieldtype": "Data", "width": 200},
        {"label": "Old Basic", "fieldname": "old_basic", "fieldtype": "Currency", "width": 120},
        {"label": "New Basic", "fieldname": "new_basic", "fieldtype": "Currency", "width": 120},
        {"label": "Increment Amount", "fieldname": "increment_amount", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = ""

    # ✅ MultiSelect Company Handling
    if filters.get("company"):
        companies = filters.get("company")

        # if coming as JSON string
        if isinstance(companies, str):
            companies = frappe.parse_json(companies)

        conditions += " AND il.company IN %(company)s"
        filters["company"] = tuple(companies)

    # ✅ Month Filter
    if filters.get("month"):
        conditions += " AND il.increment_month = %(month)s"

    # 🔥 Main Query
    data = frappe.db.sql(f"""
        SELECT
            il.employee,
            il.employee_name,
            emp.designation,
            emp.grade,
            il.old_basic,
            il.new_basic,
            il.increment_amount
        FROM `tabIncrement Log` il
        LEFT JOIN `tabEmployee` emp ON emp.name = il.employee
        WHERE il.docstatus = 1
        {conditions}
    """, filters, as_dict=1)

    # 🚀 Optimization: preload all grades (avoid N+1 queries)
    grades = list(set([d.get("grade") for d in data if d.get("grade")]))

    grade_map = {}

    for g in grades:
        grade_doc = frappe.get_doc("Employee Grade", g)

        grade_map[g] = ", ".join([
            str(d.basic_pay)
            for d in grade_doc.get("custom_basic_pays") or []
            if d.basic_pay
        ])

    # 🔥 Attach Pay Scale + Fix Types
    for row in data:
        row["payscale"] = grade_map.get(row.get("grade"), "")

        # Select → string → float
        row["new_basic"] = float(row["new_basic"]) if row.get("new_basic") else 0

    return data