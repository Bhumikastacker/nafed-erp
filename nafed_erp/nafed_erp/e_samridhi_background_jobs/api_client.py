import frappe
import requests
import jwt
import time
from datetime import datetime, timedelta
from frappe.utils import nowdate, now_datetime


# -------------------------
# Utility: Log API Calls
# -------------------------
def log_api(call_type, response=None, request=None):
    try:
        doc = frappe.new_doc("E Samridhi Log")
        doc.call_type = call_type
        doc.response = frappe.as_json(response) if response else None
        doc.request = frappe.as_json(request) if request else None
        doc.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "E Samridhi Log Error")


# -------------------------
# Get Settings
# -------------------------
def get_settings():
    return frappe.get_single("Nafed Global Defaults")


# -------------------------
# Get Base URL
# -------------------------
def get_base_url():
    settings = get_settings()

    if not settings.e_samridhi_domain:
        raise Exception("E Samridhi Domain not configured in Nafed Global Defaults")

    return settings.e_samridhi_domain.rstrip("/")


# -------------------------
# JWT Expiry Check
# -------------------------
def is_jwt_expired(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")

        if not exp:
            return True

        return time.time() > exp - 120

    except Exception:
        return True


# -------------------------
# Login API
# -------------------------
def login():

    settings = get_settings()
    base_url = get_base_url()

    url = f"{base_url}/api/v1/esamridhi/auth/login"

    payload = {
        "username": settings.username_esamridhi,
        "password": settings.get_password("password_esamrishi")
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "E Samridhi Login Request Failed")
        raise

    if response.status_code != 200:
        log_api(
            "LOGIN_FAILED",
            response={"status_code": response.status_code, "response_text": response.text},
            request=payload
        )
        raise Exception(f"E Samridhi Login Failed. Status: {response.status_code}")

    data = response.json()

    log_api("LOGIN_SUCCESS", response=data, request=payload)

    if "jwtToken" in data:
        settings.jwt_token_esamridhi = data["jwtToken"]
        settings.save(ignore_permissions=True)
        return data["jwtToken"]

    raise Exception("E Samridhi Login Failed: jwtToken not found")


# -------------------------
# Get Valid JWT
# -------------------------
def get_valid_token():

    settings = get_settings()
    token = settings.jwt_token_esamridhi

    if not token or is_jwt_expired(token):
        token = login()

    return token


# -------------------------
# Resolve Date Range
# -------------------------
def resolve_date_range(api_name):

    settings = get_settings()
    sync_mode = settings.sync_mode

    today = nowdate()

    # FULL SYNC
    if sync_mode == "FULL":
        return "2000-01-01", today

    # CUSTOM DATE
    elif sync_mode == "CUSTOM":

        if not settings.custom_fetch_from_date:
            raise Exception("Custom Fetch From Date is required in CUSTOM mode")

        from_date = str(settings.custom_fetch_from_date)

        return from_date, today

    # INCREMENTAL
    elif sync_mode == "INCREMENTAL":

        field_map = {
            "FARMER_FETCH": "last_farmer_sync",
            "CROP_FETCH": "last_crop_sync",
            "LOT_FETCH": "last_lot_custom_fetch",
            "DISPATCH_FETCH": "last_lot_dispatch",
            "WHR_FETCH": "last_purchase_receipt_fetch",
            "PAYMENT_FETCH": "last_payment_entry_fetch"
        }

        last_sync_field = field_map.get(api_name)

        if not last_sync_field:
            raise Exception(f"No last sync field mapped for {api_name}")

        last_sync_value = getattr(settings, last_sync_field)

        if not last_sync_value:
            from_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            from_date = last_sync_value.strftime("%Y-%m-%d")

        return from_date, today

    else:
        raise Exception("Invalid Sync Mode")


# -------------------------
# Generic GET Caller
# -------------------------
def fetch_with_pagination(api_name, endpoint, api_type):

    base_url = get_base_url()
    token = get_valid_token()

    headers = {"Authorization": f"Bearer {token}"}

    page = 1
    page_size = 200

    all_records = []
    transaction_ids = []

    from_date, to_date = resolve_date_range(api_name)

    while True:

        params = {
            "pageNo": page,
            "pageSize": page_size,
            "fromDate": from_date,
            "toDate": to_date
        }

        url = f"{base_url}{endpoint}"

        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"{api_name} Request Failed")
            break

        log_api(
            f"{api_name}_STATUS",
            response={"status_code": response.status_code, "page": page},
            request=params
        )

        # Token expired
        if response.status_code == 401:
            token = login()
            headers["Authorization"] = f"Bearer {token}"

            response = requests.get(url, headers=headers, params=params, timeout=60)

        if response.status_code != 200:
            log_api(
                f"{api_name}_FAILED",
                response={"status_code": response.status_code, "response_text": response.text},
                request=params
            )
            break

        data = response.json()

        log_api(api_name, response=data, request=params)

        data_block = data.get("data")

        if not data_block:
            break

        records = data_block.get("records", [])

        if not records:
            break

        for r in records:
            all_records.append(r)

            if r.get("transactionId"):
                transaction_ids.append(r.get("transactionId"))

        page += 1

        if page > 500:
            frappe.logger().warning("Pagination safety breaker triggered.")
            break

    # -------------------------
    # Update last sync
    # -------------------------

    settings = get_settings()

    if settings.sync_mode == "INCREMENTAL" and all_records:

        field_map = {
            "FARMER_FETCH": "last_farmer_sync",
            "CROP_FETCH": "last_crop_sync",
            "LOT_FETCH": "last_lot_custom_fetch",
            "DISPATCH_FETCH": "last_lot_dispatch",
            "WHR_FETCH": "last_purchase_receipt_fetch",
            "PAYMENT_FETCH": "last_payment_entry_fetch"
        }

        last_sync_field = field_map.get(api_name)

        if last_sync_field:
            setattr(settings, last_sync_field, now_datetime())
            settings.save(ignore_permissions=True)

    return all_records, transaction_ids


