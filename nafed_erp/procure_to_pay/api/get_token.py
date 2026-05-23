import jwt
import frappe
from datetime import datetime, timedelta
from frappe.utils import now_datetime

# ================= JWT HELPERS =================
def get_secret():
    return frappe.conf.jwt_secret_key or "your-secret-key"

def get_expiry():
    return frappe.conf.jwt_expiry_seconds or 1800  # 30 mins


def generate_token(user):
    expiry_seconds = get_expiry()

    payload = {
        "sub": user,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expiry_seconds)
    }

    token = jwt.encode(payload, get_secret(), algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token, expiry_seconds


# ================= TOKEN API =================
@frappe.whitelist(allow_guest=True)
def token():
    try:
        grant_type = frappe.form_dict.get("grant_type")
        username = frappe.form_dict.get("username")
        password = frappe.form_dict.get("password")

        if grant_type != "password":
            frappe.response["http_status_code"] = 400
            frappe.response.update({
                "error": "unsupported_grant_type"
            })
            return

        # 🔐 Authenticate user
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        user = frappe.session.user

        # 🔥 Generate JWT
        auth_token, expires_in = generate_token(user)

        issued_time = now_datetime()
        expiry_time = issued_time + timedelta(seconds=expires_in)

        frappe.response.update({
            "access_token": auth_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            ".issued": issued_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            ".expires": expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        })

        return

    except frappe.AuthenticationError:
        frappe.response["http_status_code"] = 401
        frappe.response.update({
            "error": "invalid_grant",
            "error_description": "Invalid username or password"
        })
        return

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Token API Error")
        frappe.response["http_status_code"] = 500
        frappe.response.update({
            "error": "server_error",
            "error_description": str(e)
        })
        return
