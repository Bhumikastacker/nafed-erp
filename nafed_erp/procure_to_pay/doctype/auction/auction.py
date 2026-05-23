# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import nowdate, get_datetime, add_to_date
from frappe.model.document import Document
from frappe.utils import cint

import json

import json
import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, add_to_date


class Auction(Document):

    def validate(self):
        # Auto set round timings
        self.set_round_timings()

    def before_save(self):
        # Auto create customer from bidder table
        self.create_customer_from_bidder()

    def on_update_after_submit(self):
        # Run again after submit update
        self.create_customer_from_bidder()

    def create_customer_from_bidder(self):
        """
        Auto create Customer from Bidder Details Submission
        """

        if not self.get("bidder_details_submission"):
            return

        for row in self.bidder_details_submission:

            # Skip empty bidder name
            if not row.bidder_name:
                continue

            # If already linked customer exists
            if row.get("customer"):
                continue

            # Check existing customer
            existing_customer = frappe.db.exists(
                "Customer",
                {"customer_name": row.bidder_name}
            )

            if existing_customer:
                row.customer = existing_customer
                continue

            try:
                customer = frappe.new_doc("Customer")

                # Basic fields
                customer.customer_name = row.bidder_name
                customer.customer_type = "Company"

                # Mandatory defaults
                if hasattr(customer, "customer_group"):
                    customer.customer_group = "Commercial"

                if hasattr(customer, "territory"):
                    customer.territory = "India"

                # Mobile
                if hasattr(customer, "mobile_no"):
                    customer.mobile_no = row.moblie

                # Email
                if hasattr(customer, "email_id"):
                    customer.email_id = row.email

                # GSTIN
                if hasattr(customer, "gstin"):
                    customer.gstin = row.gst

                customer.insert(ignore_permissions=True)

                # Link customer back to child row
                row.customer = customer.name

                frappe.msgprint(
                    f"Customer Created: {customer.name}"
                )

            except Exception:
                frappe.log_error(
                    title="Customer Creation Failed",
                    message=frappe.get_traceback()
                )

                frappe.throw(frappe.get_traceback())
    def set_round_timings(self):
        """
        Auto set all auction round timings with minimum
        10 minutes gap between each start and end time
        """

        if not self.date_time or not self.start_time_price_discovery_round:
            return

        # Combine Date + Time for first round start
        first_start = get_datetime(
            f"{self.date_time} {self.start_time_price_discovery_round}"
        )

        # 1. End Time (Price Discovery Round)
        self.end_time_price_discovery_round = add_to_date(
            first_start,
            minutes=10,
            as_datetime=True
        )

        # 2. Start Time (H1 Discovery)
        self.start_time_h1_discovery = add_to_date(
            self.end_time_price_discovery_round,
            minutes=10,
            as_datetime=True
        )

        # 3. End Time (H1 Discovery)
        self.end_time_h1_discovery = add_to_date(
            self.start_time_h1_discovery,
            minutes=10,
            as_datetime=True
        )

        # 4. Start Time (Price Matching Round)
        self.start_time_price_matching_round = add_to_date(
            self.end_time_h1_discovery,
            minutes=10,
            as_datetime=True
        )

        # 5. End Time (Price Matching Round)
        self.end_time_price_matching_round = add_to_date(
            self.start_time_price_matching_round,
            minutes=10,
            as_datetime=True
        )

        # 6. Start Time (Price Matching Submission)
        self.start_time_price_matching_submission = add_to_date(
            self.end_time_price_matching_round,
            minutes=10,
            as_datetime=True
        )

        # 7. End Time (Price Matching Submission)
        self.end_time_price_matching_submission = add_to_date(
            self.start_time_price_matching_submission,
            minutes=10,
            as_datetime=True
        )

   

