// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Entry Form", {
 	commodity_group: function(frm) {
        frm.set_query('commodity', function() {
            return {
                filters: {
                    commodity_type: frm.doc.commodity_group
                }
            };
        });
    },
    
    
    refresh(frm) {
        if (frm.is_new()) return;

        frm.clear_custom_buttons();


	        if (!frm.doc.remarks) {
		
            
            frm.add_custom_button("Submit Remarks", function () {

                    frappe.prompt(
                        [
                            {
                                fieldname: "reason",
                                fieldtype: "Small Text",
                                label: "Reason for Submit/Reject",
                                reqd: 1
                            }
                        ],
                        (values) => {
                            frm.set_value("remarks", values.reason);

                            frm.save();
                        },
                        __("Remarks"),
                        __("Submit")
                    );

                });
            
        }
        }
 });
