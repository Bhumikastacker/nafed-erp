# import frappe
# import json
# from frappe.utils import getdate

# CALL_TYPE_MAPPING = {
#     "LOT_FETCH": "process_lot_row",
# }


# def get_records_from_log(log_id):
#     try:
#         log_doc = frappe.get_doc("E Samridhi Log", log_id)
#         response_data = log_doc.response

#         if not response_data:
#             return []

#         if isinstance(response_data, str):
#             response_data = json.loads(response_data)

#         data = response_data.get("data")

#         if not data:
#             return []

#         if isinstance(data, dict):
#             return data.get("records", [])

#         if isinstance(data, list):
#             return data

#         return []

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Error in get_records_from_log")
#         return []


# @frappe.whitelist()
# def process_log_dynamic(log_id):
#     try:
#         log_doc = frappe.get_doc("E Samridhi Log", log_id)
#         call_type = log_doc.call_type

#         records = get_records_from_log(log_id)

#         if not records:
#             return {"msg": "No records found"}

#         if call_type == "DISPATCH_FETCH":
#             inserted, skipped = process_dispatch_records(records)

#         elif call_type == "LOT_FETCH":

#             inserted, skipped = 0, 0

#             for row in records:
#                 try:
#                     result = process_lot_row(row)

#                     if result == "inserted":
#                         inserted += 1
#                     else:
#                         skipped += 1

#                 except Exception:
#                     frappe.log_error(frappe.get_traceback(), "Lot Processing Error")
#                     skipped += 1

#             frappe.db.commit()

#         else:
#             return {"msg": f"Unsupported Call Type: {call_type}"}

#         return {
#             "call_type": call_type,
#             "inserted": inserted,
#             "skipped": skipped,
#             "total": len(records)
#         }

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Dynamic Sync Error")
#         raise


# def process_lot_row(row):
#     try:
#         lot_id = row.get("lotId")
#         lot_date = row.get("lotCreatedDate")

#         if not lot_id or not lot_date:
#             return "skip"

#         if frappe.db.exists("Lot", {"esamridhi_lot_id": lot_id}):
#             return "skip"

#         doc = frappe.new_doc("Lot")

#         doc.esamridhi_lot_id = lot_id
#         doc.center = row.get("center")
#         doc.commodity = row.get("commodity")
#         doc.district = row.get("district")
#         doc.farmer_id = row.get("farmerId")
#         doc.lot_bags = row.get("lotBags")
#         doc.lot_create_date = getdate(lot_date)
#         doc.lot_qty = row.get("lotQty")
#         doc.season = row.get("season")
#         doc.society = row.get("society")
#         doc.state = row.get("state")
#         doc.state_agency = row.get("stateagency")
#         doc.transaction_id = row.get("transactionId")

#         doc.insert(ignore_permissions=True)

#         return "inserted"

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Lot Error")
#         return "skip"


# def process_dispatch_records(records):
#     try:
#         dispatch_map = {}

#         # 🔹 Step 1: Group by dispatchId
#         for row in records:
#             dispatch_id = row.get("dispatchId")

#             if not dispatch_id:
#                 continue

#             dispatch_map.setdefault(dispatch_id, []).append(row)

#         inserted, skipped = 0, 0

#         # 🔹 Step 2: Process each dispatch
#         for dispatch_id, rows in dispatch_map.items():

#             # Skip if already exists
#             if frappe.db.exists("Dispatch Receipt", {"dispatch_unique_id": dispatch_id}):
#                 skipped += 1
#                 continue

#             try:
#                 first_row = rows[0]

#                 doc = frappe.new_doc("Dispatch Receipt")

#                 # 🔹 Parent Fields
#                 doc.dispatch_unique_id = dispatch_id
#                 doc.dispatch_date = getdate(first_row.get("dispatchDate"))

#                 doc.procurement_center = first_row.get("center")
#                 doc.commodity_name = first_row.get("commodity")
#                 doc.delivery_chalan_number = first_row.get("deliveryChalanNo")

#                 doc.dispatch_quantity_in_qtls = first_row.get("dispatchQty")
#                 doc.dispatch_bags_count_in_number = first_row.get("dispatchBags")

#                 doc.district_name = first_row.get("district")
#                 doc.season = first_row.get("season")
#                 doc.society_name = first_row.get("society")

#                 doc.state_name = first_row.get("state")
#                 doc.state_agency_name = first_row.get("stateagency")

#                 doc.vehicle_number = first_row.get("vehicleNo")
#                 doc.warehouse = first_row.get("warehouse")

#                 doc.additional_remarks = f"Transaction ID: {first_row.get('transactionId')}"

#                 # 🔹 Child Table
#                 for row in rows:
#                     doc.append("lot_details", {
#                         "lot__id": row.get("lotId"),
#                         "created_date": getdate(row.get("lotCreatedDate")) if row.get("lotCreatedDate") else None,
#                         "farmer_unique_id": row.get("farmerId"),
#                         "farmer_name": row.get("farmerName"),
#                         "total_bags": row.get("lotBags"),
#                         "total_quantity_in_quital": row.get("lotQty"),
#                         "bill_number": row.get("billNumber"),
#                         "packaging_type": row.get("packagingType"),
#                         "quality_parameters_name": row.get("qualityParamName"),
#                         "quality_parameters_value": row.get("qualityParamValue"),
#                         "total_trade_amount_in_rs": row.get("tradeAmount")
#                     })

#                 # 🔹 Insert + Submit
#                 doc.insert(ignore_permissions=True)
#                 doc.flags.ignore_permissions = True
#                 doc.submit()

#                 inserted += 1

#             except Exception:
#                 frappe.log_error(
#                     frappe.get_traceback(),
#                     f"Dispatch Insert/Submit Error {dispatch_id}"
#                 )
#                 skipped += 1

#         frappe.db.commit()

#         return inserted, skipped

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Dispatch Processing Error")
#         return 0, len(records)


# def run_dynamic_sync():
#     try:
#         logs = frappe.get_all(
#             "E Samridhi Log",
#             filters={"call_type": ["in", ["LOT_FETCH", "DISPATCH_FETCH"]]},
#             fields=["name", "call_type"],
#             order_by="creation asc",
#             limit=50
#         )

#         for log in logs:
#             try:
#                 process_log_dynamic(log.name)
#             except Exception:
#                 frappe.log_error(frappe.get_traceback(), f"Log Error {log.name}")

#     except Exception:
#         frappe.log_error(fappe.get_traceback(), "Scheduler Error")
