# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe.utils import parse_addr, validate_email_address

@frappe.whitelist()
def approval_remarks(docname, reason):

    frappe.db.set_value(
        "Board Communication",
        docname,
        "reason",
        reason
    )

    frappe.db.commit()


@frappe.whitelist()
def send_board_communication_mail(docname):
    doc = frappe.get_doc("Board Communication", docname)

    if doc.status != "Approved":
        frappe.throw("Mail can be sent only after Approval.")

    doc.send_email_job()

    return "Mail sent successfully"

class BoardCommunication(Document):
	
	def on_submit(self):
		if not self.submitted_by:
			self.db_set("submitted_by", frappe.session.user)



	def validate(self):
		self.validate_date_not_past()
		print("sssssssssssss", self.status)
		if self.status == 'Approved' and not self.reason:
			frappe.throw("Please update the reason for Approval.")
		# if self.status == 'Approved':
		# 	self.send_email_job()
		if self.status == 'Rejected':
			self.check_reason()

   


	def check_reason(self):

		if not self.reason:
		 	frappe.throw("Please update the reason for Rejection.")


		recipients = []
		

		if self.owner:
			recipients.append(self.owner)


		if hasattr(self, "submitted_by") and self.submitted_by:
			email = frappe.db.get_value("User", self.submitted_by, "email")
			if email:
				recipients.append(email)

		recipients = list(set(recipients))
		
		if not recipients:
			frappe.log_error("No recipients found for Board Communication", "MAIL DEBUG")
			return
		email_template = frappe.get_doc("Email Template", "Board Communication Rejection")

		message = frappe.render_template(
			email_template.response,
			{"doc": self}
		)

		frappe.sendmail(
			recipients=recipients,
			subject=email_template.subject,
			message=message,
			reference_doctype=self.doctype,
			reference_name=self.name
		)


	
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
		member_list = [row.email for row in self.intentend_members if row.board_member]

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



