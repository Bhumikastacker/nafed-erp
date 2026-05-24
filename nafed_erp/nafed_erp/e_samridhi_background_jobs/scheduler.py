import frappe
from nafed_erp.e_samridhi_background_jobs.api_client import (
    # create_dispatch_receipt,
    create_farmer_registration,
    fetch_with_pagination,
    create_lot_in_dispatch_receipt,
    create_warehouse_receipt,
    send_ack
)


def run_esamridhi_jobs():

    settings = frappe.get_single("Nafed Global Defaults")

    if not settings.enable_e_samridhi:
        return

    # FARMER
    if settings.enable_fetch_farmer:

        records, txn_ids = fetch_with_pagination(
            "FARMER_FETCH",
            "/api/v1/nafed-esamridhi/farmers",
            "FARMER_REGISTRATION"
        )
        create_farmer_registration(records)

        # if txn_ids:
        #     send_ack("FARMER_REGISTRATION", txn_ids)

    # CROP
    if settings.enable_commoditycrop_fetch:

        records, txn_ids = fetch_with_pagination(
            "CROP_FETCH",
            "/api/v1/nafed-esamridhi/crops",
            "CROP_DETAILS"
        )

        # if txn_ids:
        #     send_ack("CROP_DETAILS", txn_ids)

    # PROCUREMENT
    if settings.enable_lot_custom:

        records, txn_ids = fetch_with_pagination(
            "LOT_FETCH",
            "/api/v1/nafed-esamridhi/lots",
            "PROCUREMENT_DETAILS"
        )
        create_lot_in_dispatch_receipt(records) 

        # if txn_ids:
        #     send_ack("PROCUREMENT_DETAILS", txn_ids)

    # DISPATCH
    if settings.enable_lot_dispatch:

        records, txn_ids = fetch_with_pagination(
            "DISPATCH_FETCH",
            "/api/v1/nafed-esamridhi/dispatches",
            "DISPATCH_DETAILS"
        )
        # create_dispatch_receipt(records)


        # if txn_ids:
        #     send_ack("DISPATCH_DETAILS", txn_ids)

    # WHR
    if settings.enable_purchase_receiptwarehouse_ledger:

        records, txn_ids = fetch_with_pagination(
            "WHR_FETCH",
            "/api/v1/nafed-esamridhi/whr",
            "WHR_DETAILS"
        )
        create_warehouse_receipt(records)

        # if txn_ids:
        #     send_ack("WHR_DETAILS", txn_ids)

    # PAYMENT
    if settings.enable_payment_entry:

        records, txn_ids = fetch_with_pagination(
            "PAYMENT_FETCH",
            "/api/v1/nafed-esamridhi/payments",
            "PAYMENT_DETAILS"
        )

        # if txn_ids:
        #     send_ack("PAYMENT_DETAILS", txn_ids)