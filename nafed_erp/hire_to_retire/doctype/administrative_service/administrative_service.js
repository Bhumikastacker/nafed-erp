// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Administrative Service", {
    refresh(frm) {
        frm.set_query("service_type", function() {
            return {
                filters: {
                    is_active: 1
                }
            };
        });
    }
});

