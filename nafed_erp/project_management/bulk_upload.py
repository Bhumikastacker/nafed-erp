import frappe
from frappe import _
from frappe.utils import getdate
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file

@frappe.whitelist()
def bulk_upload_project_milestones(file_url):
    frappe.log_error("BULK UPLOAD METHOD HIT", "DEBUG BULK UPLOAD")

    if not file_url:
        frappe.throw(_("File is required"))

    rows = read_xlsx_file_from_attached_file(file_url)

    created = []

    for idx, row in enumerate(rows[1:], start=2):
        try:
            project_id = row[0]
            milestone_name = row[1]
            start_date = row[2]
            end_date = row[3]
            description = row[4]
            budget_allocated = row[5]
            responsible_person_id = row[6]
            status = row[7]

            doc = frappe.get_doc({
                "doctype": "Project Milestone",
                "project_id": project_id,
                "milestone_name": milestone_name,
                "planned_start_date": getdate(start_date),
                "planned_end_date": getdate(end_date),
                "description": description,
                "budget_allocated": budget_allocated,
                "responsible_person_id": responsible_person_id,
                "status": status,
            })

            doc.insert(ignore_permissions=True)
            created.append(doc.name)

        except Exception as e:
            frappe.throw(
                _("Error in row {0}: {1}").format(idx, str(e))
            )

    return {
        "count": len(created),
        "names": created
    }
