import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class DisasterRecoveryPlan(Document):

    def validate(self):
        self.validate_completeness()
        self.validate_consistency()

    def validate_completeness(self):
        mandatory = [
            "rto", "rpo",
            "backup_type", "backup_frequency",
            "replication_method", "dr_site_id"
        ]

        for field in mandatory:
            if not self.get(field):
                frappe.throw(f"{self.meta.get_label(field)} is required")

        if not self.contacts:
            frappe.throw("At least one Contact must be defined")

        if not self.runbook_refs and not self.automation_runbooks:
            frappe.throw("Runbook or Automation Runbook is required")

    def validate_consistency(self):
        if self.replication_method == "Asynchronous" and self.rpo:
            if self.rpo.total_seconds() < 3600:
                frappe.throw(
                    "RPO less than 1 hour is not allowed with Asynchronous replication"
                )

        if self.backup_frequency == "Monthly" and self.rto:
            if self.rto.total_seconds() < 86400:
                frappe.throw(
                    "Monthly backups cannot support RTO less than 24 hours"
                )

    def on_update(self):
        if self.workflow_state == "Draft":
            self.db_set("approval_status", "Draft")
        if self.workflow_state == "Pending for Approval":
            self.db_set("approval_status", "In Review")
        if self.workflow_state == "Approved":
            self.db_set("approval_status", "Approved")
        if self.approval_status == "Approved" and self._approval_just_changed():
            self.finalize_plan()
            
    def _approval_just_changed(self):
        if self.is_new():
            return False

        previous = frappe.db.get_value(
            "Disaster Recovery Plan",
            self.name,
            "approval_status"
        )
        return previous != "Approved"



    def finalize_plan(self):
        self.db_set("last_modified_on", frappe.utils.today())
        self.db_set("last_modified_by", frappe.session.user)
        self.notify_users()

    def notify_users(self):
        recipients = list(filter(None, [
            self.business_owner_id,
            self.application_owner_id
        ]))

        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject="Disaster Recovery Plan Approved",
                message=f"""
                DR Plan <b>{self.name}</b><br>
                Version <b>{self.plan_version}</b> has been approved.
                """
            )



@frappe.whitelist()
def create_revision(plan_name):
    source = frappe.get_doc("Disaster Recovery Plan", plan_name)

    if source.approval_status != "Approved":
        frappe.throw("Only Approved DR Plans can be updated")

    def postprocess(src, tgt):
        tgt.plan_version = (src.plan_version or 1) + 1
        tgt.approval_status = "Draft"
        tgt.created_on = frappe.utils.today()
        tgt.created_by = frappe.session.user
        tgt.last_modified_on = None
        tgt.last_modified_by = None

    new_doc = get_mapped_doc(
        "Disaster Recovery Plan",
        plan_name,
        {
            "Disaster Recovery Plan": {"doctype": "Disaster Recovery Plan"},
            "DR and Backup Contact List": {"doctype": "DR and Backup Contact List"},
            "DR Backup Role Responsible": {"doctype": "DR Backup Role Responsible"},
            "DR Backup Supporting Documents": {"doctype": "DR Backup Supporting Documents"},
        },
        postprocess=postprocess
    )

    new_doc.insert(ignore_permissions=True)
    return new_doc.name
