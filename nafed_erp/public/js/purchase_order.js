frappe.ui.form.on("Purchase Order", {
    refresh(frm) {

        if (frm.doc.docstatus === 1) {

            frm.add_custom_button("Create Survey Schedule", function () {

                frappe.new_doc("Survey Schedule", {
                    purchase_order: frm.doc.name,
                    company: frm.doc.company
                });

            }, __("Create"));
        }
    }
});
