import frappe
import random
import string
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
from frappe.utils import today
from frappe import _


class NafedTrainingMeeting(Document):

    def validate(self):
        self.validate_time()
        if self.meeting_date and str(self.meeting_date) < today():
            frappe.throw(_("Back date entry is not allowed"))
            
        from frappe.utils import date_diff
        from frappe.utils import getdate
        start_date = getdate(self.meeting_date)
        end_date = getdate(self.meeting_end_date)
        if start_date and end_date:
        	duration = (end_date - start_date).days + 1
        else:
        	self.duration=0

    def validate_time(self):
         if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                frappe.throw(_("End Time must be greater than Start Time"))

    def on_update_after_submit(self):
        before = self.get_doc_before_save()
        if not before:
            return

        old_status_map = {
            row.name: row.attendance_status
            for row in before.attendees
        }

        newly_present = []

        for row in self.attendees:
            old_status = old_status_map.get(row.name)

            # ✅ ONLY changed rows
            if old_status != "Present" and row.attendance_status == "Present":
                newly_present.append(row)

        # Send mail ONLY when someone newly becomes Present
        if newly_present:
            send_feedback_to_all_attendees(self.name)

    
    def on_submit(self):

        # -------- APPROVED --------
        if self.workflow_state == "Approved":

            frappe.db.set_value("Trainer", self.trainer, "status", "Occupied")
            frappe.db.set_value("Meeting Links", self.custom_meet_links, "status", "Inactive")

            if not self.custom_session_id:
                session_id = self.generate_session_id()
                self.db_set("custom_session_id", session_id)

            frappe.msgprint("Invite Sent for the meeting")


        # -------- REJECTED --------
        if self.workflow_state == "Rejected":

            frappe.db.set_value("Trainer", self.trainer, "status", "Available")
            frappe.db.set_value("Meeting Links", self.custom_meet_links, "status", "Active")

            self.db_set("custom_session_id", None)

            frappe.msgprint("Meeting cancelled")


        # ------------------------------------
        # ORIGINAL CODE BELOW (UNCHANGED)
        # ------------------------------------
        base_url = frappe.utils.get_url()

        # ORIGINAL JOIN/LEAVE EMAIL (UNCHANGED)
        for att in self.attendees:

            join_url = f"{base_url}/api/method/nafed_erp.api.join_meeting?meeting={self.name}&emp={att.employee}"
            leave_url = f"{base_url}/api/method/nafed_erp.api.leave_meeting?meeting={self.name}&emp={att.employee}"
            feedback_url = f"{base_url}/api/method/nafed_erp.api.feedback_form?meeting={self.name}&employee={att.employee}"

            message = f"""
<p>Dear {att.employee_name},</p>

<p>You are invited to the training: <b>{self.meeting_title}</b></p><br>

<!-- Join Button -->
<table cellspacing="0" cellpadding="0">
  <tr>
    <td align="center" bgcolor="#1a73e8" style="border-radius:4px;">
      <a href="{join_url}" target="_blank" 
      style="padding:10px 20px; display:inline-block; font-size:14px; 
      color:#ffffff; text-decoration:none;">
        Join Meeting
      </a>
    </td>
  </tr>
</table>
<br>

Regards,<br>{self.organizer}
"""
            if att.company_email:
                frappe.sendmail(
                    recipients=att.company_email,
                    subject=f"Training Invitation: {self.meeting_title}",
                    message=message
                )
            else:
                frappe.sendmail(
                    recipients=att.personal_email,
                    subject=f"Training Invitation: {self.meeting_title}",
                    message=message
                )

        # NEW: OFFLINE VENUE EMAIL
        if self.custom_meeting == "Offline":
            send_offline_emails(self)

    # --------------------------------------
    # NEW FUNCTION — Session ID Generator
    # --------------------------------------
    def generate_session_id(self):
        prefix = "SES"
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}-{random_str}"

    def on_cancel(self):
        frappe.db.set_value("Trainer", self.trainer, "status", "")
        frappe.db.set_value("Meeting Links", self.custom_meet_links, "status", "")

