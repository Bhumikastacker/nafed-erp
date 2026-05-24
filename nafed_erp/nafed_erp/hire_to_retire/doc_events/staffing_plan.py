import frappe
def get_data(data=None):
	return {}

@frappe.whitelist()
def custom_set_job_requisitions(self, job_reqs):
	if job_reqs:
		requisitions = frappe.db.get_list(
			"Job Requisition",
			filters={"name": ["in", job_reqs]},
			fields=["designation", "no_of_positions", "expected_compensation"],
		)

		self.staffing_details = []
		for req in requisitions:
			self.append(
				"staffing_details",
				{
					"designation": req.designation,
					"vacancies": req.no_of_positions,
					"estimated_cost_per_position": req.expected_compensation,
					"total_estimated_cost": req.no_of_positions * req.expected_compensation
				},
			)		

	return self