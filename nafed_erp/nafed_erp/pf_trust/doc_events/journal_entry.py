import frappe

def on_journal_entry_submit(doc, method):
    if not doc.custom_pf_contribution_transfer:
        return

    frappe.db.set_value(
        "PF Contribution Transfer",
        doc.custom_pf_contribution_transfer,
        "journal_entry",
        doc.name
    )
