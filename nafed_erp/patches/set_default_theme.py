import frappe

def execute():
    # Theme you want to set for everyone
    theme = "Nafed_erp_theme"
    
    # Update all system users except Administrator & Guest
    users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")

    for user in users:
        frappe.db.set_value("User", user, "desk_theme", theme)

    frappe.db.commit()
    frappe.clear_cache()
