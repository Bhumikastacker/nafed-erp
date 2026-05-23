# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import now

class LegalCaseStatusUpdate(Document):

    def before_insert(self):
        self.updated_by = frappe.session.user
        self.update_timestamp = now()

    def after_insert(self):
        """
        1. Update Case Master
        2. Push to timeline
        3. Trigger dashboard refresh
        """
        case = frappe.get_doc("Legal Case Registration", self.case_id)
        case.case_status = self.case_status
        case.save(ignore_permissions=True)

        # Timeline entry
        frappe.get_doc({
            "doctype": "Communication",
            "reference_doctype": "Legal Case Registration",
            "reference_name": self.case_id,
            "communication_type": "Comment",
            "subject": "Case Status Updated",
            "content": f"""

                <b>Status:</b> {self.case_status}<br>
                <b>Remarks:</b><br>{self.description}
            """
        }).insert(ignore_permissions=True)

        # Real-time dashboard refresh
        if self.dashboard_update:
            frappe.publish_realtime(
                event="case_status_updated",
                message={
                    "case_id": self.case_id,
                    "status": self.case_status
                }
            )