# -------------------------
# ACK API
# -------------------------
def send_ack(api_type, transaction_ids):

    if not transaction_ids:
        return

    base_url = get_base_url()
    token = get_valid_token()

    headers = {"Authorization": f"Bearer {token}"}

    url = f"{base_url}/api/v1/nafed-esamridhi/acknowledgment"

    payload = {
        "apiType": api_type,
        "transactionIds": transaction_ids
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ACK Request Failed")
        return

    if response.status_code != 200:
        log_api(
            f"ACK_{api_type}_FAILED",
            response={"status_code": response.status_code, "response_text": response.text},
            request=payload
        )
        return

    data = response.json()

    log_api(
        f"ACK_{api_type}_SUCCESS",
        response=data,
        request=payload
    )

def create_lot_in_dispatch_receipt(records):

    for r in records:

        try:
            # -------------------------------
            # ✅ FILTER: Only MAIZE allowed
            # -------------------------------
            if (r.get("commodity") or "").strip().upper() != "MAIZE":
                continue

            # -------------------------------
            # Unique ID
            # -------------------------------
            lot_id = r.get("lotId")

            if not lot_id:
                continue

            # Avoid duplicate
            if frappe.db.exists("Dispatch Receipt", {"dispatch_unique_id": lot_id}):
                continue

            doc = frappe.new_doc("Dispatch Receipt")

            # -------------------------------
            # FIELD MAPPING (FIXED 🔥)
            # -------------------------------
            doc.dispatch_unique_id = lot_id

            # ⚠️ IMPORTANT FIX (API field name wrong tha)
            doc.dispatch_date = r.get("lotCreatedDate")

            doc.procurement_center = r.get("center")
            doc.state_name = r.get("state")
            doc.district_name = r.get("district")
            doc.society_name = r.get("society")

            doc.season = r.get("season")
            doc.commodity_name = r.get("commodity")

            doc.farmer_id = r.get("farmerId")
            doc.farmer_name = r.get("farmerName")

            # ⚠️ FIX: correct field names from API
            doc.lot_bags = r.get("lotBags")
            doc.lot_qty = r.get("lotQty")

            doc.trade_value = r.get("tradeValue")
            doc.bill_no = r.get("billNo")
            doc.packtype = r.get("packType")

            doc.assaying_parameters_type = r.get("assayingParametersType")
            doc.assaying_parameters_value = r.get("assayingParametersValue")

            doc.transaction_id = r.get("transactionId")

            # -------------------------------
            # SAVE
            # -------------------------------
            doc.insert(ignore_permissions=True)

            frappe.db.commit()

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"LOT Creation Failed: {r.get('lotId')}"
            )

