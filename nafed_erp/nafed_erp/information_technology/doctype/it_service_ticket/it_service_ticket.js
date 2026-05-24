// Copyright (c) 2025, Digitalis Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("IT Service Ticket", {
	before_save: function(frm) {
        return new Promise(function(resolve, reject) {
            frappe.confirm(
                __('Do you want to save this record?'),
                function() {  resolve();  },
                function() {  reject(); }
            );
        });
    },
    after_save: function(frm) {
        if (frm.doc.naming_series) {
            frm.set_df_property("naming_series", "hidden", 0);
        }
    },

    onload: function(frm) {
        frm.set_df_property("naming_series", "hidden", 1);
    },
});
