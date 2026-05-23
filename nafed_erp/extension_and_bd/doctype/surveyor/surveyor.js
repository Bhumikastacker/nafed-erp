frappe.ui.form.on('Surveyor', {

    refresh(frm) {
        toggle_fields(frm);
    },

    employee(frm) {
        if (frm.doc.employee) {
            frm.set_value('user', null);
            frm.set_value('vendor', null);

            frappe.db.get_value('Employee', frm.doc.employee, 'employee_name')
                .then(r => {
                    if (r.message) {
                        frm.set_value('surveyor_name', r.message.employee_name);
                    }
                });
        }
        toggle_fields(frm);
    },

    user(frm) {
        if (frm.doc.user) {
            frm.set_value('employee', null);
            frm.set_value('vendor', null);

            frappe.db.get_value('User', frm.doc.user, 'full_name')
                .then(r => {
                    if (r.message) {
                        frm.set_value('surveyor_name', r.message.full_name);
                    }
                });
        }
        toggle_fields(frm);
    },

    vendor(frm) {
        if (frm.doc.vendor) {
            frm.set_value('employee', null);
            frm.set_value('user', null);

            frappe.db.get_value('Supplier', frm.doc.vendor, 'supplier_name')
                .then(r => {
                    if (r.message) {
                        frm.set_value('surveyor_name', r.message.supplier_name);
                    }
                });
        }
        toggle_fields(frm);
    }

});


function toggle_fields(frm) {

    // If employee selected
    if (frm.doc.employee) {
        frm.set_df_property('user', 'hidden', 1);
        frm.set_df_property('vendor', 'hidden', 1);
        frm.set_df_property('employee', 'hidden', 0);
    }

    // If user selected
    else if (frm.doc.user) {
        frm.set_df_property('employee', 'hidden', 1);
        frm.set_df_property('vendor', 'hidden', 1);
        frm.set_df_property('user', 'hidden', 0);
    }

    // If vendor selected
    else if (frm.doc.vendor) {
        frm.set_df_property('employee', 'hidden', 1);
        frm.set_df_property('user', 'hidden', 1);
        frm.set_df_property('vendor', 'hidden', 0);
    }

    // If nothing selected
    else {
        frm.set_df_property('employee', 'hidden', 0);
        frm.set_df_property('user', 'hidden', 0);
        frm.set_df_property('vendor', 'hidden', 0);
    }

}