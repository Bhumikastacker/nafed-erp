// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Board Communication", {
    status(frm) {
    if (
        ["Approved", "Rejected"].includes(frm.doc.status) &&
        !frm.doc.reason
    ) {
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
                frm.set_value("reason", values.reason);
            },
            __("Update Reason"),
            __("Submit")
        );
    }
},

 	refresh(frm) {
    
	const readonly = ["Approved", "Rejected"].includes(frm.doc.status);

        // Fields that should remain editable


        frm.fields.forEach(field => {


                frm.set_df_property(field.df.fieldname, "read_only", readonly);
            

        });

        frm.clear_custom_buttons();

        if (frm.doc.status === "Approved") {
            frm.add_custom_button(__('Send Mail'), () => {
                frappe.call({
                    method: "nafed_erp.meeting_and_co_ordination.doctype.board_communication.board_communication.send_board_communication_mail",
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function (r) {
                        frappe.msgprint(r.message || "Mail sent successfully");
                        frm.reload_doc();
                    }
                });
            });
        }

     setTimeout(() => {
    $(".timeline-item").each(function () {

        let current_text = $(this).text().trim();

        if (current_text.includes(" assigned ")) {

            let parts = current_text.split(" assigned ");

            let assigned_by = parts[0].trim();
            let assigned_to = parts[1]?.split(":")[0]?.trim() || "";

            let new_text =
                frm.doc.name +
                "Sent to  " +
                assigned_to +
                " By " +
                assigned_by;

            $(this).html(new_text);
        }
    });
}, 2000);

	  if (frm.doc.status === "Submitted" &&  !frm.doc.reason) {
	  
	  	frm.add_custom_button(__('Update Reason'), () => {

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
                                method: "nafed_erp.meeting_and_co_ordination.doctype.board_communication.board_communication.approval_remarks",
                                args: {
                                    docname: frm.doc.name,
                                    reason: values.reason
                                },
                                callback: function () {
                                    frm.reload_doc();
                                }
                            });
                        },
                        __("Confirm"),
                        __("Submit")
                    );

                }, __('Update Remarks for Approval/Rejection'));
	  
	  
     }   
    }
});
