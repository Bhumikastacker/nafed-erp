import frappe
import jwt
from datetime import datetime, timedelta
from nafed_erp.procure_to_pay.api.get_token import get_secret


# ================= TOKEN VALIDATION =================
def validate_token():

    auth_header = frappe.get_request_header("Authorization")

    if not auth_header:
        frappe.throw("Authorization header missing", frappe.AuthenticationError)

    if not auth_header.startswith("Bearer "):
        frappe.throw("Invalid Authorization Header", frappe.AuthenticationError)

    try:
        token = auth_header.split(" ")[1]

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



# ================= GET AUCTION BY DATE =================
@frappe.whitelist(allow_guest=True)
def get_auction_by_date(
    date=None,
    pageSize=10,
    pageNumber=1,
    auctionid=None
):

    # ================= Validate Token =================
    user = validate_token()

    if not user:
        frappe.throw("Invalid Token")

    frappe.set_user(user)

    # ================= Get Portal User =================
    portal_user = frappe.db.exists(
        "Portal Users",
        {"user": user}
    )

    if not portal_user:
        frappe.throw("Portal User not found")

    print("Portal User Found:", portal_user)

    # ================= Get Allowed Auctions =================
    allowed_auctions = frappe.db.sql("""
        SELECT ap.parent
        FROM `tabAdd Protals` ap
        WHERE ap.portal = %s
    """, (portal_user,), as_dict=True)

    allowed_auction_names = [
        d.parent for d in allowed_auctions
    ]

    print("Allowed Auctions:", allowed_auction_names)

    # ================= Validate Date =================
    if not date:
        frappe.throw("Date is required")

    try:
        date_obj = datetime.strptime(
            date,
            "%d/%m/%Y"
        ).date()

    except ValueError:
        frappe.throw(
            "Invalid date format. Use dd/MM/yyyy"
        )

    # ================= Pagination =================
    pageSize = int(pageSize)
    pageNumber = int(pageNumber)

    # ================= Filters =================
    filters = {
        "date_time": date_obj,
        "name": ["in", allowed_auction_names]
    }

    if auctionid:
        filters["name"] = auctionid

    # ================= Fetch Auctions =================
    auctions = frappe.get_all(
        "Auction",
        filters=filters,
        fields=[
            "name",
            "date_time",

            "scheme",
            "season",
            "scheme_code",

            "commodity",
            "commodity_name",

            "state",
            "state_code",

            "branch",
            "branch_code",

            "reserve_price",
            "quantity_for_auction",

            "status",

            "start_time_price_discovery_round",
            "end_time_price_discovery_round",

            "start_time_h1_discovery",
            "end_time_h1_discovery",

            "start_time_price_matching_round",
            "end_time_price_matching_round",

            "start_time_price_matching_submission",
            "end_time_price_matching_submission"
        ],
        limit_start=(pageNumber - 1) * pageSize,
        limit_page_length=pageSize,
        order_by="date_time asc"
    )

    result = []

    for a in auctions:

        result.append({

            "AuctionId": a.name or "",

            "Date": (
                a.date_time.strftime("%d/%m/%Y")
                if a.date_time else ""
            ),

            "Warehouse": a.branch or "",
            "WarehouseCode": a.branch_code or "",

            "WarehouseDistrict": "",
            "WarehouseAddress": "",

            "StateCode": a.state_code or "",
            "State": a.state or "",

            "CommodityCode": a.commodity or "",
            "Commodity": (
                a.commodity_name
                or a.commodity
                or ""
            ),

            "SchemeName": a.scheme or "",
            "CommodityYear": "",

            "Season": a.season or "",
            "SeasonCode": a.scheme_code or "",

            "ReservePrice": a.reserve_price or 0,
            "QtyForAuction": (
                a.quantity_for_auction or 0
            ),

            "StartTimePriceDiscovery":
                format_time(
                    a.start_time_price_discovery_round
                ),

            "EndTimePriceDiscovery":
                format_time(
                    a.end_time_price_discovery_round
                ),

            "StartTimeH1Discovery":
                format_time(
                    a.start_time_h1_discovery
                ),

            "EndTimeH1Discovery":
                format_time(
                    a.end_time_h1_discovery
                ),

            "StartTimePriceMatching":
                format_time(
                    a.start_time_price_matching_round
                ),

            "EndTimePriceMatching":
                format_time(
                    a.end_time_price_matching_round
                ),

            "StartTimePriceMatchingSubmission":
                format_time(
                    a.start_time_price_matching_submission
                ),

            "EndTimePriceMatchingSubmission":
                format_time(
                    a.end_time_price_matching_submission
                ),

            "Status": get_status_int(a.status),

            "StatusCode": (
                a.status.upper()
                if a.status else ""
            ),

            "IsR1LogFileSubmitted": False,
            "IsR2LogFileSubmitted": False,

            "BidCountRound1": 0,
            "BidCountRound2": 0,

            "Branch": a.branch or "",
            "BranchCode": a.branch_code or ""
        })

    return result


