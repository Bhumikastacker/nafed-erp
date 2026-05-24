import frappe
from frappe.model.document import Document


@frappe.whitelist()
def approve_request(docname):
    """Approve request by Admin"""
    frappe.db.set_value(
        "Account Update Request",
        docname,
        {"approval_status": "Approved"}
    )

    add_log(docname, f"Approved by {frappe.session.user} on {frappe.utils.now_datetime()}")

    frappe.db.commit()
    return "Approved"


@frappe.whitelist()
def reject_request(docname, reason):
    """Reject request by Admin"""
    frappe.db.set_value(
        "Account Update Request",
        docname,
        {
            "approval_status": "Rejected",
            "reason_for_rejection": reason
        }
    )

    add_log(
        docname,
        f"Rejected by {frappe.session.user} | Reason: {reason} | Date: {frappe.utils.now_datetime()}"
    )

    frappe.db.commit()
    return "Rejected"


def add_log(docname, log_entry):
    """Append logs to approval_log field"""
    existing = frappe.db.get_value("Account Update Request", docname, "approval_log") or ""
    new_log = (existing + "\n" + log_entry).strip()
    frappe.db.set_value("Account Update Request", docname, "approval_log", new_log)


def set_requested_by(doc, method):
    """Set requested_by and request_date for employee submitting"""
    if doc.is_new() and not doc.requested_by:
        doc.requested_by = frappe.session.user

    if not doc.request_date:
        doc.request_date = frappe.utils.today()

def send_notification_to_approver(doc, method=None):

    frappe.log_error("DEBUG: on_submit TRIGGERED", f"Doc Name: {doc.name}")

    subject = "Approval Required: Change to Chart of Accounts"

    message = f"""
        <p>Hello,</p>
        <p>A new <b>Account Update Request</b> requires your approval.</p>

        <p><b>Account Name:</b> {doc.account_name}<br>
        <b>Account Number:</b> {doc.account_number}<br>
        <b>Description:</b> {doc.description}<br>
        <b>Justification:</b> {doc.justification}</p>

        <p>You can review the request here:<br>
        <a href="{frappe.utils.get_url('/app/account-update-request/' + doc.name)}">
        Open Account Update Request
        </a></p>

        <p>Regards,<br>
        ERP System</p>
    """

    approvers = frappe.get_all(
        "Has Role",
        filters={"role": "System Manager"},
        fields=["parent"]
    )

    frappe.log_error("DEBUG: Approvers Raw List", str(approvers))

    emails = [x.parent for x in approvers]
    frappe.log_error("DEBUG: Emails Before Filter", str(emails))

    # Filter valid emails only
    emails = [e for e in emails if "@" in e]
    frappe.log_error("DEBUG: Emails After Filter", str(emails))

    # Send email
    if emails:
        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message,
            delayed=False
        )
        frappe.log_error("DEBUG: EMAIL SENT", str(emails))
    else:
        frappe.log_error("DEBUG: NO VALID EMAILS FOUND", "")
    
    # Send notification
    for user in emails:
        frappe.notify(
            title="Approval Required",
            message=f"Account Update Request {doc.name} submitted for approval.",
            user=user,
            document_type=doc.doctype,
            document_name=doc.name
        )
        frappe.log_error("DEBUG: NOTIFICATION SENT", user)





def before_save(doc, method):
    if doc.docstatus == 0:  # draft
        doc.status = "Pending Approval"

def before_submit(doc, method):
    doc.status = "Pending Approval"
    # send_account_update_email(doc, method)
    # send_notification_to_approver(doc)

# def on_submit(doc, method):
#     doc.status = "Pending Approval"
#     send_notification_to_approver(doc)

def send_account_update_email(doc, method):
    if not hasattr(doc, "default_email_template") or not doc.default_email_template:
        return

    template = frappe.get_doc("Email Template", doc.default_email_template)

    subject = frappe.render_template(template.subject, {"doc": doc})
    message = frappe.render_template(template.response, {"doc": doc})

    frappe.sendmail(
        recipients=[doc.requested_by],
        sender="arpit21092@gmail.com",
        subject=subject,
        message=message,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        email_account="Arpit Panchal"
    )
