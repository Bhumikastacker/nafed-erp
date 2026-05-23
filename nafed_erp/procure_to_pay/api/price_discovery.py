import frappe
import jwt
from nafed_erp.procure_to_pay.api.get_token import get_secret
from frappe.utils import (now_datetime, get_time, flt)
from frappe.utils.data import get_datetime, add_to_date
from datetime import datetime


def validate_token():
    auth_header = frappe.get_request_header("Authorization")

    if not auth_header or "Bearer" not in auth_header:
        frappe.throw("Unauthorized", frappe.AuthenticationError)

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        frappe.throw("Invalid Authorization Header", frappe.AuthenticationError)

    try:
        payload = jwt.decode(
            token,
            get_secret(),
            algorithms=["HS256"]
        )

        user = payload.get("sub")

        if not user:
            frappe.throw("Invalid Token Payload", frappe.AuthenticationError)

        return user

    except jwt.ExpiredSignatureError:
        frappe.throw("Token Expired", frappe.AuthenticationError)

    except jwt.InvalidTokenError:
        frappe.throw("Invalid Token", frappe.AuthenticationError)




@frappe.whitelist(allow_guest=True)
def create_or_update_price_discovery():

    try:

        # ================= Validate Token =================
        user = validate_token()

        if not user:
            frappe.throw("Invalid Token")

        frappe.set_user(user)

        # ================= Get Request Data =================
        data = frappe.request.get_json()

        if not data:
            return {
                "status": "error",
                "message": "No data provided"
            }

        auction_id = data.get("auction_id")

        if not auction_id:
            return {
                "status": "error",
                "message": "auction_id is required"
            }

        # ================= Get Auction Details =================
        auction_doc = frappe.get_doc(
            "Auction",
            auction_id
        )

        auction_qty = float(
            auction_doc.quantity_for_auction or 0
        )

        # ================= Validate Auction Time =================

        # Current System Time
        current_time = frappe.utils.now_datetime().time()

        # Auction Start & End Time
        start_time = auction_doc.start_time_price_discovery_round
        end_time = auction_doc.end_time_price_discovery_round

        if not start_time or not end_time:
            frappe.throw(
                "Price Discovery Round timings are not set in Auction"
            )

        # Convert timedelta -> time
        start_time = (
            datetime.min + start_time
        ).time()

        end_time = (
            datetime.min + end_time
        ).time()

        # Validate Current Time
        if (
            current_time < start_time
            or current_time > end_time
        ):
            frappe.throw(
                f"Bids are allowed only between "
                f"{start_time} and {end_time}"
            )

        # ================= Validate Quantities =================
        total_bid_qty = 0
        total_winning_qty = 0

        for row in data.get(
            "price_discovery_table",
            []
        ):

            bid_qty = float(
                row.get("bid_quantity") or 0
            )

            winning_qty = float(
                row.get("winning_quantity") or 0
            )

            # ================= Validate bid_quantity =================
            if bid_qty > auction_qty:
                frappe.throw(
                    f"Bid Quantity ({bid_qty}) cannot exceed "
                    f"Quantity for Auction ({auction_qty})"
                )

            # ================= Validate winning_quantity =================
            if winning_qty > auction_qty:
                frappe.throw(
                    f"Winning Quantity ({winning_qty}) cannot exceed "
                    f"Quantity for Auction ({auction_qty})"
                )

            total_bid_qty += bid_qty
            total_winning_qty += winning_qty

        # ================= Total Bid Quantity Validation =================
        # if total_bid_qty > auction_qty:
        #     frappe.throw(
        #         f"Total Bid Quantity ({total_bid_qty}) "
        #         f"cannot exceed Quantity for Auction ({auction_qty})"
        #     )

        # ================= Total Winning Quantity Validation =================
        if total_winning_qty > auction_qty:
            frappe.throw(
                f"Total Winning Quantity ({total_winning_qty}) "
                f"cannot exceed Quantity for Auction ({auction_qty})"
            )

        # ================= Check Existing Document =================
        existing_doc_name = frappe.db.get_value(
            "Price Discovery",
            {"auction_id": auction_id},
            "name"
        )

        # ================= Update Existing =================
        if existing_doc_name:

            doc = frappe.get_doc(
                "Price Discovery",
                existing_doc_name
            )

            # Clear Old Rows
            doc.price_discovery_table = []

        # ================= Create New =================
        else:

            doc = frappe.new_doc(
                "Price Discovery"
            )

            doc.auction_id = auction_id

        # ================= Append Child Table Rows =================
        for row in data.get(
            "price_discovery_table",
            []
        ):

            bid_time = row.get("bid_time")

            # Default Current Datetime
            if not bid_time:
                bid_time = frappe.utils.now_datetime()

            doc.append(
                "price_discovery_table",
                {
                    "bidder_id": row.get("bidder_id"),
                    "bid_price": row.get("bid_price"),
                    "bid_quantity": row.get("bid_quantity"),
                    "service_provider": row.get(
                        "service_provider"
                    ),
                    "winning_quantity": row.get(
                        "winning_quantity"
                    ),
                    "bid_time": bid_time,
                    "note": row.get("note")
                }
            )

        # ================= Save Document =================
        doc.save(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "message": (
                "Price Discovery Updated Successfully"
                if existing_doc_name
                else "Price Discovery Created Successfully"
            ),
            "name": doc.name
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Price Discovery API Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }
    

