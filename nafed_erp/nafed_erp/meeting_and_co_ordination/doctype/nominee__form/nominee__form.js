frappe.ui.form.on('Nominee  Form', {
    setup(frm) {
        frm.set_query('membership_id', function() {
            return {
                filters: {
                    status: 'Approved'
                }
            };
        });
    },

    refresh(frm) {
        frm.set_query('membership_id', function() {
            return {
                filters: {
                    status: 'Approved'
                }
            };
        });
    },

   membership_id(frm) {
    if (frm.doc.membership_id) {

        frappe.db.get_value('Nominee  Form', {
            membership_id: frm.doc.membership_id
        }, 'name').then(r => {

            if (r.message && r.message.name) {
                frappe.msgprint('Nominee Form is already submitted for this Membership ID.');
                frm.set_value('membership_id', '');
                return;
            }

            frappe.db.get_doc('Board Members', frm.doc.membership_id)
                .then(doc => {
                    frm.set_value('agm_year', doc.agm_year);
                    frm.set_value('state', doc.state);
                    frm.set_value('district', doc.district);
                    frm.set_value('society_name', doc.society_name_1);
                    frm.set_value('share_capital', doc.share_capital);
                });
        });
    }
}
});