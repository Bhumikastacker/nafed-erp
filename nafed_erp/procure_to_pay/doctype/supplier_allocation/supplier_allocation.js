// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Allocation', {
    refresh: function(frm) {

        if (frm.doc.docstatus === 1) {

            frm.add_custom_button('Create Seed Purchase', function() {
                create_seed_purchase(frm);
            }, 'Create');
        }
    }
});

function create_seed_purchase(frm) {

    let source_items = frm.doc.supplier_allocation_item || [];

    if (!source_items.length) {
        frappe.msgprint("No Allocation Items found");
        return;
    }

    frappe.model.with_doctype('Seed Purchase', function() {

        let doc = frappe.model.get_new_doc('Seed Purchase');

        doc.supplier = frm.doc.supplier;
        doc.allocation = frm.doc.name;
        doc.purchase_date = frappe.datetime.nowdate();
        doc.status = "Draft";

        source_items.forEach(function(item) {

            let row = frappe.model.add_child(
                doc,
                'Seed Purchase Item',
                'seed_purchase_item'   // ✅ IMPORTANT FIX HERE
            );

            row.crop = item.crop;
            row.variety = item.variety;
            row.quantity = item.allocated_qty;
        });

        frappe.set_route('Form', 'Seed Purchase', doc.name);
    });
}

frappe.ui.form.on('Seed Purchase Item', {
    crop: function(frm, cdt, cdn) {
        fetch_rate(frm, cdt, cdn);
    },
    variety: function(frm, cdt, cdn) {
        fetch_rate(frm, cdt, cdn);
    }
});

function fetch_rate(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    if (!row.crop || !row.variety || !frm.doc.supplier) return;

    frappe.db.get_value('Seed Price', {
        crop: row.crop,
        variety: row.variety,
        supplier: frm.doc.supplier
    }, 'rate', function(r) {

        if (r && r.rate) {
            row.rate = r.rate;
            row.amount = row.rate * row.quantity;
            frm.refresh_field('seed_purchase_item');
        }
    });
}