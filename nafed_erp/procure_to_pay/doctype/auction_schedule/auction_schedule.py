# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import flt


class AuctionSchedule(Document):
    pass
import frappe
from frappe.model.document import Document
import json
from frappe.utils import flt


class AuctionSchedule(Document):
    pass


@frappe.whitelist()
def create_auctions(doc):

    # string -> dict
    if isinstance(doc, str):
        doc = json.loads(doc)

    # -----------------------------------
    # IMPORTANT
    # Save document first if unsaved
    # -----------------------------------

    auction_schedule_name = doc.get("name")

    if not auction_schedule_name or auction_schedule_name.startswith("new-"):
        frappe.throw("Please save the Auction Schedule first before creating Auctions")

    frappe.log_error(
        title="Auction Schedule DATA",
        message=str({
            "auction_schedule": auction_schedule_name,
            "rows": len(doc.get("auction_details_view", []))
        })
    )

    # ONLY use auction_details_view
    auction_details = doc.get("auction_details_view") or []

    if not auction_details:
        frappe.throw("No rows found in auction_details_view")

    created_auctions = []

    for row in auction_details:

        try:

            qty = flt(row.get("quantity_to_put_on_auction") or 0)

            # Skip zero qty rows
            if qty <= 0:
                continue

            warehouse_code = row.get("warehouse_code")

            # -----------------------------------
            # Duplicate Check
            # -----------------------------------

            already_exists = frappe.db.exists(
                "Auction",
                {
                    "auction_schedule_id": auction_schedule_name,
                    "warehouse_code": warehouse_code
                }
            )

            if already_exists:

                frappe.log_error(
                    title="Auction Duplicate Skipped",
                    message=f"""
                    Auction already exists

                    Auction Schedule: {auction_schedule_name}
                    Warehouse: {warehouse_code}
                    Existing Auction: {already_exists}
                    """
                )

                continue

            # -----------------------------------
            # Create Auction
            # -----------------------------------

            auction = frappe.get_doc({
                "doctype": "Auction",

                # LINK FIELD
                "auction_schedule_id": auction_schedule_name,

                # Parent fields
                "date_time": doc.get("date"),
                "start_time_price_discovery_round":
                    doc.get("start_time_price_discovery_round"),

                "branch": doc.get("branch"),
                "reserve_price": doc.get("reserve_price"),

                "total_warehouse_added":
                    doc.get("total_warehouse_added"),

                "total_warehouse_need_to_be_submitted":
                    doc.get("total_warehouse_need_to_be_submitted"),

                "total_auction_quantity_added":
                    doc.get("total_auction_quantity_added"),

                "total_auction_quantity_need_to_be_submitted":
                    doc.get("total_auction_quantity_need_to_be_submitted"),

                # Row fields
                "state": row.get("state"),
                "commodity": row.get("commodity"),
                "season": row.get("season"),
                "scheme": row.get("scheme"),

                "warehouse_code": warehouse_code,
                "warehouse_name": row.get("warehouse_name"),

                "uom": row.get("uom"),

                "quantity_for_auction": qty
            })

            auction.insert(ignore_permissions=True)

            auction.submit()

            created_auctions.append(auction.name)

            frappe.log_error(
                title="Auction Created",
                message=f"""
                Auction: {auction.name}
                Auction Schedule: {auction_schedule_name}
                Warehouse: {warehouse_code}
                Qty: {qty}
                """
            )

        except Exception:

            frappe.log_error(
                title="Auction Creation Failed",
                message=frappe.get_traceback()
            )

            raise

    return {
        "success": True,
        "created_auctions": created_auctions
    }
@frappe.whitelist()
def get_items_from_season_scheme(season=None, scheme=None, warehouse_code=None, commodity=None):

    filters = {}

    if season:
        filters["custom_season"] = season

    if scheme:
        filters["custom_scheme"] = scheme

    if commodity:
        filters["name"] = commodity

    if not filters:
        return []

    items = frappe.get_all(
        "Item",
        filters=filters,
        fields=["name", "custom_season", "custom_scheme", "stock_uom"]
    )

    result = []

    for item in items:

        bin_filters = {"item_code": item.name}

        if warehouse_code:
            bin_filters["warehouse"] = warehouse_code

        bins = frappe.get_all(
            "Bin",
            filters=bin_filters,
            fields=["warehouse", "actual_qty", "stock_uom"]
        )
        
        if not bins:
            continue

        for bin_row in bins:

            warehouse_name = bin_row.warehouse or ""
            state = ""

            if warehouse_name:
                warehouse_doc = frappe.db.get_value(
                    "Warehouse",
                    warehouse_name,
                    ["warehouse_name", "company"],
                    as_dict=True
                )

                if warehouse_doc and warehouse_doc.company:
                    state = frappe.db.get_value(
                        "Company",
                        warehouse_doc.company,
                        "custom_state_"
                    ) or ""

            result.append({
                "state": state,
                "commodity": item.name,
                "season": item.custom_season,
                "scheme": item.custom_scheme,
                "qty": bin_row.actual_qty or 0,
                "warehouse_code": warehouse_name,
                "warehouse_name": warehouse_name,
                "uom": bin_row.stock_uom or item.stock_uom
            })

    if not result:
        frappe.msgprint("No matching stock found for selected combination")

    return result
