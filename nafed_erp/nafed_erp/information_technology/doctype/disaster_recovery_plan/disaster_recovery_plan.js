frappe.ui.form.on("Disaster Recovery Plan", {

    refresh(frm) {

        const is_approved = frm.doc.approval_status === "Approved";
        frm.toggle_enable([
            "plan_name", "environment", "criticality",
            "rto", "rpo", "priority",
            "backup_type", "backup_frequency", "retention_policy",
            "storage_target", "backup_windows", "retention_period",
            "failover_type", "replication_method", "dr_site_id",
            "dnsrouting_changes", "failback_procedure",
            "order_of_recovery", "runbook_refs",
            "automation_runbooks", "contacts",
            "role_responsible", "supporting_artifacts"
        ], !is_approved);
        
        if (!frm.is_new() && is_approved) {
            frm.add_custom_button(__("Update Plan"), () => {
            frappe.call({
                method: "nafed_erp.information_technology.doctype.disaster_recovery_plan.disaster_recovery_plan.create_revision",
                args: { plan_name: frm.doc.name },
                callback(r) {
                    if (r.message) {
                        frappe.set_route("Form", "Disaster Recovery Plan", r.message);
                    }
                }
            });
        });
        }
    },

    before_save() {
        return new Promise((resolve, reject) => {
            frappe.confirm(
                __("Do you want to save this Disaster Recovery Plan?"),
                () => resolve(),
                () => reject()
            );
        });
    },

    validate(frm) {
        const mandatory = [
            "rto", "rpo",
            "backup_type", "backup_frequency",
            "replication_method", "dr_site_id"
        ];

        mandatory.forEach(f => {
            if (!frm.doc[f]) {
                frappe.throw(__(`${frm.fields_dict[f].df.label} is mandatory`));
            }
        });
    }
});
