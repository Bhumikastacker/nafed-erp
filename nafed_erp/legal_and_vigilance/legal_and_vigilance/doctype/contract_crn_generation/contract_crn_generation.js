// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Contract CRN Generation", {
// 	refresh(frm) {

// 	},

// });


frappe.ui.form.on("Contract CRN Generation", {
    refresh(frm) {
        // Show button only after submit
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
                __("Initiate Renewal"),
                () => {
                    frm.events.create_renewal_doc(frm);
                }
            );
        }
    },

    create_renewal_doc(frm) {
        frappe.model.with_doctype(
            "Auto-Generate Renewal Documents",
            () => {
                let renewal = frappe.model.get_new_doc(
                    "Auto-Generate Renewal Documents"
                );

                // -----------------------
                // Field Mapping
                // -----------------------
                renewal.contract_id = frm.doc.name;          // CRN ID
                renewal.generated_date = frappe.datetime.get_today();

                // Optional mappings (only if fields exist)
                // renewal.template_used = frm.doc.template_used;
                // renewal.modified_clauses = frm.doc.modified_clauses;

                // Set default approval status
                renewal.approval_status = "Open";

                // Open the new document
                frappe.set_route(
                    "Form",
                    "Auto-Generate Renewal Documents",
                    renewal.name
                );
            }
        );
    }
});
