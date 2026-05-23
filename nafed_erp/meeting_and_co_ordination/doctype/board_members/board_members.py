# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe, re
from frappe.model.document import Document
from datetime import date
from frappe.utils import getdate, today
from frappe import _
import frappe
import re
from frappe.model.document import Document
from frappe.utils import parse_addr, validate_email_address

@frappe.whitelist()
def approval_remarks(docname, reason):

	frappe.db.set_value(
		"Board Members",
		docname,
		"reason",
		reason
	)

	frappe.db.commit()


@frappe.whitelist()
def inactivate_member(docname, reason):
	if not reason:
		frappe.throw("Reason is mandatory")

	frappe.db.sql("""
		UPDATE `tabBoard Members`
		SET reason = %s,
			active = 0
		WHERE name = %s
	""", (reason, docname))

	return {
		"status": "success",
		"message": "Board Member inactivated"
	}


@frappe.whitelist()
def activate_member(docname):
		doc = frappe.get_doc("Board Members", docname)

		doc.active = 1
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		
class BoardMembers(Document):

	


	def validate(self):
		self.validate_email()
		self.validate_mobile()
		self.validate_date_not_past()
		self.landline_validation()
		
		if self.pincode:
			if not re.match(r"^[1-9][0-9]{5}$", self.pincode):
				frappe.throw("PIN Code must be a valid 6-digit number")
				
		if self.rep_name:
			if not re.match(r'^[A-Za-z ]+$', self.rep_name):
				frappe.throw("Rep. Name must contain only letters")
			
		if self.designation:
			if not re.match(r'^[A-Za-z ]+$', self.designation):
				frappe.throw("Designation must contain only letters")
		
		if self.father_name:
			if not re.match(r'^[A-Za-z ]+$', self.father_name):
				frappe.throw("Father Name must contain only letters")
	
	def landline_validation(self):
		if self.landline:

			pattern = r'^(\(?0\d{2,4}\)?[- ]?)?\d{6,8}$'

			if not re.match(pattern, self.landline):
				frappe.throw(_("Invalid landline number. Include STD code."))
		if self.account_number:

			if not re.match(r'^[0-9]{9,18}$', self.account_number):
				frappe.throw(_("Invalid bank account number."))
	
		if self.account_holder_name:

			if not re.match(r'^[A-Za-z .]{2,100}$', self.account_holder_name):
				frappe.throw(_("Invalid account holder name. Use letters only."))
			
	def validate_email(self):
		if self.email:
			# Format check
			email = self.email.strip()
			pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(pattern, self.email):
				frappe.throw("Please enter a valid Email ID")
				
			parsed_email = validate_email_address(email, False)
			if not parsed_email:
				frappe.throw("Please enter a valid Email ID")
				
			domain = self.email.split("@")[-1]
			if domain.count(".") != 1:
				frappe.throw("Please enter a valid Email ID")

			# Duplicate check
			if frappe.db.exists(
				"Board Members",
				{
					"email": self.email,
					"name": ["!=", self.name]
				}
			):
				frappe.throw("Email ID already exists")

	def validate_mobile(self):
		if self.mobile:
			# Indian mobile: 10 digits, starts with 6–9
			if not re.match(r"^[6-9]\d{9}$", self.mobile):
				frappe.throw("Please enter a valid 10-digit Mobile Number")

			# Duplicate check
			if frappe.db.exists(
				"Board Members",
				{
					"mobile": self.mobile,
					"name": ["!=", self.name]
				}
			):
				frappe.throw("Mobile Number already exists")

	def validate_date_not_past(self):
		if self.registartion_date:
			if getdate(self.registartion_date) < getdate(today()):
				frappe.throw("Date cannot be in the past. Please select today or a future date.")

	
	
	
	def on_update(self):
		print("ssssssssssssssssssssssssssssss", self.status, self.workflow_state)
		if self.workflow_state == "Rejected" and not self.reason:
		 	frappe.throw("Please enter a Reason for Rejection")
		elif self.workflow_state == "Approved":
			if not self.reason:
			 	frappe.throw("Please update the reason for Approval.")

			self.assign_membership_no()
			self.check_reason_approval()
		elif self.workflow_state == "Rejected" and self.reason:
			self.check_reason()
		
	def check_reason(self):
		before = self.get_doc_before_save()
		if not before:
			return

		if before.workflow_state == self.workflow_state:
			return

		if not self.reason:
		 	frappe.throw("Please update the reason for Rejection.")
		 	return

		recipients = []
		

		if self.owner:
			recipients.append(self.owner)


		
		if self.email:
			recipients.append(self.email)

		recipients = list(set(recipients))
		
		if not recipients:
			frappe.log_error("No recipients found for Board Member", "MAIL DEBUG")
			return
		email_template = frappe.get_doc("Email Template", "Board Memeber Rejection Mail")

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
		
	def check_reason_approval(self):
		
		

		recipients = []
		

		if self.owner:
			recipients.append(self.owner)


		
		if self.email:
			recipients.append(self.email)

		recipients = list(set(recipients))
		
		if not recipients:
			frappe.log_error("No recipients found for Board Member", "MAIL DEBUG")
			return
		email_template = frappe.get_doc("Email Template", "Board Member Approval")

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

	def assign_membership_no(self):
		# Only when Approved and membership not assigned
		if self.workflow_state != "Approved" or self.membership_no:
			return
		

		settings = frappe.db.get_value(
			"Board Settings",
			{},
			["member_id_from", "current_membership_no"],
			as_dict=True
		)

		if not settings:
			frappe.throw("Board Settings not configured")

		start_no = int(settings.member_id_from or 501)
		current_no = settings.current_membership_no

		next_no = start_no if not current_no else int(current_no) + 1
		print("aaaaaaaaaaaaaaaaaaaaaaaaaaa", next_no)
		# Assign values
		frappe.db.sql("""
		UPDATE `tabBoard Members`
			SET membership_no = %s,
				active = 1
			WHERE name = %s
		""", (next_no, self.name))

		frappe.db.commit()

		





		# Update settings
		frappe.db.set_value(
			"Board Settings",
			{},
			"current_membership_no",
			next_no
		)
		frappe.db.commit()



	def autoname(self):
		prefix = "M"

		today = date.today()
		year = today.year


		state  = frappe.get_doc("State", self.state)
		state = state.state_code

		category = frappe.get_doc("Member Type", self.member_type)
		category = category.short_code
		fy = year

		series = f".####"
		print("aaaaaaaaaaaaa", series, frappe.model.naming.make_autoname(series))
		self.serial_no = frappe.model.naming.make_autoname(series)

	
