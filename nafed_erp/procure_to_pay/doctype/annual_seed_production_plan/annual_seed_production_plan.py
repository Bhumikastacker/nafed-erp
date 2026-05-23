# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AnnualSeedProductionPlan(Document):
    pass



def validate(self):

    for row in self.items:
        if row.allocated_qty > row.approved_qty:
            frappe.throw(f"Allocated Qty cannot exceed Approved Qty for {row.crop}")

        row.remaining_qty = row.approved_qty - row.allocated_qty

# 	def before_insert(self):
# 		requests = frappe.get_all(
# 			"Government Request",
# 			filters={"workflow_state": "Approved for Planning"},
# 			fields=["commodity", "variety", "qty"]
# 		)

# 		for r in requests:
# 			row = self.append("plan_details", {})
# 			row.crop = r.commodity
# 			row.variety = r.variety
# 			row.demand_qty = r.qty

# 	def validate(self):
# 		self.total_budget = self.target_qty * self.cost_per_mt

# 		if frappe.db.exists({
# 			"doctype": "Annual Seed Production Plan",
# 			"year": self.year,
# 			"season": self.season
# 		}):
# 			frappe.throw("Plan already exists for this year & season")

# 	def before_save(self):
#          if self.workflow_state in ["Approved for Planning", "Finalized"]:
#             frappe.throw("Document cannot be edited after approval")
					

