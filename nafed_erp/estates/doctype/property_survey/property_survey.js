// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property Survey", {
	surveyor_type: function(frm) {
        if (frm.doc.surveyor_type) {
            frm.set_value('surveyor_name', '');
            frm.fields_dict['surveyor_name'].get_query = function(doc) {
                return {
                    filters: {
                        'type': doc.surveyor_type 
                    }
                };
            };
            frm.refresh_field('surveyor_type');
        }
    },
});
