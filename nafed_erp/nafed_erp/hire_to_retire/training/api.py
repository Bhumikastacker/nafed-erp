import frappe

@frappe.whitelist(allow_guest=True)
def mark_attendance(meeting, emp):
    doc = frappe.get_doc("Nafed Training Meeting", meeting)

    for att in doc.attendees:
        if att.employee == emp:
            att.attendance_status = "Present"
            att.join_time = frappe.utils.now_datetime()
            print("/////////////////",att.join_time)
            doc.save(ignore_permissions=True)
            return {"status": "success"}

    return {"status": "error", "message": "Employee not in attendee list"}


@frappe.whitelist(allow_guest=True)
def submit_feedback(meeting, employee, rating, comments):
    fb = frappe.new_doc("Nafed Training Feedback")
    fb.meeting = meeting
    fb.employee = employee
    fb.rating = rating
    fb.comments = comments
    fb.save(ignore_permissions=True)
    return {"status": "success"}
