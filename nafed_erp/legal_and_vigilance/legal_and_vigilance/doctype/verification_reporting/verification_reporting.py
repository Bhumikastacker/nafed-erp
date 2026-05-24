# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VerificationReporting(Document):
	pass


@frappe.whitelist()
def create_memo_issuance(verification_reporting_id):
    vr = frappe.get_doc("Verification Reporting", verification_reporting_id)

    memo = frappe.new_doc("Memo Issuance")

    # Core mappings
    memo.ref = vr.name
    memo.issuance_date = vr.date_range,
    memo.complaint_receipt_id = vr.complaint_receipt_id

    # Optional / conditional mappings
    # memo.template_id = vr.complaint_receipt_id
    # memo.deadline = vr.date_range

    memo.insert(ignore_permissions=True)
    frappe.db.commit()

    return memo.name
