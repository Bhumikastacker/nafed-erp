frappe.ui.form.on('Policy Management', {
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
    onload(frm) {
        frm.set_df_property("naming_series", "hidden", 1);
    },
    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.status === "Approved") {
            frm.add_custom_button(
                __("Add Compliance"),
                () => frappe.set_route("Form", "Compliance Clause", {
                    'policy_id': frm.doc.name,
                }),
                __("Compliance")
            );
            frm.add_custom_button(
                __("Update & Compliances"),
                () => frappe.set_route("List", "Compliance Clause", {
                    'policy_id': frm.doc.name,
                }),
                __("Compliance")
            );
        }
    }

});



