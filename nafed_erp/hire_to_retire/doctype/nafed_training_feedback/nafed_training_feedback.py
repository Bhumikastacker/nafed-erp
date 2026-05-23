# -*- coding: utf-8 -*-
import frappe
from frappe.utils import now, get_datetime
from frappe import _
from frappe.model.document import Document
from datetime import timedelta


class NafedTrainingFeedback(Document):

    def validate(self):
        # --- Rating Must Be Present ---
        if not self.rating:
            frappe.throw(_("Rating is mandatory."))

        # --- Rating Score (your ×5 logic kept) ---
        try:
            self.rating_score = float(self.rating) * 5
        except:
            self.rating_score = 0.0

        # --- Submission Date ---
        self.submission_date = now()

        # --- Feedback Window Check (Meeting End + 3 Days) ---
        if self.meeting:
            meeting = frappe.get_doc("Nafed Training Meeting", self.meeting)

            if meeting.end_time:
                meeting_end = get_datetime(str(meeting.end_time))
                cutoff = meeting_end + timedelta(days=3)

                if get_datetime(now()) > cutoff:
                    frappe.throw(_("Feedback window expired for this session."))

    def on_update(self):
        if self.meeting:
            update_aggregated_score(self.meeting, self.feedback_type)


def update_aggregated_score(meeting_name, feedback_type):
    """Recalculate average rating for a meeting"""

    ratings = frappe.get_all(
        "Nafed Training Feedback",
        filters={
            "meeting": meeting_name,
            "feedback_type": feedback_type
        },
        fields=["rating_score"]
    )

    if not ratings:
        field = (
            "custom_aggregated_score"
            if feedback_type == "Meeting"
            else "custom_trainer_aggregated_score"
        )

        frappe.db.set_value(
            "Nafed Training Meeting",
            meeting_name,
            field,
            0.0
        )
        return

    total = sum(float(r.rating_score or 0) for r in ratings)
    avg = total / len(ratings)

    if feedback_type == "Meeting":
        frappe.db.set_value(
            "Nafed Training Meeting",
            meeting_name,
            "custom_aggregated_score",
            avg
        )

    elif feedback_type == "Trainer":
        frappe.db.set_value(
            "Nafed Training Meeting",
            meeting_name,
            "custom_trainer_aggregated_score",
            avg
        )
