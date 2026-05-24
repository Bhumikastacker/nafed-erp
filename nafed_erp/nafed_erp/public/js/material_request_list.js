console.log("Material Request List View Settings Loaded");
frappe.listview_settings["Material Request"].onload = function(listview) {
console.log("Material Request List View onload triggered");
    listview.page.add_inner_button("Create Indent", function() {

        let selected = listview.get_checked_items();

        if (!selected.length) {
            frappe.msgprint("Select at least one Material Request");
            return;
        }

        let mr_names = selected.map(d => d.name);

        frappe.call({
            method: "nafed_erp.procure_to_pay.api.material_request.create_indent",
            args: { mr_list: mr_names },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route("Form", "Stock Entry", r.message);
                }
            }
        });

    });
};