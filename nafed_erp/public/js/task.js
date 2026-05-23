//CODE WRITTEN FOR CRI AND OFD DIVISION PROJECTS 

frappe.ui.form.on("Task", {
    refresh(frm) {
        set_milestone_read_only(frm);
        show_purchase_invoice_button(frm);
        const always_editable_fields = ["exp_end_date", "status", "completed_on", "completed_by"]; // 👈 whitelist
        if (!frm.doc.is_group && frm.doc.parent_task && frm.doc.custom_apply_workflow && frm.doc.custom_technical_partner) {

            frappe.db.get_value(
                "Task",
                frm.doc.parent_task,
                "custom_approval_status",
                (r) => {
                    if (r && r.custom_approval_status === "Approved") {
                        // Make all fields read-only
                        frm.fields.forEach(field => {
                            if (field.df && field.df.fieldname && !field.df.read_only &&!always_editable_fields.includes(field.df.fieldname)) {
                                frm.set_df_property(field.df.fieldname, "read_only", 1);
                            }
                        });


                        // UX message
                        frm.dashboard.set_headline(
                            "This Activity is locked because its Milestone is approved"
                        );
                    }
                }
            );
        }
    },
    project: function (frm) {
        if (frm.doc.project) {
            fetch_project_fields(frm);
        }
    }
});

function set_milestone_read_only(frm) {
    const editable_states = ["Draft", "Pending for Approval"];
    const always_editable_fields = ["exp_end_date", "status", "completed_on", "completed_by"]; // 👈 whitelist

    if (
        !frm.is_new() &&
        !editable_states.includes(frm.doc.workflow_state)
    ) {

        // Make all fields read-only except allowed ones
        frm.fields.forEach(field => {
            if (
                field.df &&
                field.df.fieldname &&
                !field.df.read_only &&
                !always_editable_fields.includes(field.df.fieldname)
            ) {
                frm.set_df_property(field.df.fieldname, "read_only", 1);
            }
        });

        // UX message
        frm.dashboard.set_headline("This Milestone is locked after approval");
    }
}

function fetch_project_fields(frm) {
    frappe.db.get_value(
        "Project",
        frm.doc.project,
        ["custom_division", "custom_technical_partner","custom_apply_workflow"],
        function (r) {
            if (r) {
                frm.set_value("custom_division", r.custom_division);
                frm.set_value("custom_technical_partner", r.custom_technical_partner);
                frm.set_value("custom_apply_workflow", r.custom_apply_workflow);
            }
        }
    );
}

function show_purchase_invoice_button(frm) {
    if (
        frm.doc.status === "Completed" &&
        frm.doc.project &&
        frm.doc.custom_estimated_cost && 
        frm.doc.custom_technical_partner && 
        frm.doc.custom_approval_status=="Approved"
    ) {
        
        let remaining = flt(frm.doc.custom_estimated_cost) - flt(frm.doc.custom_billed_amount || 0);

        if (remaining > 0) {

            frm.add_custom_button(
                __("Purchase Invoice"),
                function () {

                    frappe.model.open_mapped_doc({
                        method: "nafed_erp.project_management.doc_events.project.create_project_purchase_invoice",
                        frm: frm,
                        args: {
                            source_name: frm.doc.name
                        }
                    });

                },
                __("Create")
            );

        }
    }
}

frappe.ui.form.on('Task', {
    completed_on: function(frm) {

        // 👉 Agar custom_technical_partner filled hai, to kuch mat karo
        if (frm.doc.custom_technical_partner) {
            return;
        }

        // 👉 Agar completed_on empty hai
        if (!frm.doc.completed_on) return;

        let selected_date = frappe.datetime.str_to_obj(frm.doc.completed_on);
        let today = frappe.datetime.str_to_obj(frappe.datetime.get_today());

        // Time remove

        // 👉 Past date check
        if (selected_date < today) {
            frappe.msgprint({
                title: __('Invalid Date'),
                message: __('Previous date is not allowed , Please choose today Date.'),
                indicator: 'red'
            });

            frm.set_value('completed_on', null);
        }
    }
});
