# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CaseOutcomeRecordingAndClosureProcessing(Document):
	pass

# @frappe.whitelist()
# def create_outcome_with_hearings_1(case_id, outcome_type, outcome_date, settlement_amount=0):
#     outcome = frappe.new_doc("Case Outcome Recording And  Closure Processing")
#     outcome.case_id = case_id
#     outcome.outcome_type = outcome_type
#     outcome.outcome_date = outcome_date
#     outcome.settlement_amount = settlement_amount or 0

#     hearings = frappe.get_all(
#         "Legal Case Hearing",
#         filters={"case_id": case_id},
#         fields=["name", "hearing_date", "hearing_status", "advocate"],
#         order_by="hearing_date asc"
#     )

#     for h in hearings:
#         row = outcome.append("case_hearing_details")
#         row.hearing_id = h.name
#         row.date = h.hearing_date
#         row.status = h.hearing_status
#         row.advocate = h.advocate

#     outcome.insert(ignore_permissions=True)
#     return outcome.name


# Copyright (c) 2026, CSM Technologies Pvt Ltd
# For license information, please see license.txt

@frappe.whitelist()
def create_outcome_with_hearing_1(case_id, outcome_type, other_outcome_type, outcome_date, settlement_amount=0):
    """
    Creates Case Outcome record and auto-maps all hearings
    """

    outcome = frappe.new_doc("Case Outcome Recording And  Closure Processing")
    outcome.case_id = case_id
    outcome.outcome_type = outcome_type
    outcome.other_outcome_type = other_outcome_type
    outcome.outcome_date = outcome_date
    outcome.settlement_amount = settlement_amount or 0

    hearings = frappe.get_all(
        "Legal Case Hearing",
        filters={"case_id": case_id},
        fields=[
            "name",
            "hearing_date",
            "hearing_status",
            "advocate"
        ],
        order_by="hearing_date asc"
    )

    for h in hearings:
        row = outcome.append("case_hearing_details")
        row.hearing_id = h.name
        row.date = h.hearing_date
        row.status = h.hearing_status
        row.advocate = h.advocate

    outcome.insert(ignore_permissions=True)
    frappe.db.commit()

    return outcome.name

