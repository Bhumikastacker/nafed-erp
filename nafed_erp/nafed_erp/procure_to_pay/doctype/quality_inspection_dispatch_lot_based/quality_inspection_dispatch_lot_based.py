# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class QualityInspectionDispatchLotBased(Document):
    def on_submit(self):
        create_purchase_receipt(self)


def create_purchase_receipt(doc):

    # Fetch Lot Dispatch document
    lot_dispatch = frappe.get_doc("Lot Dispatch", doc.dispatch_id)

    # Create Purchase Receipt
    pr = frappe.new_doc("Purchase Receipt")

    # Parent mapping
    pr.supplier = doc.surveyor__id
    pr.division = doc.division
    pr.posting_date = today()

    # Warehouse mapping from Lot Dispatch
    pr.set_warehouse = lot_dispatch.warehouse

    # Loop through Lot Dispatch child table
    for lot in lot_dispatch.lot_details:

        pr.append("items", {
            "item_code": lot_dispatch.commodity,   # item code from commodity
            "qty": lot.lot_quantity,
            "warehouse": lot_dispatch.warehouse,
            "custom_total_dispatch_bags": lot.lot_bags,
            "custom_total_dispatch_qty": lot.lot_quantity
        })

    # Insert Purchase Receipt in Draft
    pr.insert(ignore_permissions=True)

    frappe.msgprint(f"Purchase Receipt {pr.name} created successfully")