def create_farmer_registration(records):

    for r in records:

        try:
            # -------------------------------
            # DEBUG LOG
            # -------------------------------
            frappe.logger().info(f"Farmer Record: {r}")

            farmer_id = r.get("farmerId")

            # -------------------------------
            # Duplicate Check
            # -------------------------------
            if not farmer_id:
                continue

            if frappe.db.exists("Farmer Registation", {"farmer_id": farmer_id}):
                continue

            doc = frappe.new_doc("Farmer Registation")

            # -------------------------------
            # Gender Mapping (FIXED 🔥)
            # -------------------------------
            gender_map = {
                "M": "Male",
                "F": "Female",
                "O": "Other"
            }

            gender = r.get("gender")
            gender = gender_map.get(gender, gender)

            # fallback if invalid
            if not frappe.db.exists("Gender", gender):
                gender = "Male"

            # -------------------------------
            # SAFE LINK FETCH FUNCTION 🔥
            # -------------------------------
            def get_valid_link(doctype, value, default=None):
                if value and frappe.db.exists(doctype, value):
                    return value
                return default

            # -------------------------------
            # Mandatory Fields
            # -------------------------------
            doc.farmer_id = farmer_id
            doc.farmer_name = r.get("farmerName") or "Unknown"
            doc.gender = gender
            doc.source = "E-samridhi"
            doc.registration_date = r.get("registrationDate") or nowdate()

            # -------------------------------
            # SAFE LINK FIELDS 🔥
            # -------------------------------
            # # doc.registered_by_society = get_valid_link(
            #     # "Society",
            #     # r.get("society"),
            #     # "Default Society"
            # )

            # # doc.society = get_valid_link(
            # #     "Society",
            # #     r.get("society")
            # # )

            doc.state = get_valid_link(
                "State",
                r.get("state")
            )

            doc.district = get_valid_link(
                "District",
                r.get("district")
            )

            # -------------------------------
            # Optional Fields
            # -------------------------------
            doc.father_spouse_name = r.get("fatherName")
            doc.class_category = r.get("classCategory")
            doc.farmer_category = r.get("farmerCategory")

            doc.mobile_no = r.get("mobileNo")
            doc.email_id = r.get("email")

            doc.date_of_birth = r.get("dob")

            doc.address = r.get("address")
            doc.taluka = r.get("taluka")
            doc.village = r.get("village")
            doc.pin_code = r.get("pincode")

            doc.account = r.get("bankAccount")

            doc.procurement_eligibility_flag = r.get("isEligible") or 0

            # -------------------------------
            # INSERT
            # -------------------------------
            doc.insert(ignore_permissions=True)

            # commit per record (safe but optional)
            frappe.db.commit()

        except Exception:
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"Farmer Failed: {r.get('farmerId')}"
            )

            print("ERROR:", frappe.get_traceback())