# -------------------------------
# OFFLINE EMAIL FUNCTION (UNCHANGED)
# -------------------------------
def send_offline_emails(doc):
    for att in doc.attendees:
        email = att.personal_email
        if not email:
            continue

        message = f"""
<p>Dear {att.employee_name},</p>

<p>This training will be conducted <b>Offline</b>. Please find the venue details below:</p>

<p>
<b>Venue:</b> {doc.custom_venue}<br>
<b>Date:</b> {doc.meeting_date}<br>
<b>Time:</b> {doc.start_time}
</p>

<p>Please reach the venue on time.</p>

Regards,<br>
Training Team
"""

        frappe.sendmail(
            recipients=att.personal_email,
            subject=f"Offline Training Venue Details – {doc.meeting_title}",
            message=message
        )



# ------------------------------
# UPDATED ATTENDANCE FUNCTION (UNCHANGED)
# ------------------------------
@frappe.whitelist()
def mark_training_attendance(docname):
    meeting = frappe.get_doc("Nafed Training Meeting", docname)
    today = frappe.utils.today()

    for att in meeting.attendees:
        emp = att.employee
        status = att.attendance_status if att.attendance_status else "Present"
        print(status)
        if not frappe.db.exists("Nafed Attendance", {
            "employee": emp,
            "attendance_date": today
        }):
        
            doc = frappe.get_doc({
                "doctype": "Nafed Attendance",
                "employee": emp,
                "attendance_date": today,
                "status": status,
                "training_id":meeting

                # "in_time": None,
                # "out_time": None
            })
            doc.name = f"NFA-{emp}-{today}"
            att.attendance_status ="Present"
            doc.insert(ignore_permissions=True)
            doc.submit()

    return "Attendance marked in Nafed Attendance for all employees."


@frappe.whitelist()
def send_feedback_to_all_attendees(meeting):
    doc = frappe.get_doc("Nafed Training Meeting", meeting)
    base_url = frappe.utils.get_url()

    for att in doc.attendees:
        if att.attendance_status != "Present":
            continue

        email = att.company_email or att.personal_email
        if not email:
            continue

        feedback_link_meeting = (
            f"{base_url}/feedback-form-submission/new"
            f"?employee={att.employee}&meeting={doc.name}&feedback_type=Meeting"
        )

        feedback_link_trainer = (
            f"{base_url}/feedback-form-submission/new"
            f"?employee={att.employee}&meeting={doc.name}&feedback_type=Trainer"
        )

        message = f"""
            <p>Dear {att.employee_name},</p>

            <p>Please submit your feedback for the training <b>{doc.meeting_title}</b>.</p>
            <p>
                <a href="{feedback_link_meeting}" target="_blank"
                style="padding:10px 20px; background:#1a73e8; color:white; border-radius:4px; text-decoration:none;">
                Submit Feedback For Training
                </a>
            </p>

            <p>Please submit your feedback for the Instructor <b>{doc.meeting_title}</b>.</p>
            <p>
                <a href="{feedback_link_trainer}" target="_blank"
                style="padding:10px 20px; background:#1a73e8; color:white; border-radius:4px; text-decoration:none;">
                Submit Feedback For Instructor
                </a>
            </p>

            <br>Regards,<br>Training Team
        """

        frappe.sendmail(
            recipients=[email],
            subject=f"Submit Feedback — {doc.meeting_title}",
            message=message
        )


def update_trainer_availability():
    """Update Trainer availability if meeting has ended"""

    current_time = now_datetime()

    meetings = frappe.get_all(
        "Nafed Training Meeting",
        filters={"docstatus": 1},   # only submitted meetings
        fields=["name", "trainer", "meeting_date", "end_time","custom_meet_links"]
    )

    for m in meetings:
        if not m.trainer:
            continue

        # Convert meeting end datetime
        meeting_end = get_datetime(f"{m.meeting_date} {m.end_time}")

        # If meeting finished → trainer becomes available
        if current_time > meeting_end:
            try:
                frappe.db.set_value("Trainer", m.trainer, "status", "Available")
                frappe.db.set_value("Meeting Links", m.custom_meet_links, "status", "Active")
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Trainer Status Update Failed")


