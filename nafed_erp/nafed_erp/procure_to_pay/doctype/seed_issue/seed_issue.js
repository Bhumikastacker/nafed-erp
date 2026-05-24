// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seed Issue', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Seed Production', function() {
                create_production(frm);
            }, 'Create');
        }
    }
});
function create_production(frm) {

    frappe.model.with_doctype('Seed Production', function() {

        let doc = frappe.model.get_new_doc('Seed Production');

        doc.supplier = frm.doc.supplier;
        doc.seed_issue = frm.doc.name;
        doc.production_date = frappe.datetime.nowdate();

        // optional: pass issued qty
        doc.issued_quantity = frm.doc.total_quantity || 0;

        frappe.set_route('Form', 'Seed Production', doc.name);
    });
}