// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Procurement Quotation Based", {
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
    onload(frm) {
        frm.set_df_property("naming_series", "hidden", 1);
    },
    refresh: function(frm) {
        frm.fields_dict.vendor.grid.get_field("supplier").get_query = function(doc, cdt, cdn) {
            let selected_suppliers = [];

            (frm.doc.vendor || []).forEach(row => {
                if (row.supplier) {
                    selected_suppliers.push(row.supplier);
                }
            });

            return {
                filters: [
                    ["Supplier", "name", "not in", selected_suppliers]
                ]
            };
        };
        frm.fields_dict.requisitions.grid.get_field("requisition_id").get_query = function(doc, cdt, cdn) {
            let selected_reqs = [];

            (frm.doc.requisitions || []).forEach(row => {
                if (row.requisition_id) {
                    selected_reqs.push(row.requisition_id);
                }
            });

            return {
                filters: [
                    ["Requisition", "status", "=", "Approved"],
                    ["Requisition", "mode_of_requisition", "!=", "Tender"],
                    ["Requisition", "name", "not in", selected_reqs]
                ]
            };
        };
        if (!frm.is_new() && frm.doc.status === "Submitted") {
            frm.add_custom_button("Generate RFQ", function () {
                frappe.call({
                    method: "nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based.create_rfq",
                    args: { name: frm.doc.name },
                    callback(r) {
                            frappe.msgprint("RFQ Created: " + r.message);
                            }
                });
            }).addClass("btn-primary");
        }
        if (!frm.is_new() && frm.doc.status === "Submitted") {
            frm.add_custom_button("Compare Quotations", function () {
                frappe.call({
                    method: "nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based.compare_quotations",
                    args: { name: frm.doc.name },
                    callback(r) {
                            frm.set_df_property("comparison_result", "options", r.message);
                            }
                });
            }).addClass("btn-primary");
        }
        if (!frm.is_new() && frm.doc.status === "Submitted") {
            frm.add_custom_button("Create PO", function () {
                let requisition_id = frm.doc.requisitions && frm.doc.requisitions.length > 0 ? frm.doc.requisitions[0].requisition_id : null;
                
                if (!requisition_id) {
                    frappe.msgprint("Please select a Requisition first.");
                    return;
                }
                
                frappe.call({
                    method: "nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based.get_items_from_requisition",
                    args: {
                        requisition_id: requisition_id
                    },
                    callback(r) {
                        if (r.message) {
                            let items = r.message; 
                            if (items.length > 0) {
                                frappe.call({
                                    method: "nafed_erp.information_technology.doctype.procurement_quotation_based.procurement_quotation_based.create_draft_po",
                                    args: {
                                        name: frm.doc.name,
                                        supplier: frm.doc.selected_vendor,
                                        items: items  
                                    },
                                    callback(r) {
                                        if (r.message) {
                                            frappe.msgprint("Draft PO Created: " + r.message);
                                            frappe.set_route("Form", "Purchase Order", r.message);
                                        } else {
                                            frappe.msgprint("Failed to create Draft PO.");
                                        }
                                    }
                                });
                            } else {
                                frappe.msgprint("No items found in the selected Requisition.");
                            }
                        } else {
                            frappe.msgprint("Failed to fetch items from Requisition.");
                        }
                    }
                });
            }).addClass("btn-primary");
        }


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
