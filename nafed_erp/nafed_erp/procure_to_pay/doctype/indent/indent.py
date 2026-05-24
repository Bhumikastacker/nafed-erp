# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Indent(Document):
	pass



import frappe

@frappe.whitelist()
def create_jute_work_order(indent_name):

    indent = frappe.get_doc('Indent', indent_name)

    # check already exists
    existing = frappe.db.exists('Jute Work Order', {
        'indent_reference_no': indent.name
    })

    if existing:
        return existing

    jwo = frappe.new_doc('Jute Work Order')

    jwo.indent_reference_no = indent.name
    jwo.date_of_issue = frappe.utils.today()
    jwo.dispatch_by = frappe.utils.today()

    # DELIVERY TABLE
    for row in indent.location_table:
        jwo.append('delivery_location_table', {
            'location_name': row.location_name,
            'location_address': row.location_address,
            'location_contact': row.location_contact,
            'gunny_bags_req': row.gunny_bags_req
        })

    # GUNNY BAG TABLE
    for row in indent.bag_table:
        jwo.append('gunny_bag_details_table', {
            'gunny_bag_name': row.gunny_bag_name,
            'gunny_bag_weight': row.gunny_bag_weight,
            'gunny_bag_uom': row.gunny_bag_uom,
            'gunny_bag_capacity': row.gunny_bag_capacity,
            'gunny_bag_capacity_uom': row.gunny_bag_capacity_uom,
            'unit_price':  row.unit_price
        })

    jwo.insert(ignore_permissions=True)
    frappe.db.commit()

    return jwo.name



