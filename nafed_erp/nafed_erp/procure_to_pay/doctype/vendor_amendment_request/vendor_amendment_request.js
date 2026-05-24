// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Vendor Amendment Request", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Vendor Amendment Request', {

    refresh: function(frm) {
        frm.trigger('toggle_fields_by_category');
        frm.trigger('show_current_values');

        // Show current vendor values for reference
        if (frm.doc.vendor_id && frm.doc.__islocal !== true) {
            frm.trigger('show_current_values');
        }
    },

    // ── Auto-fetch vendor details when vendor selected ────────
    vendor_id: function(frm) {
        if (!frm.doc.vendor_id) return;
        frappe.db.get_value(
            'Vendor Registration',
            frm.doc.vendor_id,
            ['vendor_name', 'vendor_code', 'workflow_state',
             'contact_name', 'mobile_number', 'email_id',
             'address', 'gstin', 'pan', 'bank_account_number',
             'ifsc_code', 'state'],
            function(values) {
                if (!values) return;
                frm.set_value('vendor_name', values.vendor_name);
                frm.set_value('vendor_code', values.vendor_code);

                // E5: warn if vendor not active
                if (!['Active', 'HO Approved'].includes(values.workflow_state)) {
                    frappe.msgprint({
                        message: 'This vendor is not Active. Status: '
                                 + values.workflow_state,
                        indicator: 'red',
                        title: 'Vendor Not Active'
                    });
                }

                // Show current values in description for reference
                frm.set_df_property('new_contact_name', 'description',
                    'Current: ' + (values.contact_name || 'Not set'));
                frm.set_df_property('new_mobile_number', 'description',
                    'Current: ' + (values.mobile_number || 'Not set'));
                frm.set_df_property('new_email_id', 'description',
                    'Current: ' + (values.email_id || 'Not set'));
                frm.set_df_property('new_gstin', 'description',
                    'Current: ' + (values.gstin || 'Not set'));
                frm.set_df_property('new_pan', 'description',
                    'Current: ' + (values.pan || 'Not set'));
                frm.set_df_property('new_bank_account_number', 'description',
                    'Current: ' + (values.bank_account_number || 'Not set'));
                frm.set_df_property('new_ifsc_code', 'description',
                    'Current: ' + (values.ifsc_code || 'Not set'));
            }
        );
    },

    // ── Auto-fetch bank when new IFSC entered ─────────────────
    new_ifsc_code: function(frm) {
        if (!frm.doc.new_ifsc_code || frm.doc.new_ifsc_code.length !== 11) return;
        frappe.call({
            method: 'nafed_erp.procure_to_pay.api.vendor_api.fetch_bank_from_ifsc',
            args: { ifsc: frm.doc.new_ifsc_code },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    frm.set_value('new_bank_name', r.message.bank_name);
                    frm.set_value('bank_verified', 1);
                    frappe.show_alert({
                        message: 'Bank verified: ' + r.message.bank_name,
                        indicator: 'green'
                    });
                }
            }
        });
    },

    // ── GSTIN verify on entry ─────────────────────────────────
    new_gstin: function(frm) {
        if (!frm.doc.new_gstin || frm.doc.new_gstin.length !== 15) return;
        frappe.call({
            method: 'nafed_erp.procure_to_pay.api.vendor_api.verify_gstin',
            args: { gstin: frm.doc.new_gstin },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    frm.set_value('gstin_verified', 1);
                    frappe.show_alert({message: 'GSTIN verified ✓', indicator: 'green'});
                } else {
                    frm.set_value('manual_verification_required', 1);
                    frappe.show_alert({
                        message: 'GST API failed — flagged for manual verification (E4)',
                        indicator: 'orange'
                    });
                }
            }
        });
    },

    // ── Show/hide sections by amendment category ──────────────
    amendment_category: function(frm) {
        frm.trigger('toggle_fields_by_category');
    },

    toggle_fields_by_category: function(frm) {
        const cat = frm.doc.amendment_category;

        // Financial fields
        const financial = ['new_bank_account_number', 'new_ifsc_code', 'new_bank_name'];
        // Regulatory fields
        const regulatory = ['new_gstin', 'new_pan', 'new_fssai_number', 'new_msme_number'];
        // Contact fields
        const contact = ['new_contact_name', 'new_mobile_number',
                         'new_email_id', 'new_address', 'new_state'];
        // Document fields
        const document = ['new_license_expiry_date'];

        if (!cat || cat === 'Emergency') {
            // Show all fields for emergency or unset category
            [...financial, ...regulatory, ...contact, ...document]
                .forEach(f => frm.toggle_display(f, true));
            frm.toggle_display('emergency_audit_note', cat === 'Emergency');
        } else {
            // Hide all, show only relevant category
            [...financial, ...regulatory, ...contact, ...document]
                .forEach(f => frm.toggle_display(f, false));
            frm.toggle_display('emergency_audit_note', false);

            if (cat === 'Financial')
                financial.forEach(f => frm.toggle_display(f, true));
            else if (cat === 'Regulatory/Tax')
                regulatory.forEach(f => frm.toggle_display(f, true));
            else if (cat === 'Contact/Address')
                contact.forEach(f => frm.toggle_display(f, true));
            else if (cat === 'Document Renewal')
                document.forEach(f => frm.toggle_display(f, true));
        }
    },

    show_current_values: function(frm) {
        // Already handled inside vendor_id trigger above
    }
});
