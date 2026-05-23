import frappe
from frappe.model.document import Document
from nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based import get_items_from_requisition
from nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based import create_draft_po


class ProcurementTenderBased(Document):

    def on_update(self):
        self.sync_status()
        self.generate_po_on_approve()

    def sync_status(self):
        status_map = {
            "Draft": "Draft",
            "Submitted": "Published",
            "Validated": "Evaluated",
            "Approved": "Awarded"
        }
        self.db_set(
            "tender_status",
            status_map.get(self.workflow_state, self.workflow_state)
        )

    def generate_po_on_approve(self):
        if self.workflow_state != "Approved":
            return
        if not self.l1_vendor:
            frappe.throw("Select L1 Vendor before approval")
        all_items = []
        requisition_names = []
        for row in self.requisitions:
            requisition = frappe.get_doc(
				"Requisition", row.requisition_id
			)
            if requisition.po_generated:
                frappe.throw(
					f"Purchase Order already generated for Requisition "
					f"{requisition.name}"
				)
            all_items.extend(
				get_items_from_requisition(requisition.name)
			)
            # requisition_names.append(requisition.name)
        if not all_items:
            frappe.throw("No items found from linked requisitions")

        po_name = create_draft_po(
			supplier=self.l1_vendor,
			items=all_items
		)
        # for req_name in requisition_names:
        #     frappe.db.set_value(
		# 		"Requisition",
		# 		req_name,
		# 		{
		# 			"po_generated": 1,
		# 			"purchase_order": po_name
		# 		}
		# 	)
        self.db_set("po_generated", 1)
        self.db_set("purchase_order", po_name)
        frappe.msgprint(
			f"Draft Purchase Order <b>{po_name}</b> generated successfully"
		)
