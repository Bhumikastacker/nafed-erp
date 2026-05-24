import frappe
import requests
import re
from nafed_erp.utils.crypto import decrypt_payload, encrypt_payload
from nafed_erp.utils.security import validate_auth_token


# ---------------- COMMON AUTH FUNCTION ----------------
def validate_request():
    api_key = frappe.get_request_header("api-key")
    if api_key != frappe.conf.mobile_api_key:
        frappe.local.response["http_status_code"] = 401
        return False, {
            "response": encrypt_payload({
                "status": 401,
                "message": "Invalid API Key",
                "result": []
            })
        }

    auth_token = frappe.get_request_header("Auth-Token")
    if not auth_token:
        frappe.local.response["http_status_code"] = 401
        return False, {
            "response": encrypt_payload({
                "status": 401,
                "message": "Auth token missing",
                "result": []
            })
        }

    user = validate_auth_token()
    if not user:
        frappe.local.response["http_status_code"] = 401
        return False, {
            "response": encrypt_payload({
                "status": 401,
                "message": "Unauthorized",
                "result": None
            })
        }

    return True, None


# ---------------- COMMON DATE FILTER FUNCTION ----------------
def get_date_filter(payload, fieldname):
    filters = {}

    from_date = payload.get("from_date")
    to_date = payload.get("to_date")

    if from_date and to_date:
        filters[fieldname] = ["between", [from_date, to_date]]
    elif from_date:
        filters[fieldname] = [">=", from_date]
    elif to_date:
        filters[fieldname] = ["<=", to_date]

    return filters



# ---------------- INDENT API ----------------
@frappe.whitelist(allow_guest=True)
def get_indent_list():

    try:

        # Validate Request
        is_valid, error_response = validate_request()

        if not is_valid:
            return error_response

        # Get Request Payload
        request_data = frappe.request.get_json()

        payload = decrypt_payload(
            request_data.get("request")
        )

        # Date Filters
        filters = get_date_filter(
            payload,
            "request_date"
        )

        # Parent Data
        indent_list = frappe.get_all(
            "Indent",
            fields=[
                "name",
                "sla",
                "sla_name",
                "request_date",
                "kms_year",
                "state",
                "docstatus",
                "scheme",
                "request_no",
                "total_quantity",
                "total_price",
                "upload_document"
            ],
            filters=filters,
            order_by="modified desc"
        )

        final_data = []

        # Loop Through Each Indent
        for indent in indent_list:

            # ---------------- BAG TABLE ----------------
            bag_table = frappe.get_all(
                "Gunny Items Child",
                filters={
                    "parent": indent.name,
                    "parenttype": "Indent",
                    "parentfield": "bag_table"
                },
                fields=[
                    "gunny_bag_name",
                    "gunny_bag_weight",
                    "gunny_bag_uom",
                    "gunny_bag_capacity",
                    "gunny_bag_capacity_uom",
                    "unit_price"
                ]
            )

            # ---------------- LOCATION TABLE ----------------
            location_table = frappe.get_all(
                "Delivery Location Details",
                filters={
                    "parent": indent.name,
                    "parenttype": "Indent",
                    "parentfield": "location_table"
                },
                fields=[
                    "location_name",
                    "location_address",
                    "location_contact",
                    "gunny_bags_req",
                    "gunny_bags_delivered"
                ]
            )

            # Attach Child Tables
            indent["bag_table"] = bag_table

            indent["location_table"] = location_table

            final_data.append(indent)

        # Final Response
        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": final_data
            })
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Indent API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }

# ---------------- JUTE WORK ORDER API ----------------
@frappe.whitelist(allow_guest=True)
def get_jute_wo_details():

    try:

        # Validate Request
        is_valid, error_response = validate_request()

        if not is_valid:
            return error_response

        # Request Payload
        request_data = frappe.request.get_json()

        payload = decrypt_payload(
            request_data.get("request")
        )

        # Date Filter
        filters = get_date_filter(
            payload,
            "date_of_issue"
        )

        # Parent Data
        jwo_list = frappe.get_all(
            "Jute Work Order",
            fields=[
                "name",
                "docstatus",
                "indent_reference_no",
                "total_quantity",
                "total_price",
                "sla_id",
                "sla_name",
                "date_of_issue",
                "dispatch_by",
                "jute_miller",
                "status"
            ],
            filters=filters,
            order_by="modified desc"
        )

        final_data = []

        # Loop Through Each Work Order
        for jwo in jwo_list:

            # ---------------- GUNNY BAG CHILD TABLE ----------------
            gunny_bag_details_table = frappe.get_all(
                "Gunny Items Child",
                filters={
                    "parent": jwo.name,
                    "parenttype": "Jute Work Order",
                    "parentfield": "gunny_bag_details_table"
                },
                fields=[
                    "gunny_bag_name",
                    "gunny_bag_weight",
                    "gunny_bag_uom",
                    "gunny_bag_capacity",
                    "gunny_bag_capacity_uom",
                    "unit_price"
                ]
            )

            # ---------------- DELIVERY LOCATION CHILD TABLE ----------------
            delivery_location_table = frappe.get_all(
                "Delivery Location Details",
                filters={
                    "parent": jwo.name,
                    "parenttype": "Jute Work Order",
                    "parentfield": "delivery_location_table"
                },
                fields=[
                    "location_name",
                    "location_address",
                    "location_contact",
                    "gunny_bags_req",
                    "gunny_bags_delivered"
                ]
            )

            # Attach Child Tables
            jwo["gunny_bag_details_table"] = gunny_bag_details_table

            jwo["delivery_location_table"] = delivery_location_table

            final_data.append(jwo)

        # Final Response
        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": final_data
            })
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Jute WO API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }

