# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LotDispatch(Document):

    def on_submit(self):
        create_quality_inspection(self)


def create_quality_inspection(doc):

    # Loop through each row of lot_details
    for row in doc.lot_details:

        # Get Lot document
        lot_doc = frappe.get_doc("Lot", row.lot_id)

        qi = frappe.new_doc("Quality Inspection Dispatch Lot Based")

        # Parent field mapping
        qi.lot_dispatch = doc.name
        qi.dispatch_date = doc.dispatch_date
        qi.division = doc.division
        qi.season = doc.season
        qi.commodity = doc.commodity
        qi.state_agency = doc.state_agency
        qi.state = doc.state
        qi.district = doc.district
        qi.center = doc.center
        qi.society = doc.society
        qi.dispatch_id = doc.name
        qi.lot = row.lot_id
        qi.surveyor__id = row.farmer_id


        # Fetch data from Lot doctype
        qi.item_code = lot_doc.commodity
        qi.qty = lot_doc.lot_qty

        # Save in Draft
        qi.insert(ignore_permissions=True)

    frappe.msgprint("Quality Inspection Dispatch Lot Based documents created successfully.")
