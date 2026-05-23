import frappe

@frappe.whitelist()
def get_pos_profile_details():

    pos_profile = frappe.db.get_value(
        "POS Profile User",
        {"user": frappe.session.user},
        "parent"
    )

    if not pos_profile:
        return {}

    profile = frappe.get_doc("POS Profile", pos_profile)

    return {
        "warehouse": profile.warehouse,
        "target_warehouse": profile.custom_target_warehouse,
        "store": profile.custom_store
    }