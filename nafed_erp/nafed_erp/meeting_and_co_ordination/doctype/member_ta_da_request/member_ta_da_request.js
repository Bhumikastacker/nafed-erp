// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Member TA DA Request", {
 
 refresh(frm) {
    

	if (frm.is_new()) return;
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
                                method: "nafed_erp.meeting_and_co_ordination.doctype.member_ta_da_request.member_ta_da_request.approval_remarks",
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
    },
 
 	da_amount: function(frm) {
        calculate_total(frm);
    },
    number_of_days: function(frm) {
        calculate_total(frm);
    },
    
    additional_amount: function(frm) {
        final_amount(frm);
    },
    
    fare_2: function(frm) {
        final_amount(frm);
    },
    
    fare_c: function(frm) {
        final_amount(frm);
    },
    
    total_da: function(frm) {
        final_amount(frm);
    },
 });
 
 
 function calculate_total(frm) {
    frm.set_value('total_da', (frm.doc.da_amount || 0) * (frm.doc.number_of_days || 0));
}

function final_amount(frm) {
    frm.set_value('total_amount', (frm.doc.fare_c || 0) + (frm.doc.fare_2 || 0)+ (frm.doc.additional_amount || 0)+  (frm.doc.total_da || 0));
}
