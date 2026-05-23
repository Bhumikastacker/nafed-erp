import frappe
from frappe.utils import get_url
from frappe.utils.background_jobs import enqueue

def validate_suppliers(doc, method):

    # 🔹 Check if division is set
    if not doc.custom_division:
        return

    # 🔹 Fetch division document
    division = frappe.get_doc("Division", doc.custom_division)

    # 🔹 Run validation ONLY if is_rbd is checked
    if not division.is_rbd:
        return

    # 🔹 Your existing logic
    for item in doc.items:
        allowed_suppliers = frappe.get_all(
            "Item Supplier",
            filters={"parent": item.item_code},
            pluck="supplier"
        )

        for supplier in doc.suppliers:
            if supplier.supplier not in allowed_suppliers:
                frappe.throw(
                    f"Supplier <b>{supplier.supplier}</b> is not allowed for the mentioned items."
                )

def on_submit_send_web_form(doc, method):
    if not doc.suppliers:
        return

    # 🔹 Check if division is set
    if not doc.custom_division:
        return

    # 🔹 Fetch division document
    division = frappe.get_doc("Division", doc.custom_division)

    # 🔹 Run validation ONLY if is_rbd is checked
    if not division.is_rbd:
        return

    enqueue(
        "nafed_erp.procure_to_pay.doc_events.request_for_quotation.send_rfq_emails",
        queue="long",
        timeout=500,
        doc=doc
    )

def send_rfq_emails(doc):
    # If doc is passed as dict (sometimes happens), reload it
    if isinstance(doc, dict):
        doc = frappe.get_doc("Request for Quotation", doc.get("name"))

    for row in doc.suppliers:
        if not row.email_id:
            continue

        webform_link = get_url(
            f"/supplier-quotation/new?rfq={doc.name}&supplier={row.supplier}"
        )

        subject = f"Request for Quotation: {doc.name}"

        message = f"""
        Dear {row.supplier_name or row.supplier},<br><br>

        You are requested to submit your quotation for RFQ <b>{doc.name}</b>.<br><br>

        Please use the link below:<br>
        <a href="{webform_link}">{webform_link}</a><br><br>

        Regards,<br>
        {doc.company}
        """

        frappe.sendmail(
            recipients=[row.email_id],
            subject=subject,
            message=message,
            delayed=False
        )

@frappe.whitelist(allow_guest=True)
def get_rfq_data(rfq, supplier=None):
    rfq_doc = frappe.get_doc("Request for Quotation", rfq)

    data = {
        "company_name": rfq_doc.company,
        "items": [],
        "supplier_name": None
    }

    # 🔹 Items
    for d in rfq_doc.items:
        data["items"].append({
            "item_code": d.item_code,
            "item_name": d.item_name,
            "description": d.description,
            "qty": d.qty,
            "uom": d.uom
        })

    # 🔹 Supplier Name
    if supplier:
        supplier_name = frappe.db.get_value(
            "Supplier", supplier, "supplier_name"
        )
        data["supplier_name"] = supplier_name
    print("//////////////////////////////////////////",data)
    return data

def validate_unique_supplier_emails(doc, method):

    # 🔹 Check if division is set
    if not doc.custom_division:
        return

    # 🔹 Fetch division document
    division = frappe.get_doc("Division", doc.custom_division)

    # 🔹 Run validation ONLY if is_rbd is checked
    if not division.is_rbd:
        return
    
    seen_emails = set()
    duplicates = set()

    for row in doc.suppliers:
        if row.email_id:
            email = row.email_id.strip().lower()

            if email in seen_emails:
                duplicates.add(row.email_id)
            else:
                seen_emails.add(email)

    if duplicates:
        frappe.throw(
            "Duplicate Email IDs found in Suppliers table: {}".format(
                ", ".join(duplicates)
            )
        )

@frappe.whitelist()
def get_item_by_barcode(barcode):

    result = frappe.get_all(
        "Item Barcode",
        filters={"barcode": barcode},
        fields=["parent", "custom_mrp"],
        limit=1
    )

    # ❌ Barcode not found
    if not result:
        return {}

    item_code = result[0].parent
    mrp = result[0].custom_mrp or 0

    # ✅ Always return item_code
    return {
        "item_code": item_code,
        "rate": mrp   # 0 if not available
    }