# ================= CREATE PRICE MATCHING ROUND BIDS =================

@frappe.whitelist(allow_guest=True)
def create_price_matching_round_bids():

    try:

        # ================= Validate Token =================
        user = validate_token()

        if not user:
            frappe.throw("Invalid Token")

        frappe.set_user(user)

        # ================= Get Request Data =================
        data = frappe.request.get_json()

        if not data:
            return {
                "status": "failed",
                "message": "No data provided"
            }

        auction_id = data.get("auction_id")
        bids = data.get("price_discovery_table", [])

        if not auction_id:
            return {
                "status": "failed",
                "message": "auction_id is required"
            }

        # =====================================================
        # CHECK AUCTION
        # =====================================================
        if not frappe.db.exists("Auction", auction_id):
            frappe.throw("Auction not found")

        auction = frappe.get_doc("Auction", auction_id)

        # =====================================================
        # GET RESULT DATA
        # =====================================================
        results = auction.result or []

        if not results:
            frappe.throw("No auction result found")

        # =====================================================
        # FIND HIGHEST PRICE (H1)
        # =====================================================
        h1_price = max([flt(r.bid_price or 0) for r in results])

        total_winning_qty = 0

        for r in results:

            price = flt(r.bid_price or 0)
            qty = flt(r.awarded_quantity or 0)

            if price == h1_price:
                total_winning_qty += qty

        # =====================================================
        # ROUND 2 LOGIC
        # =====================================================
        total_qty = flt(auction.quantity_for_auction or 0)

        if total_qty > total_winning_qty:

            is_round2_required = True

            qty_for_round2 = total_qty - total_winning_qty

        else:

            is_round2_required = False

            qty_for_round2 = 0

        # =====================================================
        # VALIDATE ROUND 2 ALLOWED OR NOT
        # =====================================================
        if not is_round2_required:
            frappe.throw("Price Matching Round is not allowed")

        # =====================================================
        # ALLOWED VALUES
        # =====================================================
        allowed_qty = flt(qty_for_round2, 3)
        allowed_rate = flt(h1_price)

        # ================= Create Price Discovery =================
        pd_doc = frappe.new_doc("Price Discovery")

        pd_doc.auction_id = auction_id
        pd_doc.round = "price matching rounds"

        # =====================================================
        # VALIDATE + ADD BIDS
        # =====================================================
        for row in bids:

            bid_qty = flt(row.get("bid_quantity"))
            bid_rate = flt(row.get("bid_price"))

            # ================= VALIDATION =================

            # Quantity should be exact
            if bid_qty != allowed_qty:
                frappe.throw(
                    f"Bid Quantity must be exactly {allowed_qty}"
                )

            # Rate should not be less than H1 price
            if bid_rate < allowed_rate:
                frappe.throw(
                    f"Bid Price cannot be less than {allowed_rate}"
                )

            pd_doc.append("price_discovery_table", {

                "bidder_id": row.get("bidder_id"),

                "bid_price": bid_rate,

                "bid_quantity": bid_qty,

                "bid_time": row.get("bid_time").strip()
                if row.get("bid_time")
                else None,

                "round": "price matching rounds",

                "service_provider": row.get("service_provider")

            })

        # ================= Save =================
        pd_doc.insert(ignore_permissions=True)

        frappe.db.commit()

        # ================= Final Response =================
        return {
            "message": {
                "status": "success",
                "message": "Price Discovery Created Successfully",
                "name": pd_doc.name,
                "allowed_quantity": allowed_qty,
                "allowed_bid_price": allowed_rate
            }
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "create_price_matching_round_bids Error"
        )

        return {
            "message": {
                "status": "failed",
                "message": str(e)
            }
        }