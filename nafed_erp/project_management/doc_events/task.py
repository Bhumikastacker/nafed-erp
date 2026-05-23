##CODE WRITTEN FOR CRI AND OFD DIVISION PROJECTS 

import frappe
from frappe import _
from frappe.utils import flt,getdate

def validate(doc, method):
    validate_weight_range(doc)
    validate_project_not_rejected(doc)
    validate_task_start_date(doc)
    validate_milestone_budget(doc)
    validate_milestone_activity_planning(doc)
    validate_activity_weights_under_milestone(doc)
    validate_activity_creation_when_milestone_completed(doc)
    validate_milestone_weights_under_project(doc)

def validate_weight_range(doc):
    # Applies to both Milestone and Activity
    if not doc.project:
        return
    if not doc.custom_apply_workflow:
        return
    if not doc.custom_division:
        return
    if not doc.custom_technical_partner:
        return
    if not doc.task_weight or doc.task_weight <= 0 or doc.task_weight > 100:
        frappe.throw(
            _("Weight must be between 1 and 100.")
        )

def validate_project_not_rejected(doc):
    if not doc.project:
        return
    
    if not doc.custom_technical_partner:
        return

    project_data = frappe.db.get_value(
        "Project",
        doc.project,
        "custom_approval_status",
        as_dict=True
    )

    # 🔴 Check approval status
    if project_data.custom_approval_status == "Rejected":
        frappe.throw(
            _(f"The selected Project {doc.project} is Rejected. You cannot create or update Tasks for this Project.")
        )

def validate_milestone_activity_planning(doc):
    # Only Milestones
    if not doc.is_group:
        return
    
    if not doc.project:
        return

    if not doc.is_milestone:
        return
    
    if not doc.custom_technical_partner:
        return
    
    if not doc.custom_division:
        return
    
    if not doc.custom_apply_workflow:
        return
    # 🔒 Trigger ONLY when sending for approval
    if doc.custom_approval_status != "Pending for Approval":
        return

    if not doc.depends_on:
        frappe.throw(
            _("Cannot send Milestone <b>{0}</b> for approval.<br>"
              "Please add at least one Activity.")
            .format(doc.subject)
        )

    total_weight = 0
    activity_count = 0

    for row in doc.depends_on:
        if not row.task:
            continue

        activity = frappe.get_doc("Task", row.task)

        if activity.status == "Cancelled":
            continue

        activity_count += 1
        total_weight += activity.task_weight or 0

    # 1️⃣ Must have at least one valid Activity
    if activity_count == 0:
        frappe.throw(
            _("Cannot send Milestone <b>{0}</b> for approval.<br>"
              "No valid Activities found.")
            .format(doc.subject)
        )

    # 2️⃣ Total Activity weight must be exactly 100
    if total_weight != 100:
        frappe.throw(
            _("Cannot send Milestone <b>{0}</b> for approval.<br>"
              "Total Activity Weight is <b>{1}%</b>. It must be exactly <b>100%</b>.")
            .format(doc.subject, total_weight)
        )

#All Validations for Activities
def validate_activity_weights_under_milestone(doc):
    # Only for Activities
    if doc.is_group:
        return

    # Only if Activity has a Milestone
    if not doc.parent_task:
        return

    if not doc.project:
        return
    
    if not doc.custom_technical_partner:
        return
    
    if not doc.custom_division:
        return
    
    if not doc.custom_apply_workflow:
        return
    
    activities = frappe.get_all(
        "Task",
        filters={
            "parent_task": doc.parent_task,
            "is_group": 0,
            "status": ["!=", "Cancelled"],
            "name": ["!=", doc.name]
        },
        fields=["task_weight"]
    )

    total_weight = sum(a.task_weight or 0 for a in activities)
    total_weight += doc.task_weight or 0  # include current activity

    # 🔴 Block ONLY if it exceeds 100
    if total_weight > 100:
        frappe.throw(
            _(
                "Total Activity weight under this Milestone cannot exceed 100.<br>"
                "Current total (including this Activity): <b>{0}</b>"
            ).format(total_weight)
        )


def validate_activity_creation_when_milestone_completed(doc):
    if doc.is_group or not doc.parent_task:
        return

    milestone = frappe.get_doc("Task", doc.parent_task)

    if milestone.progress >= 100:
        frappe.throw(
            _("Cannot add Activities. Milestone is already completed.")
        )



##All Validations for Milestones
def validate_milestone_weights_under_project(doc):
    # Only for Milestones
    if not doc.is_group:
        return

    # Only if Milestone belongs to a Project
    if not doc.project:
        return

    if not doc.is_milestone:
        return
    
    if not doc.custom_technical_partner:
        return
    
    if not doc.custom_division:
        return
    
    if not doc.custom_apply_workflow:
        return
    milestones = frappe.get_all(
        "Task",
        filters={
            "project": doc.project,
            "is_group": 1,
            "status": ["!=", "Cancelled"],
            "name": ["!=", doc.name]
        },
        fields=["task_weight"]
    )

    total_weight = sum(m.task_weight or 0 for m in milestones)
    total_weight += doc.task_weight or 0  # include current milestone

    # 🔴 Block ONLY if it exceeds 100
    if total_weight > 100:
        frappe.throw(
            _(
                "Total Milestone weight under this Project cannot exceed 100.<br>"
                "Current total (including this Milestone): <b>{0}</b>"
            ).format(total_weight)
        )


def validate_milestone_budget(doc, method=None):

    if not doc.project:
        return
    if not doc.custom_technical_partner:
        return
    if not doc.is_milestone:
        return
    
    project = frappe.get_doc("Project", doc.project)

    if not project.estimated_costing:
        return

    # -----------------------------------
    # Sum of all milestone costs
    # -----------------------------------
    total_milestone_cost = frappe.db.sql("""
        SELECT SUM(custom_estimated_cost)
        FROM `tabTask`
        WHERE project = %s
        AND name != %s
    """, (doc.project, doc.name))[0][0] or 0

    # Add current document value
    total_milestone_cost += flt(doc.custom_estimated_cost)

    # -----------------------------------
    # Validation
    # -----------------------------------
    if total_milestone_cost > flt(project.estimated_costing):

        frappe.throw(_(
            "Total Milestone Cost ({0}) exceeds Project Estimated Costing ({1})"
        ).format(
            frappe.format_value(total_milestone_cost, {"fieldtype": "Currency"}),
            frappe.format_value(project.estimated_costing, {"fieldtype": "Currency"})
        ))


def validate_task_start_date(doc, method=None):

    if not doc.exp_start_date:
        return

    task_start = getdate(doc.exp_start_date)

    # -----------------------------------
    # 1️⃣ Validate against Project
    # -----------------------------------
    if doc.project:
        project_start = frappe.db.get_value(
            "Project",
            doc.project,
            "expected_start_date"
        )

        if project_start and task_start < getdate(project_start):
            frappe.throw(
                _("Task Expected Start Date cannot be before Project Expected Start Date ({0})")
                .format(project_start)
            )

    # -----------------------------------
    # 2️⃣ Validate against Parent Task
    # -----------------------------------
    if doc.parent_task:
        parent_start = frappe.db.get_value(
            "Task",
            doc.parent_task,
            "exp_start_date"
        )

        if parent_start and task_start < getdate(parent_start):
            frappe.throw(
                _("Child Task Expected Start Date cannot be before Parent Task Start Date ({0})")
                .format(parent_start)
            )