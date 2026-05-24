// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


// frappe.ui.form.on("Auction Schedule", {

//     refresh: function (frm) {

//         // Hide Add Row button
//         frm.get_field("auction_details").grid.cannot_add_rows = true;

//         frm.refresh_field("auction_details");

//         // Custom Add Button
//         frm.add_custom_button(__('Add'), function () {
//             add_child_row(frm);
//         });
//     },

//     season: function (frm) {
//         fetch_auction_details(frm);
//     },

//     scheme: function (frm) {
//         fetch_auction_details(frm);
//     },

//     warehouse: function (frm) {
//         fetch_auction_details(frm);
//     },

//     commodity: function (frm) {
//         fetch_auction_details(frm);
//     },

//     before_save: function (frm) {

//         console.log("DEBUG START");
//         console.log(frm.doc);

//         if (!frm.doc.auction_details_view || !frm.doc.auction_details_view.length) {

//             frappe.msgprint(__("Please add at least one row"));

//             frappe.validated = false;

//             return;
//         }

//         // =====================================
//         // TOTALS
//         // =====================================

//         let warehouse_count = 0;
//         let total_quantity = 0;

//         (frm.doc.auction_details_view || []).forEach(row => {

//             if (row.warehouse_code) {
//                 warehouse_count++;
//             }

//             total_quantity += flt(
//                 row.quantity_to_put_on_auction || 0
//             );
//         });

//         frm.set_value(
//             "total_warehouse_added",
//             warehouse_count
//         );

//         frm.set_value(
//             "total_warehouse_need_to_be_submitted",
//             warehouse_count
//         );

//         frm.set_value(
//             "total_auction_quantity_added",
//             total_quantity
//         );

//         frm.set_value(
//             "total_auction_quantity_need_to_be_submitted",
//             total_quantity
//         );

//         // =====================================
//         // CREATE AUCTIONS
//         // =====================================

//         frappe.call({
//             method: "nafed_erp.procure_to_pay.doctype.auction_schedule.auction_schedule.create_auctions",
//             args: {
//                 doc: frm.doc
//             },
//             callback: function (r) {

//                 console.log("Auction creation completed");

//             }
//         });
//     }
// });


frappe.ui.form.on("Auction Schedule", {

    refresh: function (frm) {

        // Hide Add Row button
        frm.get_field("auction_details").grid.cannot_add_rows = true;

        frm.refresh_field("auction_details");

        // Custom Add Button
        frm.add_custom_button(__('Add'), function () {
            add_child_row(frm);
        });
    },

    season: function (frm) {
        fetch_auction_details(frm);
    },

    scheme: function (frm) {
        fetch_auction_details(frm);
    },

    warehouse: function (frm) {
        fetch_auction_details(frm);
    },

    commodity: function (frm) {
        fetch_auction_details(frm);
    },

    validate: function (frm) {

        if (!frm.doc.auction_details_view || !frm.doc.auction_details_view.length) {

            frappe.msgprint(__("Please add at least one row"));

            frappe.validated = false;

            return;
        }

        // =====================================
        // TOTALS
        // =====================================

        let warehouse_count = 0;
        let total_quantity = 0;

        (frm.doc.auction_details_view || []).forEach(row => {

            if (row.warehouse_code) {
                warehouse_count++;
            }

            total_quantity += flt(
                row.quantity_to_put_on_auction || 0
            );
        });

        frm.set_value(
            "total_warehouse_added",
            warehouse_count
        );

        frm.set_value(
            "total_warehouse_need_to_be_submitted",
            warehouse_count
        );

        frm.set_value(
            "total_auction_quantity_added",
            total_quantity
        );

        frm.set_value(
            "total_auction_quantity_need_to_be_submitted",
            total_quantity
        );
    },

    after_save: function (frm) {

        // Avoid duplicate creation
        if (frm.doc.__islocal) {
            return;
        }

        frappe.call({
            method: "nafed_erp.procure_to_pay.doctype.auction_schedule.auction_schedule.create_auctions",
            args: {
                doc: frm.doc
            },
            freeze: true,
            freeze_message: __("Creating Auctions..."),

            callback: function (r) {

                if (r.message.success) {

                    frappe.msgprint({
                        title: __("Success"),
                        message: __("Auctions Created Successfully"),
                        indicator: "green"
                    });

                    console.log(r.message.created_auctions);
                }
            }
        });
    }
});


