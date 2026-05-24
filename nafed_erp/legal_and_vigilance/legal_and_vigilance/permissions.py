# import frappe
# from frappe.utils import today

# @frappe.whitelist()
# def has_case_access(case_id, access_type):
#     user = frappe.session.user

#     # ----------------------------------
#     # System Manager = Full Access
#     # ----------------------------------
#     if "System Manager" in frappe.get_roles(user):
#         return True

#     # ----------------------------------
#     # Case-level ACL check
#     # ----------------------------------
#     return bool(frappe.db.exists(
#         "Legal Case Assignment",
#         {
#             "case_id": case_id,
#             "lawyer": user,
#             "access_type": access_type,
#             "status": "Active",
#             "permission_start_date": ["<=", today()],
#             "expiry_date": [">=", today()]
#         }
#     ))
