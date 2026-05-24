// Copyright (c) 2026, CSM Technologies Pvt Ltd
// For license information, please see license.txt

frappe.ui.form.on("Estimated Budget Entry Form", {
   refresh(frm) {
        if (frm.is_new()) return;

        frm.clear_custom_buttons();
	const readonly = ["Approved", "Rejected"].includes(frm.doc.status);

        // Fields that should remain editable
        const editable_fields = ["serial_no", "membership_no"];

        frm.fields.forEach(field => {

            if (!editable_fields.includes(field.df.fieldname)) {
                frm.set_df_property(field.df.fieldname, "read_only", readonly);
            }

        });


	        if (!frm.doc.remarks) {
            // Activate
            
            frm.add_custom_button("Submit Remarks", function () {

                    frappe.prompt(
                        [
                            {
                                fieldname: "reason",
                                fieldtype: "Small Text",
                                label: "Reason for Submit/Reject",
                                reqd: 1
                            }
                        ],
                        (values) => {
                            frm.set_value("remarks", values.reason);

                            frm.save();
                        },
                        __("Remarks"),
                        __("Submit")
                    );

                });
            
        }
        }
    
});
