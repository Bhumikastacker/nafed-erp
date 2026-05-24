// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property Proposal", {
	zone: function(frm) {
        if (frm.doc.zone) {
            frm.set_value('branch', '');
            frm.fields_dict['branch'].get_query = function(doc) {
                return {
                    filters: {
                        'custom_zone': doc.zone 
                    }
                };
            };
            frm.refresh_field('branch');
        }
    },
});