# ---------------- DISPATCH DETAILS API ----------------
@frappe.whitelist(allow_guest=True)
def get_dispatch_details():

    try:

        # Validate Request
        is_valid, error_response = validate_request()

        if not is_valid:
            return error_response

        # Request Payload
        request_data = frappe.request.get_json()

        payload = decrypt_payload(
            request_data.get("request")
        )

        # Date Filter
        filters = get_date_filter(
            payload,
            "date_of_dispatch"
        )

        # Parent Data
        dispatch_list = frappe.get_all(
            "Dispatch Details",
            fields=[
                "name",
                "docstatus",
                "work_order_ref_no",
                "sla_id",
                "sla_name",
                "jute_miller",
                "date_of_issue",
                "date_of_dispatch",
                "quantity",
                "total_quantity_delivered",
                "total_amount",
                "upload_documents",
                "inspection_report",
                "bill",
                "transport_challan",
                "loading_supervision_report",
                "tax_invoice",
                "insurance_copy",
                "remarks"
            ],
            filters=filters,
            order_by="modified desc"
        )

        final_data = []

        # Loop Through Each Dispatch
        for dispatch in dispatch_list:

            # ---------------- ITEM DETAILS CHILD TABLE ----------------
            item_details = frappe.get_all(
                "Gunny Items Child",
                filters={
                    "parent": dispatch.name,
                    "parenttype": "Dispatch Details",
                    "parentfield": "item_details"
                },
                fields=[
                    "gunny_bag_name",
                    "gunny_bag_weight",
                    "gunny_bag_uom",
                    "gunny_bag_capacity",
                    "gunny_bag_capacity_uom",
                    "unit_price"
                ]
            )

            # ---------------- DELIVERY DETAILS CHILD TABLE ----------------
            delivery_details = frappe.get_all(
                "Delivery Location Details",
                filters={
                    "parent": dispatch.name,
                    "parenttype": "Dispatch Details",
                    "parentfield": "delivery_details"
                },
                fields=[
                    "location_name",
                    "location_address",
                    "location_contact",
                    "gunny_bags_req",
                    "gunny_bags_delivered"
                ]
            )

            # Attach Child Tables
            dispatch["item_details"] = item_details

            dispatch["delivery_details"] = delivery_details

            final_data.append(dispatch)

        # Final Response
        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": final_data
            })
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Dispatch API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }

# ---------------- SALES INVOICE API ----------------
@frappe.whitelist(allow_guest=True)
def get_si_details():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "posting_date")
        filters["division"] = "jute"

        invoices = frappe.get_all(
            "Sales Invoice",
            fields=[
                "name",
                "docstatus",
                "grand_total",
                "title",
                "division",
                "custom_upload_eivoice_copy"
            ],
            filters=filters,
            order_by="modified desc"
        )

        for invoice in invoices:

            # Child table items
            items = frappe.get_all(
                "Sales Invoice Item",
                fields=[
                    "item_code",
                    "item_name",
                    "qty",
                    "rate",
                    "amount"
                ],
                filters={
                    "parent": invoice["name"]
                }
            )

            invoice["items"] = items

            # Download URL for E-Invoice copy
            if invoice.get("custom_upload_eivoice_copy"):
                invoice["e_invoice_download_url"] = (
                    frappe.utils.get_url() +
                    invoice["custom_upload_eivoice_copy"]
                )
            else:
                invoice["e_invoice_download_url"] = ""

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": invoices
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Sales Invoice API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


# ---------------- PAYMENT ENTRY API ----------------
@frappe.whitelist(allow_guest=True)
def get_payment_entries():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        from_date = payload.get("from_date")
        to_date = payload.get("to_date")

        date_condition = ""
        values = {}

        if from_date and to_date:
            date_condition = "AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
            values.update({"from_date": from_date, "to_date": to_date})
        elif from_date:
            date_condition = "AND pe.posting_date >= %(from_date)s"
            values.update({"from_date": from_date})
        elif to_date:
            date_condition = "AND pe.posting_date <= %(to_date)s"
            values.update({"to_date": to_date})

        data = frappe.db.sql(f"""
            SELECT DISTINCT
                pe.name,
                pe.posting_date,
                pe.paid_amount,
                pe.received_amount,
                pe.party,
                pe.mode_of_payment
            FROM `tabPayment Entry` pe
            INNER JOIN `tabPayment Entry Reference` per
                ON per.parent = pe.name
            INNER JOIN `tabSales Invoice` si
                ON si.name = per.reference_name
            WHERE
                per.reference_doctype = 'Sales Invoice'
                AND si.division = 'jute'
                {date_condition}
            ORDER BY pe.modified DESC
        """, values, as_dict=True)

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payment Entry API Error")
        return {"status": "error", "message": str(e)}