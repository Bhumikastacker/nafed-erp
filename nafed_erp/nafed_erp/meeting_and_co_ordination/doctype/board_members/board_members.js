frappe.ui.form.on("Board Members", {
    refresh(frm) {
    
    
        if (frm.is_new()) return;
        const readonly = ["Approved", "Rejected"].includes(frm.doc.status);

        // Fields that should remain editable
        const editable_fields = ["serial_no", "membership_no"];

        frm.fields.forEach(field => {

            if (!editable_fields.includes(field.df.fieldname)) {
                frm.set_df_property(field.df.fieldname, "read_only", readonly);
            }

        });


        frm.clear_custom_buttons();

	  if (frm.doc.status === "Submitted" &&  !frm.doc.reason) {
	  
	  	frm.add_custom_button(__('UpDate Reason'), () => {

                    frappe.prompt(
                        [
                            {
                                fieldname: "reason",
                                fieldtype: "Small Text",
                                label: "Reason for Approval/Rejection",
                                reqd: 1
                            }
                        ],
                        (values) => {
                            frappe.call({
                                method: "nafed_erp.meeting_and_co_ordination.doctype.board_members.board_members.approval_remarks",
                                args: {
                                    docname: frm.doc.name,
                                    reason: values.reason
                                },
                                callback: function () {
                                    frm.reload_doc();
                                }
                            });
                        },
                        __("Confirm In-Activation"),
                        __("Submit")
                    );

                }, __('Update Remarks for Approval/Rejection'));
	  
	}  
        if (frm.doc.status === "Approved") {

            if (frm.doc.active === 0) {

                frm.add_custom_button(__('Active'), () => {

                    frappe.prompt(
                        [
                            {
                                fieldname: "reason",
                                fieldtype: "Small Text",
                                label: "Reason for Activation",
                                reqd: 1
                            }
                        ],
                        (values) => {
                            frappe.call({
                                method: "nafed_erp.meeting_and_co_ordination.doctype.board_members.board_members.activate_member",
                                args: {
                                    docname: frm.doc.name,
                                    reason: values.reason
                                },
                                callback: function () {
                                    frm.reload_doc();
                                }
                            });
                        },
                        __("Confirm Activation"),
                        __("Submit")
                    );

                }, __('Actions'));

            }

            // ==========================
            // INACTIVATE BUTTON
            // ==========================
            else {

                frm.add_custom_button(__('In-Active'), () => {

                    frappe.prompt(
                        [
                            {
                                fieldname: "reason",
                                fieldtype: "Small Text",
                                label: "Reason for In-Activation",
                                reqd: 1
                            }
                        ],
                        (values) => {
                            frappe.call({
                                method: "nafed_erp.meeting_and_co_ordination.doctype.board_members.board_members.inactivate_member",
                                args: {
                                    docname: frm.doc.name,
                                    reason: values.reason
                                },
                                callback: function () {
                                    frm.reload_doc();
                                }
                            });
                        },
                        __("Confirm In-Activation"),
                        __("Submit")
                    );

                }, __('Actions'));
            }
        }
    }
});

