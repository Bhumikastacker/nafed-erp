import frappe
from frappe.model.document import Document


class PriceDiscovery(Document):
    pass


# =========================================================
# MAIN PROCESSING METHOD
# =========================================================
def process_pqt_price_discovery(auction_id):

    try:

        # =========================================================
        # GET AUCTION
        # =========================================================
        if not frappe.db.exists("Auction", auction_id):

            frappe.logger().info(
                f"❌ Auction not found: {auction_id}"
            )

            return

        auction = frappe.get_doc(
            "Auction",
            auction_id
        )

        # =========================================================
        # GET ALL PRICE DISCOVERY DOCS
        # =========================================================
        pd_docs = frappe.get_all(

            "Price Discovery",

            filters={
                "auction_id": auction_id
            },

            fields=["name"]

        )

        if not pd_docs:

            frappe.logger().info(
                f"❌ No Price Discovery docs found for {auction_id}"
            )

            return

        # =========================================================
        # MERGE ALL ROWS
        # =========================================================
        all_rows = []

        for pd in pd_docs:

            pd_doc = frappe.get_doc(
                "Price Discovery",
                pd.name
            )

            if pd_doc.price_discovery_table:

                all_rows.extend(
                    pd_doc.price_discovery_table
                )

        if not all_rows:

            frappe.logger().info(
                "❌ No rows found in price_discovery_table"
            )

            return

        # =========================================================
        # SEPARATE ROUNDS
        # =========================================================
        price_discovery_bids = []
        price_matching_bids = []

        for row in all_rows:

            round_name = (
                (row.round or "")
                .strip()
                .lower()
            )

            # SAFE CHECK
            if "price matching" in round_name:

                price_matching_bids.append(row)

            else:

                price_discovery_bids.append(row)

        # =========================================================
        # PQT LOGIC FUNCTION
        # =========================================================
        def get_best_bid(rows):

            bids = []

            for row in rows:

                bid_time_seconds = 0

                if row.bid_time:

                    try:

                        bid_time_seconds = (
                            row.bid_time.total_seconds()
                        )

                    except Exception:

                        bid_time_seconds = 0

                bids.append({

                    "bidder_id": row.bidder_id,

                    "price": float(
                        row.bid_price or 0
                    ),

                    "qty": float(
                        row.bid_quantity or 0
                    ),

                    "service_provider": row.service_provider,

                    "time_seconds": bid_time_seconds,

                    "bid_time": row.bid_time

                })

            if not bids:

                return None, None

            # =========================================================
            # SORTING
            # P = Highest Price
            # Q = Highest Quantity
            # T = Latest Time
            # =========================================================
            bids.sort(

                key=lambda x: (

                    -x["price"],
                    -x["qty"],
                    -x["time_seconds"]

                )

            )

            best_bid = bids[0]

            # =========================================================
            # CRITERIA NOTE
            # =========================================================
            note = "Selected based on: "

            same_price = [

                b for b in bids
                if b["price"] == best_bid["price"]

            ]

            if len(same_price) == 1:

                note += "P (Highest Price)"

            else:

                same_qty = [

                    b for b in same_price
                    if b["qty"] == best_bid["qty"]

                ]

                if len(same_qty) == 1:

                    note += "Q (Highest Quantity among same price bids)"

                else:

                    note += "T (Latest Time among same price & quantity bids)"

            return best_bid, note

        # =========================================================
        # CLEAR OLD TABLES
        # =========================================================
        auction.set("result", [])

        auction.set(
            "price_discovery_round_log",
            []
        )

        auction.set(
            "price_matching_round",
            []
        )

        # =========================================================
        # PRICE DISCOVERY ROUND
        # =========================================================
        if price_discovery_bids:

            best_bid, note = get_best_bid(
                price_discovery_bids
            )

            if best_bid:

                # =========================================================
                # ADD RESULT
                # =========================================================
                auction.append(
                    "result",
                    {

                        "auction_portal": best_bid["service_provider"],

                        "bidder_id": best_bid["bidder_id"],

                        "bid_price": best_bid["price"],

                        "awarded_quantity": best_bid["qty"],

                        "criteria": note,

                        "round": "Price Discovery",

                        "bid_log_time": best_bid["bid_time"]

                    }
                )

                # =========================================================
                # REMAINING QTY
                # =========================================================
                quantity_for_auction = float(
                    auction.quantity_for_auction or 0
                )

                awarded_quantity = float(
                    best_bid["qty"] or 0
                )

                remaining_quantity = (
                    quantity_for_auction - awarded_quantity
                )

                if remaining_quantity < 0:

                    remaining_quantity = 0

                # =========================================================
                # ADD PRICE MATCHING ROUND TABLE
                # =========================================================
                auction.append(
                    "price_matching_round",
                    {

                        "quantity": remaining_quantity,

                        "bid_price": best_bid["price"]

                    }
                )

                frappe.logger().info(
                    "✅ Price Discovery Winner Added"
                )

        # =========================================================
        # PRICE MATCHING ROUND
        # =========================================================
        if price_matching_bids:

            frappe.logger().info(
                "🚀 Processing Price Matching Round"
            )

            pm_best_bid, pm_note = get_best_bid(
                price_matching_bids
            )

            if pm_best_bid:

                auction.append(
                    "result",
                    {

                        "auction_portal": pm_best_bid["service_provider"],

                        "bidder_id": pm_best_bid["bidder_id"],

                        "bid_price": pm_best_bid["price"],

                        "awarded_quantity": pm_best_bid["qty"],

                        "criteria": pm_note,

                        "round": "Price Matching Round",

                        "bid_log_time": pm_best_bid["bid_time"]

                    }
                )

                frappe.logger().info(
                    "✅ Price Matching Winner Added"
                )

        # =========================================================
        # SERVICE PROVIDER LOGS
        # =========================================================
        service_provider_logs = {}

        for row in all_rows:

            provider = (
                row.service_provider
                or "Unknown"
            )

            if provider not in service_provider_logs:

                service_provider_logs[provider] = {

                    "bid_count": 0,

                    "last_bid_time": row.bid_time,

                    "round": row.round

                }

            service_provider_logs[provider]["bid_count"] += 1

            existing_time = (
                service_provider_logs[provider]["last_bid_time"]
            )

            if row.bid_time:

                if (

                    not existing_time

                    or row.bid_time > existing_time

                ):

                    service_provider_logs[provider]["last_bid_time"] = (
                        row.bid_time
                    )

        # =========================================================
        # APPEND LOGS
        # =========================================================
        for provider, values in service_provider_logs.items():

            auction.append(
                "price_discovery_round_log",
                {

                    "service_provider": provider,

                    "bid_time": values["last_bid_time"],

                    "bid_count": values["bid_count"],

                    "round": values["round"]

                }
            )

        # =========================================================
        # SAVE AUCTION
        # =========================================================
        auction.save(
            ignore_permissions=True
        )

        frappe.db.commit()

        frappe.logger().info(
            f"✅ Auction Updated Successfully: {auction.name}"
        )

    except Exception:

        frappe.log_error(

            frappe.get_traceback(),

            "Price Discovery PQT Error"

        )


