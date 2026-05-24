frappe.ui.form.on("Project", {
    refresh: function (frm) {
        set_project_read_only(frm);
        remove_add_button_from_dashboard(frm);
        create_button_for_purchase_invoice(frm);
        create_button_for_sales_invoice(frm);
    },
    custom_division: function (frm) {
        toggle_apply_workflow(frm);
    }
});

function set_project_read_only(frm) {
    const editable_states = ["Draft", "Pending for Approval"];
    const always_editable_fields = ["status", "is_active"];
    if (!frm.is_new() && !editable_states.includes(frm.doc.workflow_state)) {

        frm.fields.forEach(field => {
            if (
                field.df &&
                field.df.fieldname&&
                !field.df.read_only &&
                !always_editable_fields.includes(field.df.fieldname)
            ) {
                frm.set_df_property(field.df.fieldname, "read_only", 1);
            }
        });

        frm.dashboard.set_headline("This project is locked after approval");
    }
}

function toggle_apply_workflow(frm) {
    if (frm.doc.custom_division) {
        frm.set_value("custom_apply_workflow", 1);
    } else {
        frm.set_value("custom_apply_workflow", 0);
    }
}

function remove_add_button_from_dashboard(frm) {

    const doctypes_to_hide = [
        "Purchase Invoice",
        "Task",
        "Activity Progress Log",
        "Project Extension Request",
        "Sales Invoice"
    ];

    setTimeout(() => {
        doctypes_to_hide.forEach(doctype => {
            $(`a:contains("${doctype}")`)
                .closest('.document-link')
                .find('.btn-new')
                .hide();
        });
    }, 300);
}

function create_button_for_purchase_invoice(frm) {

    if (
        frm.doc.status === "Completed" &&
        frm.doc.custom_technical_partner &&
        frm.doc.estimated_costing && 
        frm.doc.custom_approval_status =="Approved"
    ) {

        let remaining = flt(frm.doc.estimated_costing) - flt(frm.doc.total_purchase_cost || 0);

        if (remaining > 0) {

            frm.add_custom_button(
                "Purchase Invoice",
                function () {

                    frappe.model.open_mapped_doc({
                        method: "nafed_erp.project_management.doc_events.project.create_project_purchase_invoice",
                        frm: frm,
                        args: {
                            source_name: frm.doc.name
                        }
                    });

                },
                "Create"
            );

        }

    }
}


function create_button_for_sales_invoice(frm) {

    if (
        frm.doc.status !== "Cancelled" &&
        frm.doc.custom_approval_status === "Approved" &&
        frm.doc.customer &&
        frm.doc.custom_technical_partner &&
        frm.doc.custom_estimated_margin_percent
    ) {

        frm.add_custom_button(
            "Sales Invoice",
            function () {

                frappe.model.open_mapped_doc({
                    method: "nafed_erp.project_management.doc_events.project.create_project_sales_invoice",
                    frm: frm,
                    args: {
                        source_name: frm.doc.name
                    }
                });

            },
            "Create"
        );
    }
}

frappe.ui.form.on("Project", {
    async custom_technical_partner(frm) {

        if (!frm.doc.custom_technical_partner) {
            frm.set_value("customer", null);
            return;
        }

        let supplier = frm.doc.custom_technical_partner;

        // Case 1: Supplier is secondary_party
        let case1 = await frappe.db.get_list("Party Link", {
            filters: {
                secondary_party: supplier,
                secondary_role: "Supplier",
                primary_role: "Customer"
            },
            fields: ["primary_party"],
            limit: 1
        });

        if (case1.length > 0) {
            frm.set_value("customer", case1[0].primary_party);
            return;
        }

        // Case 2: Supplier is primary_party
        let case2 = await frappe.db.get_list("Party Link", {
            filters: {
                primary_party: supplier,
                primary_role: "Supplier",
                secondary_role: "Customer"
            },
            fields: ["secondary_party"],
            limit: 1
        });

        if (case2.length > 0) {
            frm.set_value("customer", case2[0].secondary_party);
            return;
        }

        frappe.msgprint("No linked Customer found for this Technical Partner.");
        frm.set_value("customer", null);
    }
});