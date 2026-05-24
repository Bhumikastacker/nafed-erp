# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AgendaFromDivision(Document):
	
	def on_update(self):
		if not self.agenda_no:
		    return

		division_list = frappe.get_all(
		    "Agenda From Division",
		    filters={"agenda_no": self.agenda_no},
		    pluck="division"
		)

		filters = {"doc_type": "Agenda"}

		if division_list:
		    filters["division"] = ["not in", division_list]

		remaining = frappe.db.exists("Mails Configurations", filters)

		frappe.db.set_value(
		    "Meeting Agenda",
		    self.agenda_no,
		    "check_agend_from_div",
		    0 if remaining else 1
		)