@frappe.whitelist()
def get_item_warehouse_stock(item_code, company=None):
    """
    Fetch item stock warehouse-wise from Bin table

    Also fetch:
    - UOM from Item master (stock_uom)
    - Warehouse Name from Warehouse doctype (warehouse_name)

    Filter only selected Branch (Company) warehouses
    """

    if not item_code:
        return []

    conditions = ""

    # Branch = Company filter
    if company:
        conditions += " AND w.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            b.warehouse,
            w.warehouse_name,
            w.company,
            i.stock_uom AS uom,
            COALESCE(SUM(b.actual_qty), 0) AS actual_qty
        FROM `tabBin` b

        LEFT JOIN `tabWarehouse` w
            ON b.warehouse = w.name

        LEFT JOIN `tabItem` i
            ON b.item_code = i.item_code

        WHERE
            b.item_code = %(item_code)s
            AND b.actual_qty > 0
            {conditions}

        GROUP BY
            b.warehouse,
            w.warehouse_name,
            w.company,
            i.stock_uom

        HAVING
            SUM(b.actual_qty) > 0

        ORDER BY
            b.warehouse
        """,
        {
            "item_code": item_code,
            "company": company
        },
        as_dict=True
    )

    # Debug logs
    frappe.errprint("===== STOCK FETCH DEBUG =====")
    frappe.errprint(f"Item Code: {item_code}")
    frappe.errprint(f"Company (Branch): {company}")
    frappe.errprint(data)

    return data



@frappe.whitelist()

# def create_sales_order_and_reservation(auction_name):

#     auction = frappe.get_doc("Auction", auction_name)

#     if not auction.bidder_details_submission:
#         frappe.throw("No Bidder found")

#     if not auction.result:
#         frappe.throw("No Result data found")

#     # if not auction.auction_details:
#     #     frappe.throw("No Auction Details found")

#     # Winner row from result table
#     result_row = auction.result[0]

#     bidder_id = result_row.bidder_id

#     # Find bidder details
#     bidder = None

#     for row in auction.bidder_details_submission:
#         if row.bidder_id == bidder_id:
#             bidder = row
#             break

#     if not bidder:
#         frappe.throw("Winner bidder details not found")

#     customer_name = bidder.bidder_name

#     # Check customer
#     existing_customer = frappe.db.get_value(
#         "Customer",
#         {"customer_name": customer_name},
#         "name"
#     )

#     if existing_customer:
#         customer = frappe.get_doc("Customer", existing_customer)

#     else:
#         customer = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "customer_type": "Individual"
#         })

#         customer.insert(ignore_permissions=True)

#     # Result table data
#     qty = float(result_row.awarded_quantity or 0)
#     rate = float(result_row.bid_price or 0)

#     # Create Sales Order
#     so = frappe.get_doc({
#         "doctype": "Sales Order",
#         "customer": customer.name,
#         "transaction_date": nowdate(),
#         "delivery_date": nowdate(),
#         "reserve_stock": 1,
#         "custom_auction_id": auction.name,
#         "custom_urgency_level": "Normal",
#         "items": []
#     })

#     # Auction warehouse rows
#     # for row in auction.auction_details:

#     #     so.append("items", {
#     #         "item_code": auction.commodity,
#     #         "qty": qty,
#     #         "rate": rate,
#     #         "warehouse": row.warehouse
#     #     })

#     so.insert(ignore_permissions=True)
#     so.submit()

#     frappe.msgprint(
#         f"Sales Order {so.name} created and stock reserved successfully"
#     )

#     return {
#         "sales_order": so.name
#     }

@frappe.whitelist()
def create_sales_order_and_reservation(auction_name):

    # =========================
    # GET AUCTION
    # =========================
    auction = frappe.get_doc("Auction", auction_name)

    if not auction.result:
        frappe.throw("No Result data found")

    if not auction.auction_schedule_id:
        frappe.throw("Auction Schedule ID not found")

    # =========================
    # GET AUCTION SCHEDULE
    # =========================
    auction_schedule = frappe.get_doc(
        "Auction Schedule",
        auction.auction_schedule_id
    )

    if not auction_schedule.auction_details_view:
        frappe.throw("No Auction Details View data found in Auction Schedule")

    # =========================
    # WINNER DETAILS FROM RESULT
    # =========================
    result_row = auction.result[0]

    bidder_id = result_row.bidder_id
    awarded_qty = float(result_row.awarded_quantity or 0)
    rate = float(result_row.bid_price or 0)

    # =========================
    # FIND BIDDER
    # =========================
    bidder = None

    for row in auction.bidder_details_submission:
        if row.bidder_id == bidder_id:
            bidder = row
            break

    if not bidder:
        frappe.throw("Winner bidder details not found")

    customer_name = bidder.bidder_name

    # =========================
    # CUSTOMER CHECK / CREATE
    # =========================
    existing_customer = frappe.db.get_value(
        "Customer",
        {"customer_name": customer_name},
        "name"
    )

    if existing_customer:
        customer = frappe.get_doc("Customer", existing_customer)

    else:
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual"
        })

        customer.insert(ignore_permissions=True)

    # =========================
    # COMPANY
    # =========================
    company = frappe.defaults.get_global_default("company")

    if not company:
        frappe.throw("Default Company not found")

    # =========================
    # CREATE SALES ORDER
    # =========================
    so = frappe.get_doc({
        "doctype": "Sales Order",
        "company": company,
        "customer": customer.name,
        "transaction_date": nowdate(),
        "delivery_date": nowdate(),
        "reserve_stock": 1,
        "custom_auction_id": auction.name,
        "custom_urgency_level": "Normal",
        "items": []
    })

    remaining_qty = awarded_qty

    # =========================
    # ONLY WAREHOUSE FROM
    # AUCTION SCHEDULE
    # बाकी सब RESULT से
    # =========================
    for row in auction_schedule.auction_details_view:

        if remaining_qty <= 0:
            break

        warehouse = row.warehouse_code

        if not warehouse:
            continue

        # =========================
        # WAREHOUSE COMPANY VALIDATION
        # =========================
        warehouse_company = frappe.db.get_value(
            "Warehouse",
            warehouse,
            "company"
        )

        if warehouse_company != company:
            continue

        # =========================
        # AVAILABLE STOCK
        # =========================
        available_qty = float(
            frappe.db.get_value(
                "Bin",
                {
                    "item_code": auction.commodity,
                    "warehouse": warehouse
                },
                "actual_qty"
            ) or 0
        )

        if available_qty <= 0:
            continue

        # =========================
        # ALLOCATE QTY
        # =========================
        allocate_qty = min(available_qty, remaining_qty)

        so.append("items", {
            "item_code": auction.commodity,
            "qty": allocate_qty,
            "rate": rate,
            "warehouse": warehouse,
            "uom": row.uom
        })

        remaining_qty -= allocate_qty

    # =========================
    # VALIDATION
    # =========================
    if not so.items:
        frappe.throw("Unable to allocate stock from warehouses")

    # =========================
    # SAVE SALES ORDER
    # =========================
    so.insert(ignore_permissions=True)

    frappe.db.commit()

    # =========================
    # REDIRECT
    # =========================
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/app/sales-order/{so.name}"

    return {
        "sales_order": so.name,
        "status": "Draft",
        "message": "Sales Order created successfully"
    }