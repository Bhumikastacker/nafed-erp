frappe.ui.form.on('Delivery Note', {
    // This will trigger when 'Lot Dispatch ID' is selected
    custom_lot_dispatch_id: function(frm) {
        if (frm.doc.custom_lot_dispatch_id) {

            // Fetch data from Lot Dispatch DocType
            frappe.db.get_doc('Lot Dispatch', frm.doc.custom_lot_dispatch_id)
                .then(lot_dispatch => {
                    
                    // Clear the Delivery Note child table
                    // Fieldname: custom__items_detail (note the double underscore)
                    frm.clear_table('custom__items_detail');

                    if (lot_dispatch.lot_details && lot_dispatch.lot_details.length > 0) {
                        
                        lot_dispatch.lot_details.forEach(source_row => {
                            let child_row = frm.add_child('custom__items_detail');
                            
                            // Field Mapping (Source -> Target)
                            child_row.lot_id = source_row.lot_id;
                            child_row.dispatch_quantity = source_row.lot_quantity || 0;
                            child_row.source_location = lot_dispatch.warehouse;
                            
                            // Set Item Code (Commodity)
                            let item_code = source_row.commodity || lot_dispatch.commodity;
                            child_row.item_code = item_code;

                            // Fetch UOM from Item Master (same logic as your hint)
                            if (item_code) {
                                frappe.db.get_value('Item', item_code, 'stock_uom')
                                    .then(r => {
                                        if (r.message && r.message.stock_uom) {
                                            child_row.uom = r.message.stock_uom;

                                            // Refresh child table after updating UOM
                                            frm.refresh_field('custom__items_detail');
                                        }
                                    });
                            }
                        });

                        // Refresh child table to display updated data
                        frm.refresh_field('custom__items_detail');

                        // Show success message
                        frappe.show_alert({
                            message: __("Items and UOM fetched from Lot Dispatch successfully"), 
                            indicator: 'green'
                        });
                    }
                });
        } else {
            // Clear the table if Lot Dispatch ID is removed
            frm.clear_table('custom__items_detail');
            frm.refresh_field('custom__items_detail');
        }
    }
});