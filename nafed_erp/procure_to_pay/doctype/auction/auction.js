// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Auction", {
// 	refresh(frm) {
frappe.ui.form.on("Auction", {
    refresh: function(frm) {
        update_total_counts(frm);
    },

    // Commodity select hone par trigger
    commodity: function(frm) {
        fetch_all_warehouse_stock(frm);
    },

    branch: function(frm) {
        // Branch change hone par dubara fresh fetch ke liye
        if (frm.doc.commodity) {
            fetch_all_warehouse_stock(frm);
        }
    }
});


frappe.ui.form.on("Auction Child table", {

    // Jaise hi quantity_to_put_on_auction change ho
    quantity_to_put_on_auction: function(frm, cdt, cdn) {
        update_total_counts(frm);
    },

    // qty change hone par bhi total update
    qty: function(frm, cdt, cdn) {
        update_total_counts(frm);
    },

    // row remove hone par
    auction_details_remove: function(frm) {
        update_total_counts(frm);
    }
});


function fetch_all_warehouse_stock(frm) {
    console.log("📦 Commodity Triggered");

    // Commodity + Branch required
    if (!frm.doc.commodity || !frm.doc.branch) {
        return;
    }

    console.log("Selected Commodity:", frm.doc.commodity);
    console.log("Selected Branch:", frm.doc.branch);

    frappe.call({
        method: "nafed_erp.procure_to_pay.doctype.auction.auction.get_item_warehouse_stock",
        args: {
            item_code: frm.doc.commodity,
            company: frm.doc.branch
        },

        callback: function(r) {
            console.log("📥 API Response:", r.message);

            if (r.message && r.message.length > 0) {

                let rows_added = 0;

                r.message.forEach(stock_row => {

                    let already_exists = false;

                    // Duplicate check:
                    // same commodity + same warehouse
                    (frm.doc.auction_details || []).forEach(row => {
                        if (
                            row.commodity == frm.doc.commodity &&
                            row.warehouse == stock_row.warehouse
                        ) {
                            already_exists = true;
                        }
                    });

                    if (!already_exists) {

                        let row = frm.add_child("auction_details");

                        row.commodity = frm.doc.commodity;
                        row.warehouse = stock_row.warehouse || "";
                        row.qty = stock_row.actual_qty || 0;

                        // Blank by default
                        row.quantity_to_put_on_auction = 0;

                        row.state = frm.doc.state;
                        row.scheme = frm.doc.scheme;
                        row.season = frm.doc.season;

                        rows_added++;
                    }
                });

                frm.refresh_field("auction_details");

                // instant total update
                update_total_counts(frm);

                if (rows_added > 0) {
                    frappe.msgprint(
                        `${rows_added} warehouse row(s) added successfully`
                    );

                    console.log("✅ Rows Added:", rows_added);
                } else {
                    frappe.msgprint(
                        "All warehouse rows already exist for this commodity"
                    );
                }

            } else {
                frappe.msgprint("No stock found for selected Commodity");
            }
        }
    });
}


function update_total_counts(frm) {
    let total_rows = (frm.doc.auction_details || []).length;
    let total_auction_qty = 0;

    // quantity_to_put_on_auction ka live total
    (frm.doc.auction_details || []).forEach(row => {
        total_auction_qty += flt(row.quantity_to_put_on_auction || 0);
    });

    // Direct model update for instant reflection
    frm.doc.total_warehouse_added = total_rows;
    frm.doc.total_warehouse_need_to_be_submitted = total_rows;

    frm.doc.total_auction_quantity_added = total_auction_qty;
    frm.doc.total_auction_quantity_need_to_be_submitted = total_auction_qty;

    // Immediate refresh on screen
    frm.refresh_field("total_warehouse_added");
    frm.refresh_field("total_warehouse_need_to_be_submitted");
    frm.refresh_field("total_auction_quantity_added");
    frm.refresh_field("total_auction_quantity_need_to_be_submitted");

    console.log("Total Warehouse Added:", total_rows);
    console.log("Total Auction Quantity Added:", total_auction_qty);
}


frappe.ui.form.on("Auction", {
refresh: function(frm) {
    if (frm.doc.docstatus === 1) {

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Order",
                filters: {
                    custom_auction_id: frm.doc.name
                },
                fields: ["name"],
                limit_page_length: 1
            },
            callback: function(r) {

               
                if (!r.message || r.message.length === 0) {

                    frm.add_custom_button("Reserve Stock ", function() {
                        frappe.call({
                            method: "nafed_erp.procure_to_pay.doctype.auction.auction.create_sales_order_and_reservation",
                            args: {
                                auction_name: frm.doc.name
                            },
                            callback: function(res) {
                                if (res.message) {
                                    frappe.msgprint("Sales Order Created: " + res.message.sales_order);

                                  
                                    frm.reload_doc();
                                }
                            }
                        });
                    });

                }

            }
        });
    }
}

});