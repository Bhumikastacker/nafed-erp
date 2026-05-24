import frappe
from frappe import _
from frappe.utils import flt

def validate(doc,method):
    validate_estimating_cost(doc)
    set_status_to_active(doc)
    validate_project_common_party(doc)
    validate_estimated_margin_cost_range(doc)

def validate_estimating_cost(doc):
    if doc.custom_technical_partner and not doc.estimated_costing:
        frappe.throw("Estimated Cost cannot be zero for a Technical Partner.")

def validate_estimated_margin_cost_range(doc):
    percent = doc.custom_estimated_margin_percent

    if not doc.custom_technical_partner: 
        return
    if percent is None:
        return  # or throw if field is mandatory

    if percent <= 0 or percent >= 100:
        frappe.throw(
            _("Margin Percent must be greater than 0 and less than 100.")
        )

def set_status_to_active(doc):
    if doc.workflow_state == "Approved":
        doc.percent_complete_method="Manual"


# ============================================================
# MAIN ENTRY
# ============================================================

@frappe.whitelist()
def create_project_purchase_invoice(source_name, target_doc=None):

    # Check if this name belongs to Task
    if frappe.db.exists("Task", source_name):
        return _create_from_task(source_name)

    # Else check if it is Project
    if frappe.db.exists("Project", source_name):
        return _create_from_project(source_name)

    frappe.throw(f"Invalid source document: {source_name}")


# ============================================================
# PROJECT BILLING
# ============================================================

def _create_from_project(project_name):

    project = frappe.get_doc("Project", project_name)

    return _make_purchase_invoice(project=project)


# ============================================================
# TASK (MILESTONE) BILLING
# ============================================================

def _create_from_task(task_name):

    task = frappe.get_doc("Task", task_name)

    project = frappe.get_doc("Project", task.project)

    return _make_purchase_invoice(
        project=project,
        task=task.name
    )


# ============================================================
# PURCHASE INVOICE CREATION
# ============================================================

def _make_purchase_invoice(project, task=None):

    doc = frappe.new_doc("Purchase Invoice")

    doc.supplier = project.custom_technical_partner
    doc.company = project.company
    doc.project = project.name
    doc.division = project.custom_division

    doc.append("items", {
        "rate": 0,
        "project": project.name,
        "custom_task": task
    })

    doc.run_method("set_missing_values")

    return doc


# ============================================================
# VALIDATION ON SAVE
# ============================================================

def validate_purchase_invoice(doc, method=None):

    if not doc.project:
        return

    project = frappe.get_doc("Project", doc.project)

    # -----------------------
    # Calculate new total
    # -----------------------
    current_total = flt(project.total_purchase_cost or 0)
    new_amount = flt(doc.base_grand_total or 0)

    total_after_save = current_total + new_amount

    if not project.custom_technical_partner: 
        return
    # -----------------------
    # Project Budget Validation (Hard Stop)
    # -----------------------
    if project.estimated_costing and total_after_save > flt(project.estimated_costing):

        exceeded_amount = total_after_save - flt(project.estimated_costing)

        frappe.throw(
            _("Project budget exceeded by {0}. You cannot proceed, raise the budget using project extension request.")
            .format(
                frappe.format_value(
                    exceeded_amount,
                    {"fieldtype": "Currency"}
                )
            )
        )

    # -----------------------
    # Milestone Validation
    # -----------------------
    for row in doc.items:
        if row.custom_task:

            task = frappe.get_doc("Task", row.custom_task)

            remaining = (
                flt(task.custom_estimated_cost or 0)
                - flt(task.custom_billed_amount or 0)
            )

            if flt(row.base_amount) > remaining:
                frappe.throw(
                    _("Milestone amount exceeds remaining budget for Task {0}.")
                    .format(task.name)
                )


# ============================================================
# SUBMIT HOOK
# ============================================================

def update_billing_on_submit(doc, method=None):

    total_added = 0

    for row in doc.items:

        if row.custom_task:

            task = frappe.get_doc("Task", row.custom_task)

            task.custom_billed_amount = (
                flt(task.custom_billed_amount) + flt(row.base_amount)
            )

            task.save(ignore_permissions=True)

        total_added += flt(row.base_amount)

    if doc.project:

        project = frappe.get_doc("Project", doc.project)

        project.total_purchase_cost = (
            flt(project.total_purchase_cost) + total_added
        )

        project.save(ignore_permissions=True)


# ============================================================
# CANCEL HOOK
# ============================================================

def revert_billing_on_cancel(doc, method=None):

    total_reduced = 0

    for row in doc.items:

        if row.custom_task:

            task = frappe.get_doc("Task", row.custom_task)

            task.custom_billed_amount = (
                flt(task.custom_billed_amount) - flt(row.base_amount)
            )

            task.save(ignore_permissions=True)

        total_reduced += flt(row.base_amount)

    if doc.project:

        project = frappe.get_doc("Project", doc.project)

        project.total_purchase_cost = (
            flt(project.total_purchase_cost) - total_reduced
        )

        project.save(ignore_permissions=True)


## Sales Invoice Creation from the Project
@frappe.whitelist()
def create_project_sales_invoice(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.customer = source.customer
        target.project = source.name
        target.custom_department= source.custom_division

    doc = get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "name": "project"
                }
            }
        },
        target_doc,
        set_missing_values
    )

    return doc

def validate_project_common_party(doc):
    if not doc.custom_technical_partner or not doc.customer:
        return

    party_link = frappe.db.exists(
        "Party Link",
        {
            "primary_party": doc.customer,
            "secondary_party": doc.custom_technical_partner,
        },
    )

    if not party_link:
        party_link = frappe.db.exists(
            "Party Link",
            {
                "primary_party": doc.custom_technical_partner,
                "secondary_party": doc.customer,
            },
        )

    if not party_link:
        frappe.throw("Customer and Supplier are not linked via Party Link.")