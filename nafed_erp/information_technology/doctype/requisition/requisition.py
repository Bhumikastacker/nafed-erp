# Copyright (c) 2025, CSM Technologies Pvt Ltd
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Requisition(Document):

    def on_update(self):
        if self.workflow_state == "Draft":
            self.db_set("status", "Draft")

        elif self.workflow_state == "Submitted":
            self.db_set("status", "Submitted")

        elif self.workflow_state == "Revert":
            self.db_set("status", "Draft")

        elif self.post_facto_purchase and self.workflow_state == "Submitted":
            self.db_set("status", "Submitted Post Facto")

        elif self.workflow_state == "Validated":
            self.db_set("status", "Validated")

        elif self.workflow_state == "Approved":
            self.db_set("status", "Approved")
            self.notify_it_team()

        elif self.workflow_state == "Rejected":
            self.db_set("status", "Rejected")

        if not self.requested_by:
            self.db_set("requested_by", frappe.session.user)
            self.db_set("request_date", frappe.utils.nowdate())

    def notify_it_team(self):
        it_users = frappe.get_all(
            "Has Role",
            filters={"role": "HO IT Division"},
            pluck="parent"
        )
        if not it_users:
            return
        items_html = ""
        for item in self.items:
            items_html += f"""
            <tr>
                <td>{item.item_name}</td>
                <td>{item.quantity}</td>
                <td>{item.required_by or ''}</td>
            </tr>
            """
        subject = f"IT Requisition Approved | {self.name}"
        message = f"""
        <p>Dear Team,</p>
        <p>The following <b>IT Requisition has been Approved</b>. Please initiate further processing.</p>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr><td><b>Requisition ID</b></td><td>{self.name}</td></tr>
            <tr><td><b>Requested By</b></td><td>{self.requester_name}</td></tr>
            <tr><td><b>Branch / Location</b></td><td>{self.branchlocation}</td></tr>
            <tr><td><b>Priority</b></td><td>{self.priority}</td></tr>
            <tr><td><b>Mode of Requisition</b></td><td>{self.mode_of_requisition}</td></tr>
            <tr><td><b>Post-Facto Purchase</b></td><td>{"Yes" if self.post_facto_purchase else "No"}</td></tr>
            <tr><td><b>Purpose</b></td><td>{self.purpose or '-'}</td></tr>
        </table>
        <br>
        <b>Requested Items</b>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Description</th>
            </tr>
            {items_html}
        </table>
        <br>
        <p>Please log in to ERPNext for further action.</p>
        """
        frappe.sendmail(
            recipients=it_users,
            subject=subject,
            message=message,
            reference_doctype=self.doctype,
            reference_name=self.name
        )
        for user in it_users:
            frappe.publish_realtime(
                event="notification",
                message={
                    "title": "IT Requisition Approved",
                    "description": f"Requisition {self.name} is approved and pending IT action.",
                    "doctype": self.doctype,
                    "docname": self.name,
                },
                user=user
            )
