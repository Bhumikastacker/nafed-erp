// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Meeting MoM", {
 	refresh(frm) {
    
	 const readonly = ["Approved", "Rejected"].includes(frm.doc.status);

        // Fields that should remain editable


        frm.fields.forEach(field => {


                frm.set_df_property(field.df.fieldname, "read_only", readonly);
            

        });
        frm.clear_custom_buttons();

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
                                method: "nafed_erp.meeting_and_co_ordination.doctype.meeting_mom.meeting_mom.approval_remarks",
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
   

	        if (!frm.doc.check_mom_from_div) {
		
            
            frm.add_custom_button("Send MoM Mails To Division", function () {

                    frappe.call({
                                method: "nafed_erp.meeting_and_co_ordination.doctype.meeting_mom.meeting_mom.send_configured_mail",
                                args: {
                                    docname: frm.doc.name
                                },
                                callback: function(r) {
                                    frappe.msgprint("Mail Sent Successfully");
                                }
                            });
                });
            
        }
        
        
   }
});