# -------------------------
# Warehouse Receipt Creation
# -------------------------
def create_warehouse_receipt(records):
    """
    WHR_FETCH → Parent Warehouse Receipt

    Also fetch:
    DISPATCH_FETCH → lot_dispatch_details
    LOT_FETCH → lot_details
    """

    for r in records:
        try:
            whr_no = r.get("whrNo")

            if not whr_no:
                continue

            # Avoid duplicate
            if frappe.db.exists("Warehouse Receipt", {"whr_number": whr_no}):
                continue

            doc = frappe.new_doc("Warehouse Receipt")

            # =====================================================
            # Parent Field Mapping (WHR_FETCH)
            # =====================================================

            doc.whr_number = whr_no
            doc.whr_created_date = r.get("whrDate")

            doc.scheme = None  # if scheme available later
            doc.season = r.get("seasonId")
            doc.commodity_name = r.get("commodity")
            doc.warehouse_name = r.get("warehouse")

            doc.total_dispatch_quantity_in_qtls = r.get("totalDispatchQty")
            doc.total_accepted_quantity_in_qtls = r.get("totalAcceptedQty")
            doc.quantity_loss_in_qtls = r.get("quantityLoss")
            doc.quantity_gain_in_qtls = r.get("quantityGain")
            doc.whr_total_value_in_rs = r.get("whrValue")

            doc.state_agency_name = r.get("stateagency")
            doc.society_name = r.get("society")
            doc.state_name = r.get("state")
            doc.district_name = r.get("district")
            doc.procurement_center = r.get("center")

            doc.total_dispatch_bags_in_number = r.get("totalDispatchBags")
            doc.total_accepted_bags_in_number = r.get("totalAcceptedBags")

            doc.additional_remarks = r.get("remark")

            dispatched_ids = r.get("dispatchedIds")

            # =====================================================
            # Fetch DISPATCH_FETCH data
            # =====================================================

            if dispatched_ids:
                dispatch_records, _ = fetch_with_pagination(
                    "DISPATCH_FETCH",
                    "/api/v1/nafed-esamridhi/dispatches",
                    "DISPATCH_DETAILS"
                )

                for d in dispatch_records:
                    if d.get("dispatchId") != dispatched_ids:
                        continue

                    child = doc.append("lot_dispatch_details", {})

                    child.dispatchid = d.get("dispatchId")
                    child.vehicle_number = d.get("vehicleNo")
                    child.delivery_chalan_number = d.get("deliveryChalanNo")
                    child.dispatch_quantity_in_qtls = d.get("dispatchQty")
                    child.dispatch_bags_count_in_number = d.get("dispatchBags")
                    child.farmer_unique_id = d.get("farmerId")
                    child.dispatch_date = d.get("dispatchDate")

                    lot_id = d.get("lotId")

                    # =====================================================
                    # Fetch LOT_FETCH data
                    # =====================================================

                    if lot_id:
                        lot_records, _ = fetch_with_pagination(
                            "LOT_FETCH",
                            "/api/v1/nafed-esamridhi/lots",
                            "PROCUREMENT_DETAILS"
                        )

                        for l in lot_records:
                            if l.get("lotId") != lot_id:
                                continue

                            lot_child = doc.append("lot_details", {})

                            lot_child.lot__id = l.get("lotId")
                            lot_child.created_date = l.get("lotCreatedDate")
                            lot_child.farmer_unique_id = l.get("farmerId")
                            lot_child.farmer_name = l.get("farmerName")
                            lot_child.total_bags = l.get("lotBags")
                            lot_child.total_quantity_in_quital = l.get("lotQty")
                            lot_child.remark = l.get("remark")
                            lot_child.bill_number = l.get("billNo")
                            lot_child.packaging_type = l.get("packType")

                            lot_child.quality_parameters_name = l.get(
                                "assayingParametersType"
                            )

                            lot_child.moisture = l.get("moisture")
                            lot_child.foreign_matter = l.get("foreignMatter")
                            lot_child.broken_grains = l.get("brokenGrains")

                            lot_child.quality_parameters_value = l.get(
                                "assayingParametersValue"
                            )

                            lot_child.total_trade_amount_in_rs = l.get("tradeValue")
                            lot_child.admixture = l.get("admixture")

                            break

            # =====================================================
            # Save
            # =====================================================

            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Warehouse Receipt Creation Failed: {r.get('whrNo')}"
            )