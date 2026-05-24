frappe.ui.form.on('Compliance Clause', {
    before_save: function(frm) {
        return new Promise(function(resolve, reject) {
            frappe.confirm(
                __('Do you want to save this record?'),
                function() {  
                    resolve();  
                },
                function() {  
                    reject(); 
                }
            );
        });
    },

    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.status !== 'Compliant') {
            frm.add_custom_button(__('Update Compliance Status'), function() {
                // Open the dialog for updating the compliance status
                open_compliance_status_dialog(frm);
            });
        }
    },

    after_save: function(frm) {
        if (frm.doc.naming_series) {
            frm.set_df_property("naming_series", "hidden", 0);
        }
        if (frm.doc.status === 'Draft') {
            // Route for approval
            frappe.msgprint(__('Compliance Clause created. Awaiting approval.'));
        } else {
            // Notify stakeholders if compliance clause is approved
            frappe.msgprint(__('Compliance Clause approved.'));
        }
    },

    onload: function(frm) {
        frm.fields_dict['naming_series'].df.hidden = true;
        frm.refresh_fields('naming_series');
        if (frappe.route_options && frappe.route_options.policy_id) {
            // Set the Policy ID field with the passed value
            frm.set_value('policy_id', frappe.route_options.policy_id);
        }
    }
});

// Function to open the compliance status update dialog
function open_compliance_status_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: 'Update Compliance Status',
        fields: [
            {
                label: 'Status',
                fieldname: 'compliance_status',
                fieldtype: 'Select',
                options: ['Draft', 'Submitted', 'In Progress', 'Remediated', 'Verified', 'Compliant'],
                reqd: true
            },
            {
                label: 'Remarks',
                fieldname: 'remarks',
                fieldtype: 'Small Text',
                reqd: true
            }
        ],
        primary_action(values) {
            // Validate the fields before proceeding
            if (!values.compliance_status || !values.remarks) {
                frappe.msgprint('Status Update and Remarks are mandatory.');
                return;
            }

            // Make the call to update compliance status and remarks
            update_compliance_status(frm, values.compliance_status, values.remarks);

            // Close the dialog
            d.hide();
        }
    });

    // Show the dialog
    d.show();
}

// Function to update compliance status and remarks in the document
function update_compliance_status(frm, status, remarks) {
    frm.call({
        method: "update_complience_status",  // Call the global function
        args: {
            doctype: frm.doc.doctype,       // Pass the doctype
            docname: frm.doc.name,           // Pass the docname
            status: status,                  // Pass the status field value
            remarks: remarks                 // Pass the remarks field value
        },
        callback: function(r) {
            // Notify the user upon successful update
            frappe.msgprint(__('Compliance Status and Remarks updated successfully.'));
            // Optionally, refresh the form to reflect the changes
            frm.refresh();
        }
    });
}
