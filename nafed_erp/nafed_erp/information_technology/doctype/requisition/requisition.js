// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Requisition", {
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
    onload: function(frm) {
        frm.fields_dict['items'].grid.get_field('asset_type').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            console.log("Selected Category:", row.asset_category);
            return {
                filters: {
                    'category': row.asset_category
                }
            };
        };
    },
});
