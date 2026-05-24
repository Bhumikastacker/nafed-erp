// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Administrative Service Request", {
    service: function(frm) {
        if (!frm.doc.service) return;

        // Clear existing checklist
        frm.clear_table("service_request_checklist");

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Administrative Service", // your service doctype
                name: frm.doc.service
            },
            callback: function(r) {
                if (!r.message) return;

                let service_doc = r.message;

                // Loop through its documents_required child table
                (service_doc.service_document_checklist || []).forEach(row => {
                    let child = frm.add_child("service_request_checklist");
                    child.document = row.document;   // map fields
                });

                frm.refresh_field("service_request_checklist");
            }
        });
    }
});
