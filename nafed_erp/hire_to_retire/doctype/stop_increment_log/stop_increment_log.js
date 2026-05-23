// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stop Increment Log", {
	onload(frm) {
        frm.set_query("employee", () => {
            return {
                filters: {
                    company: frm.doc.company,
                    status : "Active"
                }
            };
        });
	},
    company(frm) {
        // reset employee when company changes
        frm.set_value("employee", null);

        frm.set_query("employee", () => {
            return {
                filters: {
                    company: frm.doc.company,
                    status : "Active"
                }
            };
        });
    }
});
