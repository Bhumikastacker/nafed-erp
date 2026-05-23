import frappe

def execute():
    # list all the workspace names you want to hide (not labels)
    workspaces_to_hide = [
        "Home",
        "Overview",
        "Accounting"
        "Employee Lifecycle",
        "Recruitment",
        "Shift & Attendance",
        "Buying",
        "Selling",
        "Leaves",
        "Expense Claims",
        "Stock",
        "Assets",
        "Performance",
        "HR",
        "Manufacturing",
        "Quality"
        "Salary Payout",
        "Tax & Benefits",
        "Projects",
        "Support",
        "Users",
        "Website",
        "Payroll",
        "CRM",
        "Tools",
        "ERPNext Settings",
        "Integrations",
        "Build",
        "ERPNext Integrations"

        # add more as needed
    ]

    for ws in workspaces_to_hide:
        if frappe.db.exists("Workspace", ws):
            frappe.db.set_value("Workspace", ws, "is_hidden", 1)

    frappe.db.commit()
    frappe.clear_cache()
