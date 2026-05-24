import frappe
from frappe.utils import now_datetime,get_datetime

def rate_limit(key, limit=5, window=60):
    cache_key = f"rate:{key}"
    count = frappe.cache().get_value(cache_key) or 0

    if int(count) >= limit:
        frappe.throw("Too many requests", frappe.RateLimitExceededError)

    frappe.cache().set_value(
        cache_key,
        int(count) + 1,
        expires_in_sec=window
    )
    
def validate_auth_token():
    """
    Reads token from custom header:
    auth-token: <token>
    Validates from cache and returns user
    """

    # Custom header
    auth_token = frappe.local.request.headers.get("auth-token")
    print(auth_token)
    if not auth_token:
        return None

    token_doc = frappe.db.get_value(
        "Mobile API Token",
        {
            "token": auth_token,
            "active": 1   # 🔥 IMPORTANT
        },
        ["user", "expire_in"],
        as_dict=True
    )
	
    if not token_doc:
        return None
    
    if now_datetime() > get_datetime(token_doc.expire_in):
        return None
    print(token_doc.user)
    return token_doc.user

# def validate_auth_token():
#     """
#     Reads token from:
#     Authorization: Bearer <token>
#     Validates from cache and returns user
#     """

#     auth_header = frappe.get_request_header("Authorization")

#     if not auth_header:
#         return None

#     # Expected format: "Bearer xxxxxxxxx"
#     parts = auth_header.split(" ")

#     if len(parts) != 2 or parts[0] != "Bearer":
#         return None

#     auth_token = parts[1]

#     # Fetch user from cache
#     user = frappe.cache().get_value(f"auth_token:{auth_token}")

#     if not user:
#         return None

#     return user


