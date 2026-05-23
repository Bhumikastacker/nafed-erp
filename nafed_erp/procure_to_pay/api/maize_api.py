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
# ---------------- LOT RECEIPT API ----------------
@frappe.whitelist(allow_guest=True)
def get_lot_receipts():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "dispatch_date")

        data = frappe.get_all(
            "Dispatch Receipt",
            fields=[
                "name",
                "dispatch_unique_id",
                "society_name",
                "district_name",
                "state_name",
                "status",
                "season",
                "commodity_name",
                "farmer_id",
                "lot_bags",
                "lot_qty"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Lot Receipt API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
# ---------------- QUALITY INSPECTION API ----------------
@frappe.whitelist(allow_guest=True)
def get_quality_inspection_details():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "report_date")

        data = frappe.get_all(
            "Quality Inspection",
            fields=[
                "name",
                "docstatus",
                "report_date",
                "inspection_type",
                "reference_type",
                "reference_name",
                "item_code"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Quality Inspection API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
    # ---------------- GOODS RECEIPT NOTES API ----------------
@frappe.whitelist(allow_guest=True)
def get_goods_receipt_notes():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "posting_date")

        data = frappe.get_all(
            "Purchase Receipt",
            fields=[
                "name",
                "docstatus",
                "title",
                "company",
                "posting_date",
                "grand_total",
                "per_returned"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Goods Receipt Notes API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
    # ---------------- PURCHASE INVOICE API ----------------
@frappe.whitelist(allow_guest=True)
def get_purchase_invoices():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "posting_date")

        data = frappe.get_all(
            "Purchase Invoice",
            fields=[
                "name",
                "title",
                "supplier",
                "company",
                "status",
                "posting_date",
                "division",
                "grand_total"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Purchase Invoice API Error"
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

        filters = get_date_filter(payload, "posting_date")

        data = frappe.get_all(
            "Payment Entry",
            fields=[
                "name",
                "party_name",
                "payment_type",
                "party_type",
                "party",
                "posting_date",
                "mode_of_payment",
                "reference_no",
                "status"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Payment Entry API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
    # ---------------- SALES ORDER API ----------------
@frappe.whitelist(allow_guest=True)
def get_sales_orders():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "transaction_date")

        data = frappe.get_all(
            "Sales Order",
            fields=[
                "name",
                "customer",
                "customer_name",
                "status",
                "delivery_date",
                "custom_ready_for_delivery",
                "grand_total",
                "per_delivered",
                "per_billed"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Sales Order API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
    # ---------------- DELIVERY NOTE API ----------------
@frappe.whitelist(allow_guest=True)
def get_delivery_notes():
    try:
        is_valid, error_response = validate_request()
        if not is_valid:
            return error_response

        request_data = frappe.request.get_json()
        payload = decrypt_payload(request_data.get("request"))

        filters = get_date_filter(payload, "posting_date")

        data = frappe.get_all(
            "Delivery Note",
            fields=[
                "name",
                "title",
                "status",
                "grand_total",
                "per_installed"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Delivery Note API Error"
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
        

        data = frappe.get_all(
            "Sales Invoice",
            fields=[
                "name",
                "docstatus",
                "grand_total",
                "title",
                "division"
            ],
            filters=filters,
            order_by="modified desc"
        )

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Success",
                "result": data
            })
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sales Invoice API Error")
        return {"status": "error", "message": str(e)}