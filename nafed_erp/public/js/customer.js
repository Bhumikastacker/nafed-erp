frappe.ui.form.on('Customer', {

    validate: function(frm) {

        if (frm.doc.custom_account_number && frm.doc.custom_reenter_account_number) {

            if (frm.doc.custom_account_number !== frm.doc.custom_reenter_account_number) {

                frappe.msgprint(__('Account Number and Re-enter Account Number must be the same'));
                frappe.validated = false;
            }
        }
    },

    custom_reenter_account_number: function(frm) {

        if (frm.doc.custom_account_number && frm.doc.custom_reenter_account_number) {

            if (frm.doc.custom_account_number !== frm.doc.custom_reenter_account_number) {

                frappe.msgprint(__('Account numbers do not match'));
            }
        }
    }

});