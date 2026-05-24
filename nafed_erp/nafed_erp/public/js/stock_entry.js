frappe.ui.form.on("Stock Entry", {
    refresh(frm) {
    console.log("🔄 Refresh triggered");
        

        frm.add_custom_button("Create PO From Indent", function() {

            frappe.call({
                method: "nafed_erp.procure_to_pay.api.stock_entry.create_po_from_indent",
                args: { stock_entry: frm.doc.name },
                callback: function(r) {
                    frappe.set_route("Form", "Purchase Order", r.message);
                }
            });

        });

    }
});

console.log("Stock Entry JS Loaded");

frappe.ui.form.on("Stock Entry", {

    onload(frm) {

        // Only for REPACK from GRN
        if (
            frm.doc.purchase_receipt_reference &&
            frm.doc.items.length === 0
        ) {

            frappe.db.get_doc(
                "Purchase Receipt",
                frm.doc.purchase_receipt_reference
            ).then(pr => {

                pr.items.forEach(row => {

                    let child = frm.add_child("items");

                    child.item_code = row.item_code;

                    child.qty = row.qty;

                    child.uom = row.uom;

                    child.s_warehouse = row.warehouse;

                    child.t_warehouse = row.warehouse;
                });

                frm.refresh_field("items");
            });
        }
    }
});

frappe.ui.form.on("Stock Entry", {

    refresh(frm) {

        calculate_indent(frm);

    }
});

frappe.ui.form.on("Stock Entry Detail", {

    item_code(frm, cdt, cdn) {

        calculate_indent(frm);

    },

    qty(frm, cdt, cdn) {

        calculate_indent(frm);

    },

    s_warehouse(frm, cdt, cdn) {

        calculate_indent(frm);

    },

    items_add(frm) {

        calculate_indent(frm);

    }
});

function calculate_indent(frm) {

    let requested_qty = 0;

    let available_qty_total = 0;

    let fully_available = 0;

    let partially_available = 0;

    let not_available = 0;

    frm.doc.items.forEach(function(row) {

        if (!row.item_code || !row.s_warehouse) return;

        frappe.call({

            method: "frappe.client.get_value",

            args: {

                doctype: "Bin",

                filters: {
                    item_code: row.item_code,
                    warehouse: row.s_warehouse
                },

                fieldname: ["actual_qty"]

            },

            callback: function(r) {

                let available_qty = r.message?.actual_qty || 0;

                let req_qty = row.qty || 0;

                let used_qty = Math.min(
                    available_qty,
                    req_qty
                );

                let difference = req_qty - used_qty;

                // CHILD VALUES
                frappe.model.set_value(
                    row.doctype,
                    row.name,
                    "custom_available_qty",
                    available_qty
                );

                frappe.model.set_value(
                    row.doctype,
                    row.name,
                    "custom_difference_qty",
                    difference
                );

                frappe.model.set_value(
                    row.doctype,
                    row.name,
                    "custom_fully_available",
                    available_qty >= req_qty ? req_qty : 0
                );

                frappe.model.set_value(
                    row.doctype,
                    row.name,
                    "custom_partially_available",
                    (available_qty > 0 && available_qty < req_qty)
                        ? used_qty : 0
                );

                // TOTALS
                requested_qty += req_qty;

                available_qty_total += used_qty;

                if (available_qty >= req_qty) {

                    fully_available += req_qty;

                } else if (available_qty > 0) {

                    partially_available += used_qty;

                } else {

                    not_available += req_qty;
                }

                // PARENT TOTALS
                frm.set_value(
                    "custom_requested_qty",
                    requested_qty
                );

                frm.set_value(
                    "custom_difference_qty",
                    requested_qty - available_qty_total
                );

                frm.set_value(
                    "custom_fully_available",
                    fully_available
                );

                frm.set_value(
                    "custom_partially_available",
                    partially_available
                );

            }

        });

    });

    frm.refresh_field("items");
}
