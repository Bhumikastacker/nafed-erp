import frappe

def update_payment_related_status(doc, method):

    for ref in doc.references:

        # ============================================
        # ✅ 1. PURCHASE INVOICE → DISPATCH RECEIPT
        # ============================================
        if ref.reference_doctype == "Purchase Invoice":

            purchase_invoice = ref.reference_name
            if not purchase_invoice:
                continue

            dispatch_name = frappe.db.get_value(
                "Purchase Invoice",
                purchase_invoice,
                "custom_whr_no"
            )

            if dispatch_name and frappe.db.exists("Dispatch Receipt", dispatch_name):

                current_status = frappe.db.get_value(
                    "Dispatch Receipt",
                    dispatch_name,
                    "status"
                )

                if current_status != "Payment Completed":
                    frappe.db.set_value(
                        "Dispatch Receipt",
                        dispatch_name,
                        "status",
                        "Payment Completed"
                    )

        # ============================================
        # ✅ 2. SALES INVOICE → JUTE WORK ORDER
        # ============================================
        elif ref.reference_doctype == "Sales Invoice":

            sales_invoice = ref.reference_name
            if not sales_invoice:
                continue

            jwo_name = frappe.db.get_value(
                "Sales Invoice",
                sales_invoice,
                "custom_jute_work_order"
            )

            if jwo_name and frappe.db.exists("Jute Work Order", jwo_name):

                jwo = frappe.get_doc("Jute Work Order", jwo_name)

                if jwo.status != "Invoice Paid":
                    jwo.db_set("status", "Invoice Paid")