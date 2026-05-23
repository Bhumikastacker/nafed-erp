# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date

@frappe.whitelist()
def approval_remarks(docname, reason):

    frappe.db.set_value(
        "Member TA DA Request",
        docname,
        "remarks",
        reason
    )

    frappe.db.commit()


class MemberTADARequest(Document):
	def on_update(self):
		print("ssssssssssssssssssssssssssssss", self.status, self.workflow_state)
		if self.workflow_state == "Rejected" and not self.remarks:
		 	frappe.throw("Please enter a Reason for Rejection")
		if self.workflow_state == "Approved" and not self.remarks:
			
			 frappe.throw("Please update the reason for Approval.")
			 
		if 	self.status == 'Draft' and self.meeting_id:
			status = frappe.db.get_value(
				"Board Meeting",
				{"name": self.meeting_id},
				"status"
			)
			if status != 'Agenda Approved':
				frappe.throw("You can  only select the meeting for TA Da only having status Agenda Approved only")
		 

			
	def validate(self):
		self.validate_child_members()

	def validate_child_members(self):
		if not self.members:
		    return

		member_list = []

		for row in self.members:  
		    

		    if self.member_id and row.member == self.member_id:
		        frappe.throw(
		            f"Row #{row.idx}: Child Member ID cannot be same as Parent Member ID ({self.member_id})"
		        )


		    if row.member in member_list:
		        frappe.throw(
		            f"Row #{row.idx}: Member ID {row.member} is already added in Members table"
		        )

		    member_list.append(row.member)