# ================= GET AUCTION BY DATE =================
@frappe.whitelist(allow_guest=True)
def get_auction_by_date_ims(
    date=None,
    pageSize=10,
    pageNumber=1,
    auctionid=None
):

    # ================= Validate Date =================
    if not date:
        frappe.throw("Date is required")

    try:
        date_obj = datetime.strptime(
            date,
            "%d/%m/%Y"
        ).date()

    except ValueError:
        frappe.throw(
            "Invalid date format. Use dd/MM/yyyy"
        )

    # ================= Pagination =================
    pageSize = int(pageSize)
    pageNumber = int(pageNumber)

    # ================= Filters =================
    filters = {
        "date_time": date_obj
    }

    if auctionid:
        filters["name"] = auctionid

    # ================= Fetch Auctions =================
    auctions = frappe.get_all(
        "Auction",
        filters=filters,
        fields=[
            "name",
            "date_time",

            "scheme",
            "season",
            "scheme_code",

            "commodity",
            "commodity_name",

            "state",
            "state_code",

            "branch",
            "branch_code",

            "reserve_price",
            "quantity_for_auction",

            "status",

            "start_time_price_discovery_round",
            "end_time_price_discovery_round",

            "start_time_h1_discovery",
            "end_time_h1_discovery",

            "start_time_price_matching_round",
            "end_time_price_matching_round",

            "start_time_price_matching_submission",
            "end_time_price_matching_submission"
        ],
        limit_start=(pageNumber - 1) * pageSize,
        limit_page_length=pageSize,
        order_by="date_time asc"
    )

    result = []

    for a in auctions:

        result.append({

            "AuctionId": a.name or "",

            "Date": (
                a.date_time.strftime("%d/%m/%Y")
                if a.date_time else ""
            ),

            "Warehouse": a.branch or "",
            "WarehouseCode": a.branch_code or "",

            "WarehouseDistrict": "",
            "WarehouseAddress": "",

            "StateCode": a.state_code or "",
            "State": a.state or "",

            "CommodityCode": a.commodity or "",
            "Commodity": (
                a.commodity_name
                or a.commodity
                or ""
            ),

            "SchemeName": a.scheme or "",
            "CommodityYear": "",

            "Season": a.season or "",
            "SeasonCode": a.scheme_code or "",

            "ReservePrice": a.reserve_price or 0,
            "QtyForAuction": (
                a.quantity_for_auction or 0
            ),

            "StartTimePriceDiscovery":
                format_time(
                    a.start_time_price_discovery_round
                ),

            "EndTimePriceDiscovery":
                format_time(
                    a.end_time_price_discovery_round
                ),

            "StartTimeH1Discovery":
                format_time(
                    a.start_time_h1_discovery
                ),

            "EndTimeH1Discovery":
                format_time(
                    a.end_time_h1_discovery
                ),

            "StartTimePriceMatching":
                format_time(
                    a.start_time_price_matching_round
                ),

            "EndTimePriceMatching":
                format_time(
                    a.end_time_price_matching_round
                ),

            "StartTimePriceMatchingSubmission":
                format_time(
                    a.start_time_price_matching_submission
                ),

            "EndTimePriceMatchingSubmission":
                format_time(
                    a.end_time_price_matching_submission
                ),

            "Status": get_status_int(a.status),

            "StatusCode": (
                a.status.upper()
                if a.status else ""
            ),

            "IsR1LogFileSubmitted": False,
            "IsR2LogFileSubmitted": False,

            "BidCountRound1": 0,
            "BidCountRound2": 0,

            "Branch": a.branch or "",
            "BranchCode": a.branch_code or ""
        })

    return result
