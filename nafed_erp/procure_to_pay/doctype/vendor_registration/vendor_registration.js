// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// vendor_registration.js
// Main client script for Vendor Registration

// Include custom validation module - use nafed_erp instead of custom_app
// 
frappe.ui.form.on('Vendor Registration', {

    refresh: function(frm) {
        frm.trigger('toggle_conditional_fields');
        frm.trigger('show_verification_badges');
    },

    // ── IFSC → auto-fetch bank name ──────────────────────────
    ifsc_code: function(frm) {
        if (!frm.doc.ifsc_code || frm.doc.ifsc_code.length !== 11) return;

        frappe.call({
            method: 'nafed_erp.procure_to_pay.api.vendor_api.fetch_bank_from_ifsc',
            args: { ifsc: frm.doc.ifsc_code },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    frm.set_value('bank_name',   r.message.bank_name);
                    frm.set_value('bank_verified', 1);
                    frappe.show_alert({
                        message: 'Bank verified: ' + r.message.bank_name,
                        indicator: 'green'
                    });
                } else {
                    frappe.show_alert({
                        message: 'Could not verify IFSC. Enter bank name manually.',
                        indicator: 'orange'
                    });
                }
            }
        });
    },

    // ── GSTIN → verify on entry ──────────────────────────────
    gstin: function(frm) {
        if (!frm.doc.gstin || frm.doc.gstin.length !== 15) return;

        frappe.call({
            method: 'nafed_erp.procure_to_pay.api.vendor_api.verify_gstin',
            args: { gstin: frm.doc.gstin },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    frm.set_value('gst_verified', 1);
                    frappe.show_alert({
                        message: 'GSTIN verified ✓',
                        indicator: 'green'
                    });
                }
            }
        });
    },

    // ── PAN → verify on entry ────────────────────────────────
    pan: function(frm) {
        if (!frm.doc.pan || frm.doc.pan.length !== 10) return;
        frappe.call({
            method: 'nafed_erp.procure_to_pay.api.vendor_api.verify_pan',
            args: { pan: frm.doc.pan },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    frm.set_value('pan_verified', 1);
                    frappe.show_alert({
                        message: 'PAN verified ✓',
                        indicator: 'green'
                    });
                }
            }
        });
    },

    // ── conditional fields ───────────────────────────────────
    msme_registered: function(frm) {
        frm.trigger('toggle_conditional_fields');
    },
    fssai_required: function(frm) {
        frm.trigger('toggle_conditional_fields');
    },

    toggle_conditional_fields: function(frm) {
        frm.toggle_display('msme_number', frm.doc.msme_registered);
        frm.toggle_display('fssai_number', frm.doc.fssai_required);
        frm.set_df_property('msme_number', 'reqd',
            frm.doc.msme_registered ? 1 : 0);
        frm.set_df_property('fssai_number', 'reqd',
            frm.doc.fssai_required ? 1 : 0);
    },

    show_verification_badges: function(frm) {
        if (frm.doc.gst_verified) {
            frm.set_df_property('gstin', 'description',
                '<span style="color:green;font-weight:bold">✓ GST Verified</span>');
        }
        if (frm.doc.pan_verified) {
            frm.set_df_property('pan', 'description',
                '<span style="color:green;font-weight:bold">✓ PAN Verified</span>');
        }
        if (frm.doc.bank_verified) {
            frm.set_df_property('ifsc_code', 'description',
                '<span style="color:green;font-weight:bold">✓ Bank Verified — '
                + (frm.doc.bank_name || '') + '</span>');
        }
    },
});