# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json

class ProcurementQuotationBased(Document):
	def on_update(self):
		if self.workflow_state == "Draft":
			self.db_set("status", "Draft")
		if self.workflow_state == "Submitted":
			self.db_set("status", "Submitted")
		if self.workflow_state == "Reviewed":
			self.db_set("status", "In Progress")	
		if self.workflow_state == "Approved":
			self.db_set("status", "Approved")

	def validate(self):
		if len(self.vendor) < 3:
			frappe.throw("Minimum 3 vendors must be selected as per policy.")
		if self.workflow_state == "Submitted" and not self.selected_vendor:
			frappe.throw("Select the L1 Vendor before submitting the document.")
		suppliers = [vendor.supplier for vendor in self.vendor]
		if len(suppliers) != len(set(suppliers)):
			frappe.throw("Duplicate suppliers found in vendor table.")
		requisition_ids = [req.requisition_id for req in self.requisitions]
		if len(requisition_ids) != len(set(requisition_ids)):
			frappe.throw("Duplicate Requisition IDs found in requisitions table.")

@frappe.whitelist()
def create_rfq(name):
    doc = frappe.get_doc("Procurement Quotation Based", name)

    rfq = frappe.new_doc("Request for Quotation")
    rfq.transaction_date = frappe.utils.nowdate()
    if not doc.vendor:
        frappe.throw("No supplier(s) found in vendor table!")

    for sup in doc.vendor:
        if not sup.supplier:
            frappe.throw(f"Supplier missing at Row {sup.idx}")
        rfq.append("suppliers", {"supplier": sup.supplier})
    for req_row in doc.requisitions:
        if not req_row.requisition_id:
            frappe.throw(f"Row {req_row.idx}: Missing Requisition ID")
        requisition = frappe.get_doc("Requisition", req_row.requisition_id)
        if not requisition.items:
            frappe.throw(f"No items found in Requisition: {req_row.requisition_id}")
        for row in requisition.items:
            if not row.asset_type:
                frappe.throw(f"Requisition {req_row.requisition_id}, Row {row.idx}: Asset Type missing")
            item_code = frappe.db.get_value("IT Asset Type",row.asset_type,"item_code")
            if not item_code:
                frappe.throw(f"Item not linked with Asset Type: {row.asset_type}")
            default_warehouse = frappe.db.get_single_value( "Stock Settings","default_warehouse")
            if not default_warehouse:
                frappe.throw("Default Warehouse is not set in Stock Settings")
            conversion_factor = frappe.db.get_value("UOM Conversion Detail",{"parent": item_code,"uom": row.uom},"conversion_factor")
            if not conversion_factor:
                frappe.throw(f"UOM '{row.uom}' not defined for Item '{item_code}'")
            rfq.append("items", {
                "item_code": item_code,
                "qty": row.quantity,
                "rate": row.rate,
                "uom": row.uom,
                "conversion_factor": conversion_factor,
                "schedule_date": row.required_by,
                "warehouse": default_warehouse
            })
            rfq.message_for_supplier = (
                f"Dear Supplier,\n\n"
                f"Please quote for the items against Requisition "
                f"{req_row.requisition_id}.\n\n"
                "Regards,\nProcurement Team"
            )

    rfq.insert(ignore_permissions=True)
    rfq.submit()

    doc.db_set("status", "RFQ Created")
    doc.db_set("workflow_state", "RFQ Created")

    return rfq.name

@frappe.whitelist()
def compare_quotations(name):
	doc = frappe.get_doc("Request for Quotation Supplier", name)
	rows = ""
	for q in doc.vendor:
		rows += f"""
			<tr>
				<td>{q.vendor}</td>
				<td>{q.price}</td>
				<td>{q.taxes}</td>
				<td>{q.warranty}</td>
				<td>{q.delivery_time}</td>
				<td>{q.validity}</td>
			</tr>
		"""
	html = f"""
	<table class="table table-bordered">
		<thead>
			<tr>
				<th>Vendor</th><th>Price</th><th>Taxes</th>
				<th>Warranty</th><th>Delivery</th><th>Validity</th>
			</tr>
		</thead>
		<tbody>{rows}</tbody>
	</table>
	"""
	return html


@frappe.whitelist()
def get_items_from_requisition(requisition_id):
    requisition = frappe.get_doc("Requisition", requisition_id)

    if not requisition:
        frappe.throw(_("Requisition not found"))
    items = []

    for row in requisition.items:
        items.append({
            "asset_category": row.asset_category,
            "asset_type": row.asset_type,
            "quantity": row.quantity,
            "rate": row.rate,
            "amount": row.amount,
            "uom": row.uom,
            "required_by": row.required_by
        })
    
    return items



@frappe.whitelist()
def create_draft_po(name, supplier, items):
    existing_po = frappe.db.get_value("Procurement Quotation Based",name,"purchase_order")
    if existing_po:
        frappe.throw(
            f"Purchase Order already exists: <b>{existing_po}</b>"
        )
    if isinstance(items, str):
        items = json.loads(items)
    if not items:
        frappe.throw("No items received to create Purchase Order")
    po = frappe.new_doc("Purchase Order")
    po.supplier = supplier
    po.schedule_date = frappe.utils.nowdate()
    default_warehouse = frappe.db.get_single_value( "Stock Settings","default_warehouse")
    for idx, item in enumerate(items, start=1):
        if not item.get("asset_type"):
            frappe.throw(f"Row {idx}: Asset Type missing")
        item_code = frappe.db.get_value("IT Asset Type",item["asset_type"],"item_code")
        if not item_code:
            frappe.throw(f"Item not linked with Asset Type: {item['asset_type']}")
        is_stock = frappe.db.get_value("Item",item_code, "is_stock_item")
        conversion_factor = frappe.db.get_value("UOM Conversion Detail",
            {
                "parent": item_code,
                "uom": item.get("uom")
            },
            "conversion_factor") or 1
        po_item = {
            "item_code": item_code,
            "qty": float(item.get("quantity", 0)),
            "rate": float(item.get("rate", 0)),
            "uom": item.get("uom"),
            "conversion_factor": conversion_factor,
            "schedule_date": item.get("required_by"),
        }
        warehouse = frappe.db.get_value(
            "Warehouse",
            {
                "company": po.company,
                "is_group": 0
            },
            "name"
        )

        if not warehouse:
            frappe.throw(
                f"No warehouse found for company {po.company}"
            )
        po_item["warehouse"] = warehouse
        po.append("items", po_item)
    po.insert(ignore_permissions=True)
    frappe.db.set_value("Procurement Quotation Based",name,"purchase_order",po.name)
    return po.name

