# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe.utils import parse_addr, validate_email_address
from frappe.model.document import Document


class CoordinationCommunication(Document):
	
	def on_submit(self):
		if not self.submitted_by:
			self.db_set("submitted_by", frappe.session.user)



	def validate(self):
		self.validate_date_not_past()
		print("sssssssssssss", self.status)
		if self.status == 'Send to Division':
			self.send_email_job()
		if self.status == 'Rejected':
			if not self.reason:
		 		frappe.throw("Please update the reason for Rejection.")

	
	def validate_date_not_past(self):
		if self.date:
			if getdate(self.date) < getdate(today()):
				frappe.throw("Date cannot be in the past. " \
				"Please select today or a future date.")
		if self.cc:
			emails = self.cc.split(",")
			for email in emails:
				email = email.strip()
				parsed_email = validate_email_address(email, False)
				print(parsed_email)
				if not parsed_email:
					frappe.throw(_("{0} is not a valid Email Address").format(email))
		

	def send_email_job(self):
		if not self.reason:
		 	frappe.throw("Please update the reason for Approval.")



		attachments = []

		# Get attached files
		files = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": self.doctype,
				"attached_to_name": self.name
			},
			fields=["file_name", "file_url"]
		)

		for f in files:
			file_doc = frappe.get_doc("File", {"file_url": f.file_url})
			attachments.append({
				"fname": f.file_name,
				"fcontent": file_doc.get_content()
			})

		# =========================
		# Get Recipients
		# =========================
		member_list = [
			frappe.db.get_value("User", row.user, "email")
			for row in self.intentend_members if row.user
		]

		if self.cc:
			cc_list = [email.strip() for email in self.cc.split(",") if email.strip()]
			member_list.extend(cc_list)


		# =========================
		# Send Mail
		# =========================
		frappe.sendmail(
			recipients=member_list,
			subject=f"{self.name} Notification",
			message=self.message,
			reference_doctype=self.doctype,
			reference_name=self.name,
			attachments=attachments
		)	
