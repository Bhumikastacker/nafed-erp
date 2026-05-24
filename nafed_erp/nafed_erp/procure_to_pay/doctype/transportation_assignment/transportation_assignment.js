// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Transportation Assignment", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Transportation Assignment', {

    // This function triggers when you select a 'Lot Dispatch ID'
    lot_dispatch_id: function(frm) {
        if (frm.doc.lot_dispatch_id) {

            frappe.db.get_doc('Lot Dispatch', frm.doc.lot_dispatch_id)
                .then(lot_dispatch => {
                    frm.clear_table('items');

                    if (lot_dispatch.lot_details && lot_dispatch.lot_details.length > 0) {
                        
                        lot_dispatch.lot_details.forEach(source_row => {
                            let child_row = frm.add_child('items');
                            
                            // Map
                            child_row.lot_id = source_row.lot_id;
                            child_row.dispatch_quantity = source_row.lot_quantity || 0;
                            child_row.source_location = lot_dispatch.warehouse;
                            
                            // Get the Item Code (Commodity)
                            let item_code = source_row.commodity || lot_dispatch.commodity;
                            child_row.item_code = item_code;

                            // --- LOGIC TO FETCH UOM FROM ITEM MASTER ---
                            if (item_code) {
                                frappe.db.get_value('Item', item_code, 'stock_uom')
                                    .then(r => {
                                        if (r.message && r.message.stock_uom) {

                                            // Set UOM from Item Master to your child table row
                                            child_row.uom = r.message.stock_uom;
                                            frm.refresh_field('items');
                                        }
                                    });
                            }
                        });

                        frm.refresh_field('items');
                        frappe.show_alert({
                            message: __("Items and UOM (from Item Master) successfully fetched"), 
                            indicator: 'green'
                        });
                    }
                });
        }
    },                                                                                                                                                                                                                                                                                                                                                                                  

    // BLACKLIST CHECK
    transporter_name: function(frm) {                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
        if (frm.doc.transporter_name) {

            // Check 'on_hold' status directly from the Supplier master
            frappe.db.get_value('Supplier', frm.doc.transporter_name, 'on_hold')
                .then(r => {
                    if (r.message && r.message.on_hold) {
                        frappe.msgprint({
                            title: __('Transporter Blocked'),
                            indicator: 'red',
                            message: __("Transporter <b>{0}</b> is currently BLACKLISTED / ON HOLD!", [frm.doc.transporter_name])
                        });

                        // Clearing the field so user cannot select this transporter
                        frm.set_value('transporter_name', "");
                    }
                });
        }
    },

    // Transit time calculation
    expected_loading_date: function(frm) { calculate_transit_time(frm); },
    expected_delivery_date: function(frm) { calculate_transit_time(frm); }
});

// Helper function to calculate days between dates
function calculate_transit_time(frm) {
    if (frm.doc.expected_loading_date && frm.doc.expected_delivery_date) {
        let diff = frappe.datetime.get_diff(frm.doc.expected_delivery_date, frm.doc.expected_loading_date);

        if (diff < 0) {
            frappe.msgprint(__("Delivery date cannot be earlier than loading date!"));
            frm.set_value('expected_delivery_date', "");
            
        } else {
            frm.set_value('transit_time_days', diff);
        }
    }
}

