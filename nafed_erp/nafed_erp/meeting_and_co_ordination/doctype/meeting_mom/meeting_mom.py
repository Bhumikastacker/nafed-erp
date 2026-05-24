import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today



@frappe.whitelist()
def send_configured_mail(docname):
		doc = frappe.get_doc("Meeting MoM", docname)

		name = doc.name
		message = doc.mom_content

		# Convert comma-separated emails into list
		to_list = []
		cc_list = []
		division_list = frappe.get_all(
			"Mom From Division",
			filters={"mom_no": name},
			pluck="division"
		)

		# Prepare filters
		filters = {
			"doc_type": "Mom"
		}

		# Apply division filter only if list exists
		if division_list:
			filters["division"] = ["not in", division_list]

		# Fetch Mail Configurations
		records = frappe.get_all(
			"Mails Configurations",
			filters=filters,
			fields=["emails_to", "emails_cc"]
		)
		emails_to = []
		emails_cc = []

		for row in records:
			if row.emails_to:
				emails_to.extend([e.strip() for e in row.emails_to.split(",") if e.strip()])

			if row.emails_cc:
				emails_cc.extend([e.strip() for e in row.emails_cc.split(",") if e.strip()])

		# Remove duplicates
		emails_to = list(set(emails_to))
		emails_cc = list(set(emails_cc))

		print("TO:", emails_to)
		print("CC:", emails_cc)

		# Email content
		subject = "Agenda Submiited Request From Board"



		# Optional: Add link to document
		# if self.reference_doctype and self.reference_name:
		# 	doc_link = get_url(
		# 		f"/app/{frappe.scrub(self.reference_doctype)}/{self.reference_name}"
		# 	)
		message += f"<br><br>Reference Document:"
		print(docname, name)
		frappe.sendmail(
			recipients=to_list,
			cc =cc_list,
			subject=subject,
			message=message,
			reference_doctype=docname,
			reference_name=name
		)
		# Send Email
		frappe.msgprint("Email sent successfully!")


@frappe.whitelist()
def approval_remarks(docname, reason):

    frappe.db.set_value(
        "Meeting MoM",
        docname,
        "reason",
        reason
    )

    frappe.db.commit()

class MeetingMoM(Document):

	def on_update(self):
		if self.meeting and self.name:
		    frappe.db.set_value(
		        "Board Meeting",
		        self.meeting,
		        "linked_mom",
		        self.name
		    )

	def validate(self):
		
		if self.workflow_state == 'Submitted':
			
			frappe.db.set_value(
				"Board Meeting",
				self.meeting,
				{
				    "status": "MoM Draft",
				    "workflow_state": "MoM Draft",

				}
			)
			
		if self.workflow_state == 'Approved':
			if not self.reason:
			 	frappe.throw("Please update the reason for Approval.")
			frappe.db.set_value(
				"Board Meeting",
				self.meeting,
				{
				    "status": "MoM Approved",
				    "workflow_state": "MoM Approved",

				}
			)
		if self.workflow_state == 'Rejected':
			if not self.reason:
			 	frappe.throw("Please update the reason for Rejected.")

			
