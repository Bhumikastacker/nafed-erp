// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Procurement Tender Based", {
	before_save: function(frm) {
        return new Promise(function(resolve, reject) {
            frappe.confirm(
                __('Do you want to save this record?'),
                function() {  resolve();  },
                function() {  reject(); }
            );
        });
    },
    after_save(frm) {
        if (frm.doc.naming_series) {
            frm.set_df_property("naming_series", "hidden", 0);
        }
    },
    // Hide naming series on load
    onload(frm) {
        frm.set_df_property("naming_series", "hidden", 1);
        
    },
    refresh: function(frm) {
        frm.fields_dict.requisitions.grid
        .get_field("requisition_id")
        .get_query = function (doc, cdt, cdn) {

            let selected_reqs = [];

            (frm.doc.requisitions || []).forEach(row => {
                if (row.requisition_id) {
                    selected_reqs.push(row.requisition_id);
                }
            });

            return {
                filters: [
                    ["Requisition", "status", "=", "Approved"],
                    ["Requisition", "mode_of_requisition", "=", "Tender"],
                    ["Requisition", "name", "not in", selected_reqs]
                ]
            };
        };
    },
    after_workflow_action(frm) {
        frm.reload_doc();
    },
});
frappe.ui.form.on("Procurement Requisition Items", {
    requisition_id(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.requisition_id) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Requisition",
                name: row.requisition_id
            },
            callback(r) {
                if (!r.message || !r.message.items || !r.message.items.length) {
                    frappe.msgprint(
                        __("No items found in selected Requisition")
                    );
                    return;
                }
                let req_item = r.message.items[0];

                frappe.model.set_value(
                    cdt,
                    cdn,
                    "category",
                    req_item.asset_category
                );

                frappe.model.set_value(
                    cdt,
                    cdn,
                    "type",
                    req_item.asset_type
                );
                frappe.model.set_value(
                    cdt,
                    cdn,
                    "quantity",
                    req_item.quantity
                );
            }
        });
    }
});
