import frappe
from frappe.model.document import Document
from frappe.utils import getdate,flt,nowdate
from frappe import _


class ActivityProgressLog(Document):

    def validate(self):
        self.validate_fields()
        self.validate_planning_completion()
        self.validate_activity_and_milestone_status()

    def validate_fields(self):
        # Skip validation if mandatory fields are missing
        if not (
            self.activity
            and self.actual_start_date
            and self.actual_end_date
        ):
            return

        activity = frappe.get_doc("Task", self.activity)

        # Ensure planned dates exist on Activity (Task)
        if not activity.exp_start_date or not activity.exp_end_date:
            frappe.throw(
                _("Planned Start Date and Planned End Date must be set for the Activity before updating progress.")
            )

        if activity.status not in ["Open", "Working"]:
            frappe.throw(_("This Activity's Status is not Open or Working. No further progress can be logged."))

        if self.activity_progress_percent>100 or self.activity_progress_percent<=0:
            frappe.throw(_("Activity Progress must be between 1 and 100"))

        # Normalize dates
        planned_start_date = getdate(activity.exp_start_date)
        planned_end_date = getdate(activity.exp_end_date)
        actual_start_date = getdate(self.actual_start_date)
        actual_end_date = getdate(self.actual_end_date)

        # Actual start cannot be after actual end
        if actual_start_date > actual_end_date:
            frappe.throw(
                _("Actual Start Date cannot be later than Actual End Date.")
            )

        # Actual start cannot be before planned start
        if actual_start_date < planned_start_date:
            frappe.throw(
                _("Actual Start Date cannot be before the planned Activity Start Date ({0}).")
                .format(planned_start_date)
            )

        # Actual end cannot be after planned end
        if actual_end_date > planned_end_date:
            frappe.throw(
                _("Actual End Date cannot be after the planned Activity End Date ({0}).")
                .format(planned_end_date)
            )

    def validate_planning_completion(self):
        self.validate_activity_weights_under_milestone()
        self.validate_milestone_weights_under_project()

    # -------------------------
    # Milestone-level validation
    # -------------------------
    def validate_activity_weights_under_milestone(self):
        if not self.milestone:
            return

        activities = frappe.get_all(
            "Task",
            filters={
                "parent_task": self.milestone,
                "is_group": 0,
                "status": ["!=", "Cancelled"]
            },
            fields=["task_weight"]
        )

        total_activity_weight = sum(a.task_weight or 0 for a in activities)

        if total_activity_weight != 100:
            frappe.throw(
                _(
                    "Cannot update progress.<br>"
                    "Activity planning is incomplete for Milestone <b>{0}</b>.<br>"
                    "Total Activity Weight: <b>{1}%</b> (must be 100%)."
                ).format(self.milestone, total_activity_weight)
            )

    # -------------------------
    # Project-level validation
    # -------------------------
    def validate_milestone_weights_under_project(self):
        if not self.project:
            return

        milestones = frappe.get_all(
            "Task",
            filters={
                "project": self.project,
                "is_group": 1,
                "status": ["!=", "Cancelled"]
            },
            fields=["task_weight"]
        )

        total_milestone_weight = sum(m.task_weight or 0 for m in milestones)

        if total_milestone_weight != 100:
            frappe.throw(
                _(
                    "Cannot update progress.<br>"
                    "Milestone planning is incomplete for Project <b>{0}</b>.<br>"
                    "Total Milestone Weight: <b>{1}%</b> (must be 100%)."
                ).format(self.project, total_milestone_weight)
            )

    def validate_activity_and_milestone_status(doc):
        if not doc.activity:
            return

        # 🔹 Fetch Activity
        activity = frappe.db.get_value(
            "Task",
            doc.activity,
            ["status", "parent_task"],
            as_dict=True
        )

        if not activity:
            frappe.throw(_("Linked Activity not found"))

        # 1️⃣ Validate Activity status
        if activity.status not in ("Open", "Working"):
            frappe.throw(_(
                "Cannot record progress.<br>"
                "Activity status must be <b>Open</b> or <b>Working</b>.<br>"
                "Current Activity status: <b>{0}</b>"
            ).format(activity.status))

        # 🔹 Fetch Milestone (parent task)
        if not activity.parent_task:
            frappe.throw(_("Activity is not linked to any Milestone"))

        milestone = frappe.db.get_value(
            "Task",
            activity.parent_task,
            ["status", "custom_approval_status"],
            as_dict=True
        )

        if not milestone:
            frappe.throw(_("Linked Milestone not found"))

        # 2️⃣ Validate Milestone approval
        if milestone.custom_approval_status != "Approved":
            frappe.throw(_(
                "Cannot record progress.<br>"
                "Milestone must be <b>Approved</b> before logging progress.<br>"
                "Current Approval Status: <b>{0}</b>"
            ).format(milestone.custom_approval_status))

        # 3️⃣ Validate Milestone execution status
        if milestone.status not in ("Open", "Working"):
            frappe.throw(_(
                "Cannot record progress.<br>"
                "Milestone status must be <b>Open</b> or <b>Working</b>.<br>"
                "Current Milestone status: <b>{0}</b>"
            ).format(milestone.status))


    def on_submit(self):
        self.update_activity_progress()
        self.update_higher_levels()

    def update_higher_levels(self):
        # Activity → Milestone
        if self.milestone:
            self.update_milestone_progress(self.milestone)

        # Milestone → Project
        if self.project:
            self.update_project_progress(self.project)

    def update_activity_progress(self):
        activity = frappe.get_doc("Task", self.activity)

        # Safety checks
        if activity.is_group:
            frappe.throw(_("Progress can only be logged for Activities, not Milestones."))

        new_progress = flt(self.activity_progress_percent)
        current_progress = flt(activity.progress)

        # Prevent progress regression
        if new_progress < current_progress:
            frappe.throw(
                _("Progress cannot be reduced. Current progress is {0}%.")
                .format(current_progress)
            )

        # Normalize progress
        if new_progress >= 100:
            activity.progress = 100
            activity.status = "Completed"
            activity.completed_on = getdate(nowdate())
        elif new_progress > 0:
            activity.progress = new_progress
            activity.status = "Working"
        else:
            activity.progress = 0
            activity.status = "Open"

        # ✅ ONLY save — no db.set_value
        activity.save(ignore_permissions=True)



    def update_milestone_progress(self, milestone_name):
        milestone = frappe.get_doc("Task", milestone_name)

        activities = frappe.get_all(
            "Task",
            filters={
                "parent_task": milestone_name,
                "is_group": 0,
                "status": ["!=", "Cancelled"]
            },
            fields=["progress", "task_weight"]
        )

        total_weight = sum(a.task_weight or 0 for a in activities)

        # No activities or no weight
        if total_weight == 0:
            milestone.progress = 0
            milestone.status = "Open"
            milestone.save(ignore_permissions=True)
            return

        weighted_progress = sum(
            (a.progress or 0) * (a.task_weight or 0)
            for a in activities
        )

        updated_progress = round(weighted_progress / total_weight, 2)
        updated_progress = min(updated_progress, 100)

        milestone.progress = updated_progress

        if 0 < updated_progress < 100:
            milestone.status = "Working"
        elif updated_progress == 100:
            milestone.status = "Completed"
            milestone.completed_on = getdate(nowdate())
        else:
            milestone.status = "Open"

        # ✅ ONLY save — no db.set_value
        milestone.save(ignore_permissions=True)



    def update_project_progress(self, project_name):
        project = frappe.get_doc("Project", project_name)

        milestones = frappe.get_all(
            "Task",
            filters={
                "project": project_name,
                "is_group": 1,
                "status": ["!=", "Cancelled"]
            },
            fields=["progress", "task_weight"]
        )

        total_weight = sum(m.task_weight or 0 for m in milestones)

        # No milestones or no weight
        if total_weight == 0:
            project.percent_complete = 0
            project.status = "Open"
            project.save(ignore_permissions=True)
            return

        weighted_progress = sum(
            (m.progress or 0) * (m.task_weight or 0)
            for m in milestones
        )

        progress = round(weighted_progress / total_weight, 2)
        progress = min(progress, 100)

        project.percent_complete = progress

        if 0 < progress < 100:
            project.status = "Open"
        elif progress == 100:
            project.status = "Completed"

        # ✅ ONLY save — no db.set_value
        project.save(ignore_permissions=True)

