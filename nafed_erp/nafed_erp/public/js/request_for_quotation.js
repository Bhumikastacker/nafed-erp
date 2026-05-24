frappe.ui.form.on('Request for Quotation', {
    refresh: function(frm) {
        // Add custom button under "Tools" menu
        frm.add_custom_button(__('Get Supplier from item master'), function() {

            // Check: Items table is not empty
            if (!frm.doc.items || frm.doc.items.length == 0) {
                frappe.msgprint(__("Please add some items to the Items table first."));
                return;
            }

            // Extract all item codes from Items table
            let item_codes = frm.doc.items.map(d => d.item_code);

            frappe.call({
                // Backend method call to fetch suppliers
                method: "nafed_erp.procure_to_pay.api.rfq_api.get_item_suppliers",
                args: {
                    // Passing item codes as JSON string
                    item_codes: JSON.stringify(item_codes)
                },
                callback: function(r) {

                    // If suppliers are returned
                    if (r.message && r.message.length > 0) {

                        // Remove default empty row if it exists
                        if (frm.doc.suppliers.length === 1 && !frm.doc.suppliers[0].supplier) {
                            frm.clear_table("suppliers");
                        }

                        let count = 0;

                        r.message.forEach(supplier => {

                            let exists = (frm.doc.suppliers || []).some(
                                d => d.supplier === supplier.name
                            );
                        
                            if (!exists) {
                                let row = frm.add_child("suppliers");
                                row.supplier = supplier.name;
                        
                                // set email if field exists in child table
                                if (!row.email_id) {
                                    row.email_id = supplier.email_id;
                                }
                        
                                count++;
                            }
                        });

                        if (count > 0) {
                            frm.refresh_field("suppliers");
                            frappe.show_alert(count + " suppliers were found and added.");
                        } else {
                            frappe.msgprint(__("All relevant suppliers are already in the list."));
                        }

                    } else {
                        // No suppliers found in Item Master
                        frappe.msgprint(__("No suppliers are set in the Item Master for these items."));
                    }
                }
            });
        }, __("Tools"));
    }
});

