# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class GovernmentRequest(Document):	
    pass
	# def validate(self):
	# 	if self.required_quantity <= 0:
	# 		frappe.throw("Quantity must be greater than 0")

	# 	if self.required_by_date < frappe.utils.today():
	# 		frappe.throw("Date cannot be in past")
	# 	existing = frappe.db.exists("Government Request", {
	# 			"requesting_agency": self.requesting_agency,
	# 			"commodity": self.commodity,
	# 			"required_by_date": self.required_by_date
	# 		})
	# 	if existing:
	# 		frappe.throw("Duplicate Request Exists")

@frappe.whitelist()
def make_rfq(source_name, target_doc=None):

    def set_missing_values(source, target):
        target.transaction_date = frappe.utils.nowdate()

    def update_item(source, target, source_parent):
        target.custom_gov_request_id = source_parent.get("gov_request_id") or source_parent.name

    doc = get_mapped_doc(
        "Government Request",
        source_name,
        {
            "Government Request": {
                "doctype": "Request for Quotation"
            },
            "Government Request Item": {
                "doctype": "Request for Quotation Item",
                "field_map": {
                    "seed_name": "item_code",
                    "required_quantity": "qty"
                },
                "postprocess": update_item   # ✅ KEY LINE
            }
        },
        target_doc,
        set_missing_values
    )

    return doc