# =========================================================
# ON UPDATE
# =========================================================
def on_update(doc, method):

    try:

        if not doc.auction_id:

            return

        process_pqt_price_discovery(
            doc.auction_id
        )

    except Exception:

        frappe.log_error(

            frappe.get_traceback(),

            "Price Discovery On Update Error"

        )


# =========================================================
# SCHEDULER METHOD
# =========================================================
def run_price_discovery_scheduler():

    try:

        frappe.logger().info(
            "🚀 Price Discovery Scheduler Started"
        )

        pd_list = frappe.get_all(

            "Price Discovery",

            filters={
                "docstatus": 0
            },

            fields=[
                "name",
                "auction_id"
            ]

        )

        frappe.logger().info(
            f"📌 Total Price Discovery Docs: {len(pd_list)}"
        )

        # =========================================================
        # PREVENT DUPLICATE AUCTION PROCESSING
        # =========================================================
        processed_auctions = set()

        for pd in pd_list:

            try:

                if not pd.auction_id:

                    continue

                # =========================================================
                # SKIP DUPLICATES
                # =========================================================
                if pd.auction_id in processed_auctions:

                    continue

                processed_auctions.add(
                    pd.auction_id
                )

                # =========================================================
                # PROCESS
                # =========================================================
                process_pqt_price_discovery(
                    pd.auction_id
                )

                frappe.logger().info(
                    f"✅ PQT Processed: {pd.auction_id}"
                )

            except Exception:

                frappe.log_error(

                    frappe.get_traceback(),

                    f"PQT Scheduler Auction Error - {pd.auction_id}"

                )

    except Exception:

        frappe.log_error(

            frappe.get_traceback(),

            "Price Discovery Scheduler Error"

        )