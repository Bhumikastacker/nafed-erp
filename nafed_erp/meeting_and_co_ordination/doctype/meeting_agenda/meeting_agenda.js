frappe.ui.form.on("Meeting Agenda", {
    refresh(frm) {
	if (frm.is_new()) return;
        const readonly = ["Approved", "Rejected"].includes(frm.doc.status);

        // Fields that should remain editable


        frm.fields.forEach(field => {


                frm.set_df_property(field.df.fieldname, "read_only", readonly);
            

        });
        

        if (frm.is_new()) return;

        frm.clear_custom_buttons();


	        if (!frm.doc.check_agend_from_div) {
		
            
            frm.add_custom_button("Send Draft Agenda To Division", function () {

                    frappe.call({
                                method: "nafed_erp.meeting_and_co_ordination.doctype.meeting_agenda.meeting_agenda.send_configured_mail",
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

