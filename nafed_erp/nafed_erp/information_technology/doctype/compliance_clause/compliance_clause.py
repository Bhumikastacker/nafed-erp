# Copyright (c) 2025, Digitalis Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ComplianceClause(Document):
	pass
    # def on_update(self):
    #     if self.workflow_state == "Draft":
    #         self.db_set("status", "Draft")
    #     if self.workflow_state == "Submitted":
    #         self.db_set("status", "Submitted")
    #     if self.workflow_state == "In Progress":
    #         self.db_set("status", "In Progress")    
    #     if self.workflow_state == "Remediated":
    #         self.db_set("status", "Remediated")
    #     if self.workflow_state == "Validated":
    #         self.db_set("status", "Validated")
    #     if self.workflow_state == "Compliant":
    #         self.db_set("status", "Compliant")

@frappe.whitelist()
def update_complience_status(doctype, docname, status, remarks):
    """
    This function updates the compliance status and remarks for the given document.
    """
    doc = frappe.get_doc(doctype, docname)
    doc.status = status  
    doc.remarks = remarks  
    doc.save()
    frappe.get_doc({
        'doctype': 'Compliance Clause',
        'compliance_clause': doc.name,
        'status': status,
        'remarks': remarks,
        'updated_by': frappe.session.user
    }).insert()

    return "Compliance status updated successfully"