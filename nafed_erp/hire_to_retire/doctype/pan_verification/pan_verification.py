import frappe
from frappe.model.document import Document

from india_compliance.gst_india.doctype.pan.pan import get_pan_status


class PANVerification(Document):

    def before_save(self):
        if not self.user:
            self.user = frappe.session.user
        self.verify_all_pan_numbers()

    def verify_all_pan_numbers(self):
        if not self.pan_details:
            return
        for row in self.pan_details:
            if not row.pan:
                continue
            try:
                result = get_pan_status(row.pan)
                if isinstance(result, tuple):
                    status = result[0]             
            
                elif isinstance(result, dict):
                    msg = result.get("message")
                    status = msg[0] if isinstance(msg, list) else msg    
                else:
                    status = str(result)
                row.status = status

            except Exception as e:
                frappe.log_error(
                    title="PAN Verification Error",
                    message=f"PAN: {row.pan}\nError: {str(e)}"
                )