// =====================================
// FETCH AUCTION DETAILS
// =====================================

function fetch_auction_details(frm) {

    console.log("FETCH FUNCTION CALLED");

    // Clear old rows
    frm.clear_table("auction_details");
    frm.refresh_field("auction_details");

    // Validation
    if (
        !frm.doc.season &&
        !frm.doc.scheme &&
        !frm.doc.warehouse &&
        !frm.doc.commodity
    ) {
        return;
    }

    frappe.call({

        method: "nafed_erp.procure_to_pay.doctype.auction_schedule.auction_schedule.get_items_from_season_scheme",

        args: {

            season: frm.doc.season || "",

            scheme: frm.doc.scheme || "",

            warehouse_code: frm.doc.warehouse || "",

            commodity: frm.doc.commodity || ""
        },

        callback: function (r) {

            console.log("API RESPONSE");
            console.log(r.message);

            frm.clear_table("auction_details");

            if (!r.message || !r.message.length) {

                frm.refresh_field("auction_details");

                frappe.msgprint(__("No data found"));

                return;
            }

            // =====================================
            // STORE MOVED ROWS
            // =====================================

            let moved_rows = {};

            (frm.doc.auction_details_view || []).forEach(v => {

                let key =
                    `${v.commodity}_${v.warehouse_code}_${v.season}_${v.scheme}`;

                moved_rows[key] = true;
            });

            // =====================================
            // PREVENT DUPLICATES
            // =====================================

            let existing_map = {};

            r.message.forEach(row => {

                let key =
                    `${row.commodity}_${row.warehouse_code}_${row.season}_${row.scheme}`;

                // Skip duplicate rows
                if (existing_map[key]) {
                    return;
                }

                // Skip already moved rows
                if (moved_rows[key]) {
                    return;
                }

                let child = frm.add_child("auction_details");

                child.state = row.state;

                child.commodity = row.commodity;

                child.season = row.season;

                child.scheme = row.scheme;

                child.qty = flt(row.qty);

                child.warehouse_code = row.warehouse_code;

                child.warehouse_name = row.warehouse_name;

                child.uom = row.uom;

                child.quantity_to_put_on_auction =
                    flt(row.qty);

                existing_map[key] = true;
            });

            frm.refresh_field("auction_details");

            frappe.msgprint(__("Auction Details loaded successfully"));
        }
    });
}


// =====================================
// MOVE SELECTED ROWS
// =====================================

function add_child_row(frm) {

    if (!frm.doc.branch) {

        frappe.msgprint(__('Please select Branch first'));

        return;
    }

    let selected_rows =
        frm.fields_dict.auction_details.grid.get_selected_children();

    if (!selected_rows || !selected_rows.length) {

        frappe.msgprint(__('Please select at least one row'));

        return;
    }

    let added = 0;

    // =====================================
    // ADD ROWS TO VIEW TABLE
    // =====================================

    selected_rows.forEach(d => {

        let exists = (frm.doc.auction_details_view || []).some(v =>

            v.commodity === d.commodity &&
            v.warehouse_code === d.warehouse_code &&
            v.season === d.season &&
            v.scheme === d.scheme
        );

        if (!exists) {

            let row = frm.add_child("auction_details_view");

            row.state = d.state;

            row.commodity = d.commodity;

            row.season = d.season;

            row.scheme = d.scheme;

            row.qty = flt(d.qty);

            row.warehouse_code = d.warehouse_code;

            row.warehouse_name = d.warehouse_name;

            row.uom = d.uom;

            row.quantity_to_put_on_auction =
                flt(d.quantity_to_put_on_auction || d.qty || 0);

            added++;
        }
    });

    // =====================================
    // REMOVE SELECTED ROWS
    // =====================================

    let selected_names = selected_rows.map(d => d.name);

    frm.doc.auction_details =
        (frm.doc.auction_details || []).filter(row => {

            return !selected_names.includes(row.name);
        });

    frm.refresh_field("auction_details");

    frm.refresh_field("auction_details_view");

    if (added > 0) {

        frappe.msgprint(__("Selected rows moved successfully"));
    }
}