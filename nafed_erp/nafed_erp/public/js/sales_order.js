frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {

        if (
            frm.doc.docstatus !== 1
        ) {
            return;
        }

        // Collect unique Material Requests from items
        let mr_set = new Set();

        (frm.doc.items || []).forEach(row => {
            if (row.material_request) {
                mr_set.add(row.material_request);
            }
        });

        if (mr_set.size === 0) {
            return; // no MR linked yet
        }

        if (mr_set.size === 1) {

            let mr_name = [...mr_set][0];

            frm.add_custom_button(__('Go to Material Request'), function() {
                frappe.set_route("Form", "Material Request", mr_name);
            }, __("EBD Flow"));

        } else {

            // If somehow multiple MRs exist
            frm.add_custom_button(__('View Material Requests'), function() {
                frappe.set_route("List", "Material Request", {
                    name: ["in", [...mr_set]]
                });
            }, __("EBD Flow"));
        }
    }
});