# ================= FORMAT TIME =================
def format_time(value):

    if not value:
        return ""

    # Time field returns timedelta
    if isinstance(value, timedelta):

        total_seconds = int(value.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # Datetime field
    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")

    # String fallback
    return str(value)


# ================= STATUS MAPPING =================
def get_status_int(status):

    status_map = {
        "Draft": 0,
        "Approved": 1,
        "Cancelled": 2
    }

    return status_map.get(status, 0)


@frappe.whitelist(allow_guest=True)
def get_price_matching_result(auction_code):

    # 🔐 Validate Token
    user = validate_token()
    frappe.set_user(user)

    # ================= CHECK AUCTION =================
    if not frappe.db.exists("Auction", auction_code):
        frappe.local.response.http_status_code = 404
        frappe.local.response["message"] = None
        frappe.local.response["data"] = {
            "AuctionId": auction_code,
            "Success": False,
            "Message": "Auction not found",
            "ResponseCode": "P001",
            "BidPrice": 0.0,
            "WiningBidders": None
        }
        return

    # ================= GET AUCTION =================
    auction = frappe.get_doc("Auction", auction_code)

    # ================= RESULT TABLE =================
    results = auction.result or []

    # ❌ No Result Found
    if not results:
        frappe.local.response["message"] = None
        frappe.local.response["data"] = {
            "AuctionId": auction_code,
            "Success": False,
            "Message": "Sorry, No one won from any of the portal this time.",
            "ResponseCode": "P004",
            "BidPrice": 0.0,
            "WiningBidders": None
        }
        return

    # ================= FIND HIGHEST PRICE =================
    h1_price = max([float(r.bid_price or 0) for r in results])

    winning_bidders = []
    total_winning_qty = 0

    for r in results:

        price = float(r.bid_price or 0)
        qty = float(r.awarded_quantity or 0)

        # Highest price wale bidders
        if price == h1_price:

            total_winning_qty += qty

            winning_bidders.append({
                "BidderId": r.bidder_id or "",
                "WinningQuantity": qty,
                "BidPrice": price,
                "ServiceProvider": r.auction_portal or "",
                "Criteria": r.criteria or "",
                "Round": r.round or "",
                "BidLogTime": r.bid_log_time or ""
            })

    # ================= ROUND 2 LOGIC =================
    total_qty = float(auction.quantity_for_auction or 0)

    if total_qty > total_winning_qty:
        is_round2_required = True
        qty_for_round2 = total_qty - total_winning_qty
    else:
        is_round2_required = False
        qty_for_round2 = 0

    # ================= PAGINATION HEADER =================
    frappe.local.response["headers"] = {
        "X-Pagination": frappe.as_json({
            "winnerCount": len(winning_bidders)
        }, indent=None)
    }

    # ================= FINAL RESPONSE =================
    frappe.local.response["message"] = None
    frappe.local.response["data"] = {
        "AuctionId": auction_code,
        "Success": True,
        "Message": "Success",
        "ResponseCode": "P000",
        "BidPrice": h1_price,
        "WiningBidders": winning_bidders,
        "IsMovedToPriceMatching": is_round2_required,
       "QuantityForMatchingRound": round(qty_for_round2, 3)
    }

    return


@frappe.whitelist(allow_guest=True)
def get_winning_bidder_full_details_post():

    # =========================================================
    # 🔐 TOKEN VALIDATION
    # =========================================================
    user = validate_token()
    frappe.set_user(user)

    # =========================================================
    # ✅ HANDLE JSON / FORM-DATA / PARAMS
    # =========================================================
    data = frappe.request.get_json(silent=True) or frappe.form_dict

    auction_code = data.get("auction_code")

    # =========================================================
    # ✅ VALIDATION
    # =========================================================
    if not auction_code:
        frappe.local.response.http_status_code = 400

        return {
            "success": False,
            "message": "auction_code is required"
        }

    if not frappe.db.exists("Auction", auction_code):
        frappe.local.response.http_status_code = 404

        return {
            "success": False,
            "message": "Auction not found"
        }

    # =========================================================
    # ✅ FETCH AUCTION
    # =========================================================
    auction = frappe.get_doc("Auction", auction_code)

    # =========================================================
    # 🔥 STEP 1 : SAVE / UPDATE BIDDER DETAILS
    # =========================================================
    if data.get("bidder_id"):

        bidder_rows = getattr(
            auction,
            "bidder_details_submission",
            []
        ) or []

        existing = next(
            (
                b for b in bidder_rows
                if b.bidder_id == data.get("bidder_id")
            ),
            None
        )

        # =====================================================
        # 🔄 UPDATE EXISTING ROW
        # =====================================================
        if existing:

            existing.auction_code = auction_code
            existing.bidder_name = data.get("bidder_name")
            existing.firm_name = data.get("firm_name")
            existing.email = data.get("email")
            existing.moblie = data.get("moblie")
            existing.pan = data.get("pan")
            existing.city = data.get("city")
            existing.state = data.get("state")
            existing.address = data.get("address")
            existing.tan = data.get("tan")
            existing.gst = data.get("gst")
            existing.bank_account_no = data.get("bank_account_no")
            existing.ifsc = data.get("ifsc")
            existing.account_holder_name = data.get(
                "account_holder_name"
            )

        # =====================================================
        # ➕ ADD NEW ROW
        # =====================================================
        else:

            auction.append("bidder_details_submission", {
                "auction_code": auction_code,
                "bidder_id": data.get("bidder_id"),
                "bidder_name": data.get("bidder_name"),
                "firm_name": data.get("firm_name"),
                "email": data.get("email"),
                "moblie": data.get("moblie"),
                "pan": data.get("pan"),
                "city": data.get("city"),
                "state": data.get("state"),
                "address": data.get("address"),
                "tan": data.get("tan"),
                "gst": data.get("gst"),
                "bank_account_no": data.get("bank_account_no"),
                "ifsc": data.get("ifsc"),
                "account_holder_name": data.get(
                    "account_holder_name"
                )
            })

        auction.save(ignore_permissions=True)
        frappe.db.commit()

        # reload updated doc
        auction.reload()

    # =========================================================
    # 🔥 STEP 2 : GET ROUND TABLE
    # =========================================================
    # ⚠️ Replace fieldnames below if your child table name differs
    # =========================================================

    possible_round_fields = [
        "price_discover_round",
        "price_discovery_round",
        "price_discovery_table",
        "auction_result",
        "result",
        "auction_round"
    ]

    rounds = []

    for fieldname in possible_round_fields:

        if hasattr(auction, fieldname):

            rounds = getattr(auction, fieldname) or []

            if rounds:
                break

    # =========================================================
    # ❌ NO ROUND DATA
    # =========================================================
    if not rounds:

        frappe.local.response.http_status_code = 404

        return {
            "success": False,
            "message": "No winning data found"
        }

    # =========================================================
    # ✅ GET H1 PRICE
    # =========================================================
    try:

        h1_price = max([
            float(r.bid_price or 0)
            for r in rounds
        ])

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Winning Bidder Price Error"
        )

        frappe.local.response.http_status_code = 500

        return {
            "success": False,
            "message": "Invalid bid price data"
        }

    # =========================================================
    # ✅ PREPARE RESULT
    # =========================================================
    result = []

    bidder_rows = getattr(
        auction,
        "bidder_details_submission",
        []
    ) or []

    for r in rounds:

        try:
            current_price = float(r.bid_price or 0)
        except Exception:
            current_price = 0

        # =====================================================
        # ✅ ONLY H1 BIDDERS
        # =====================================================
        if current_price == h1_price:

            bidder_id = (
                getattr(r, "bidder_id", None)
                or ""
            )

            bidder_detail = next(
                (
                    b for b in bidder_rows
                    if b.bidder_id == bidder_id
                ),
                None
            )

            result.append({

                # =============================================
                # AUCTION DATA
                # =============================================
                "AuctionId": auction_code,
                "BidderId": bidder_id,
                "BidPrice": current_price,
                "WinningQuantity": getattr(
                    r,
                    "winning_quantity",
                    0
                ),
                "ServiceProvider": getattr(
                    r,
                    "service_provider",
                    ""
                ),

                # =============================================
                # BIDDER DETAILS
                # =============================================
                "BidderName":
                    bidder_detail.bidder_name
                    if bidder_detail else "",

                "FirmName":
                    bidder_detail.firm_name
                    if bidder_detail else "",

                "Email":
                    bidder_detail.email
                    if bidder_detail else "",

                "Mobile":
                    bidder_detail.moblie
                    if bidder_detail else "",

                "PAN":
                    bidder_detail.pan
                    if bidder_detail else "",

                "City":
                    bidder_detail.city
                    if bidder_detail else "",

                "State":
                    bidder_detail.state
                    if bidder_detail else "",

                "Address":
                    bidder_detail.address
                    if bidder_detail else "",

                "Tan":
                    bidder_detail.tan
                    if bidder_detail else "",

                "GST":
                    bidder_detail.gst
                    if bidder_detail else "",

                "BankAccountNo":
                    bidder_detail.bank_account_no
                    if bidder_detail else "",

                "IFSC":
                    bidder_detail.ifsc
                    if bidder_detail else "",

                "AccountHolderName":
                    bidder_detail.account_holder_name
                    if bidder_detail else ""
            })

    # =========================================================
    # ✅ FINAL RESPONSE
    # =========================================================
    frappe.local.response.http_status_code = 200

    return {
        "success": True,
        "auction_id": auction_code,
        "highest_bid_price": h1_price,
        "total_winners": len(result),
        "data": result
    }