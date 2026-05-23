import frappe 
from frappe.utils import getdate
from frappe.email.doctype.notification.notification import evaluate_alert

def validate(doc, method):
    set_leave_approver_based_on_employee_rules(doc)


@frappe.whitelist()
def send_leave_approval_mail(docname):
    doc = frappe.get_doc("Leave Application", docname)

    notifications = frappe.get_all(
        "Notification",
        filters={
            "document_type": "Leave Application",
            "event": "Custom",
            "enabled": 1
        },
        pluck="name"
    )

    for notification_name in notifications:
        alert = frappe.get_doc("Notification", notification_name)
        evaluate_alert(doc, alert, "Custom")

    return "Leave approval notification has been sent successfully."


def set_leave_approver_based_on_employee_rules(doc):
    employee = frappe.get_doc("Employee", doc.employee)
    leave_type = doc.leave_type
    total_days = doc.total_leave_days

    posting_date = getdate(doc.posting_date or doc.creation)

    # -------------------------------------------------
    # Get matching rule
    # -------------------------------------------------
    rule = None
    for r in employee.custom_leave_approvers:
        if r.leave_type == leave_type:
            rule = r
            break

    if not rule:
        frappe.throw(
            f"No Leave Approval Rule defined for Leave Type <b>{leave_type}</b> "
            f"for Employee <b>{doc.employee_name}</b>."
        )

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------
    def get_employee_from_user(user):
        return frappe.db.get_value("Employee", {"user_id": user}, "name")

    def is_employee_on_leave(emp, check_date):
        return frappe.db.exists(
            "Leave Application",
            {
                "employee": emp,
                "from_date": ["<=", check_date],
                "to_date": [">=", check_date],
                "status": "Approved",
                "docstatus": 1
            }
        )

    def get_user_and_name(user):
        name = frappe.db.get_value("User", user, "full_name") or user
        return user, name

    def get_available_approver(approvers):
        for user in approvers:
            if not user:
                continue

            emp = get_employee_from_user(user)
            if not emp:
                continue

            if not is_employee_on_leave(emp, posting_date):
                return user
        return None

    # Check for primary approvers
    if not rule.leave_approver and not rule.upto_days:
        frappe.throw(f"No Primary Leave Approver set for employee {doc.employee_name} for Leave type '{doc.leave_type}'")

    # -------------------------------------------------
    # CASE 1: Single Approver (with fallback)
    # -------------------------------------------------
    if rule.leave_approver:
        approvers = [
            rule.leave_approver,
            rule.second_approver,
            rule.third_approver
        ]

        available = get_available_approver(approvers)
        if not available:
            frappe.throw(
                "Primary, Second and Third approvers are all on leave "
                f"on <b>{posting_date}</b>."
            )

        user_id, emp_name = get_user_and_name(available)
        doc.leave_approver = user_id
        doc.leave_approver_name = emp_name
        return

    
    # -------------------------------------------------
    # CASE 2: Days-Based Approval
    # -------------------------------------------------
    if not rule.upto_days or not rule.approver_upto_days or not rule.approver_above_days:
        frappe.throw(
            f"Leave approval rule for <b>{leave_type}</b> is incomplete. "
            "Please configure Upto Days and both approvers."
        )

    # Decide base approver (upto / above)
    if total_days <= rule.upto_days:
        base_approver = rule.approver_upto_days
    else:
        base_approver = rule.approver_above_days

    approvers = [
        base_approver,
        rule.second_approver,
        rule.third_approver
    ]

    available = get_available_approver(approvers)
    if not available:
        frappe.throw(
            "No available approver found (Primary / Second / Third) "
            f"on <b>{posting_date}</b>."
        )

    user_id, emp_name = get_user_and_name(available)
    doc.leave_approver = user_id
    doc.leave_approver_name = emp_name


def on_submit_status_validation(doc, method=None):
    if doc.status == "Leave Requested":
        frappe.throw("Only Leave Applications with status 'Approved' and 'Rejected' can be submitted")