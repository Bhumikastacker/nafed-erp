// Copyright (c) 2026, CSM Technologies Pvt Ltd
// For license information, please see license.txt

frappe.ui.form.on("Legal Case Upload Batch", {
    refresh(frm) {
        // Prevent duplicate buttons
        frm.clear_custom_buttons();

        // Download sample CSV
        frm.add_custom_button(
            'Download Sample CSV',
            () => {
                window.open(
                    '/api/method/nafed_erp.legal_and_vigilance.doctype.legal_case_upload_batch.legal_case_upload_batch.download_sample_csv'
                );
            },
            'Actions'
        );

        // Validate upload
        if (frm.doc.upload_file && frm.doc.validation_status === 'Draft') {
            frm.add_custom_button(
                'Validate Upload',
                () => {
                    frm.call('validate_upload')
                        .then(() => {
                            frappe.msgprint('Validation completed');
                            frm.reload_doc();
                        });
                },
                'Actions'
            );
        }

        // Import valid cases
        if (['Passed', 'Partial'].includes(frm.doc.validation_status)) {
            frm.add_custom_button(
                'Import Valid Cases',
                () => {
                    frm.call('import_valid_cases')
                        .then(() => {
                            frappe.msgprint('Cases imported successfully');
                            frm.reload_doc();
                        });
                },
                'Actions'
            );
        }
    }
});
