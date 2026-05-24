// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Government Action Plan', {

    refresh: function(frm) {

        // ✅ Show buttons only in Draft
        if (frm.doc.docstatus === 0) {

            frm.add_custom_button('Fetch Supplier Requests', function() {
                fetch_supplier_requests(frm);
            }, 'Get Items');

            frm.add_custom_button('Create Supplier Allocation', function() {
                create_supplier_allocation_prompt(frm);
            }, 'Create');
        }
    }

});
/* ==============================
   FETCH SUPPLIER REQUESTS
============================== */

function fetch_supplier_requests(frm) {

    if (!frm.doc.annual_plan) {
        frappe.msgprint("Please select Annual Plan");
        return;
    }

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Supplier Production Plan Request",
            filters: {
                annual_plan: frm.doc.annual_plan,
                docstatus: 1
            },
            // ✅ ADD supplier FIELD HERE
            fields: ["name","state", "supplier", "crop", "variety", "quantity"]
        },
        callback: function(r) {

            if (!r.message || r.message.length === 0) {
                frappe.msgprint("No submitted Supplier Requests found");
                return;
            }

            frm.clear_table("government_action_plan_item");

            r.message.forEach(function(d) {

                let row = frm.add_child("government_action_plan_item");

                row.state = d.state;
                row.crop = d.crop;
                row.variety = d.variety;
                row.quantity = d.quantity;

                // ✅ IMPORTANT
                row.supplier = d.supplier;

                // Optional link
                row.supplier_request = d.name;

                // Default selected
                row.is_selected = 1;

            });

            frm.refresh_field("government_action_plan_item");

            frappe.show_alert({
                message: "Supplier Requests Fetched Successfully",
                indicator: "green"
            });
        }
    });
}

/* ==============================
   CREATE SUPPLIER ALLOCATION (FILTERED)
============================== */

function create_supplier_allocation_prompt(frm) {

    let suppliers = [];

    (frm.doc.government_action_plan_item || []).forEach(d => {
        if (d.is_selected && d.supplier) {
            suppliers.push(d.supplier);
        }
    });

    // Remove duplicates
    suppliers = [...new Set(suppliers)];

    if (!suppliers.length) {
        frappe.msgprint("No selected suppliers found");
        return;
    }

    frappe.prompt([
        {
            label: 'Supplier',
            fieldname: 'supplier',
            fieldtype: 'Link',
            options: 'Supplier',
            reqd: 1,
            get_query: function() {
                return {
                    filters: {
                        name: ['in', suppliers]
                    }
                };
            }
        }
    ], function(values) {

        create_supplier_allocation(frm, values.supplier);

    }, 'Select Supplier');
}


/* ==============================
   CREATE SUPPLIER ALLOCATION DOC
============================== */

function create_supplier_allocation(frm, selected_supplier) {

    let selected_items = frm.doc.government_action_plan_item.filter(d =>
        d.is_selected && d.supplier === selected_supplier
    );

    if (!selected_items.length) {
        frappe.msgprint("No matching items for selected supplier");
        return;
    }

    frappe.model.with_doctype('Supplier Allocation', function() {

        let doc = frappe.model.get_new_doc('Supplier Allocation');

        doc.action_plan = frm.doc.name;
        doc.supplier = selected_supplier;

        selected_items.forEach(function(d) {

            let row = frappe.model.add_child(doc, 'Supplier Allocation Item', 'supplier_allocation_item');

            row.crop = d.crop;
            row.variety = d.variety;
            row.quantity = d.quantity;
            row.supplier_request = d.supplier_request;

        });

        frappe.set_route('Form', 'Supplier Allocation', doc.name);
    });
}