# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CounterMapping(Document):
	pass


@frappe.whitelist()
def get_dashboard_data(docname=None):
	data = []

	states = frappe.get_all(
		"Counter Mapping",
		fields=["name", "state"],order_by="state asc"
	)

	for s in states:
		counters = frappe.get_all(
			"AGM Counter Details",
			filters={
				"parent": s.name,
				"parenttype": "Counter Mapping",
				"active": 1
			},
			fields=[
				"counter",
				"from_filter",
				"to_filter"
			],order_by="from_filter asc"
		)

		for c in counters:
			counter_name = frappe.db.get_value(
				"AGM Counter",
				c.counter,
				"counter_name"
			)
			filter=""
			if c.from_filter:
				filter= f"{c.from_filter} - {c.to_filter}"
			data.append({
				"state": s.state,
				"counter": counter_name,
				"range": filter,
				"active": "Yes"
			})

	return data
