import frappe,secrets
from datetime import datetime
import json,calendar
from Crypto.Cipher import AES
from frappe.utils import getdate
from frappe.model.workflow import apply_workflow
from nafed_erp.utils.crypto import decrypt_payload, encrypt_payload
from nafed_erp.utils.security import rate_limit, validate_auth_token
from frappe.utils import now_datetime, add_to_date,flt,getdate,formatdate,cstr
import re
import base64
from frappe.utils.file_manager import save_file
from frappe.utils import getdate, flt
from frappe.utils import get_url
from frappe.utils import now_datetime,get_datetime
from datetime import timedelta


@frappe.whitelist(allow_guest=True)
def jobapi_auth():
    try:
        request_data = frappe.request.get_json() or {}
        payload = request_data

        username = payload.get("username")
        password = payload.get("password")

        # 🔑 AUTHENTICATION
        print("username", username, password)
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        user = frappe.get_doc("User", frappe.session.user)
        existing_token = frappe.db.get_value(
            "Mobile API Token",
            {
                "user": frappe.session.user,
                "active": 1
            },
            ["name", "token", "expire_in"],
            as_dict=True
        )

        auth_token = None

        if existing_token:
            # 🔍 Check expiry
            
            if existing_token.expire_in and get_datetime(existing_token.expire_in) > now_datetime():

            	auth_token = existing_token.token
            else:

                frappe.db.set_value(
                    "Mobile API Token",
                    existing_token.name,
                    "active",
                    0
                )
                frappe.db.commit()

        if not auth_token:
            auth_token = frappe.generate_hash(length=40)

            expiry = now_datetime() + timedelta(hours=24)


            frappe.cache().set_value(
                f"auth_token:{auth_token}",
                frappe.session.user,
                expires_in_sec=86400
            )

            doc = frappe.new_doc("Mobile API Token")
            doc.token = auth_token
            doc.user = frappe.session.user
            doc.expire_in = expiry
            doc.active = 1
            doc.insert(ignore_permissions=True)

            frappe.db.commit()

      

        result = [{
            "authToken": auth_token,
            "expired_in": "24 Hr"
        }]

        return {
            "response": {
                "status": 200,
                "message": "Authenticate successful",
                "result": result
            }
        }

    except frappe.AuthenticationError:
        return {
            "response": {
                "status": 1001,
                "message": "Invalid username or password",
                "result": None
            }
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "job_posting_ERROR")
        return {
            "response": {
                "status": 1002,
                "message": "auth failed exception",
                "result": None
            }
        }
@frappe.whitelist(allow_guest=True)
def get_job_posting_summary():
    try:
        # ---------------- AUTH ----------------
        user = validate_auth_token()

        if not user:
            frappe.local.response["http_status_code"] = 401

            return {
                "response": {
                    "status": 401,
                    "message": "Unauthorized User",
                    "result": None
                }
            }

        payload = frappe.request.get_json() or {}

        from_date = payload.get("fromdate")
        to_date = payload.get("todate")

        conditions = ""
        values = {}

        # ---------------- DATE FILTER ----------------
        if from_date and to_date:
            conditions += """
                AND DATE(posted_on) BETWEEN %(from_date)s AND %(to_date)s
            """

            values.update({
                "from_date": from_date,
                "to_date": to_date
            })

        job_posting = frappe.db.sql(f"""
            SELECT
                *
            FROM `tabJob Opening`
            WHERE custom_publish_on_company_career_page = 1 And status = 'open'
            {conditions}
            ORDER BY posted_on ASC
        """, values, as_dict=True)

        return {
            "response": {
                "status": 200,
                "message": "Data fetched successfully",
                "result": job_posting
            }
        }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Job Posting API Error"
        )

        return {
            "response": {
                "status": 1002,
                "message": "No data available",
                "result": []
            }
        }
        
@frappe.whitelist(allow_guest=True)
def job_posting_closed():
    try:
        # ---------------- AUTH ----------------
        user = validate_auth_token()

        if not user:
            frappe.local.response["http_status_code"] = 401

            return {
                "response": {
                    "status": 401,
                    "message": "Unauthorized User",
                    "result": None
                }
            }

        payload = frappe.request.get_json() or {}

        name = payload.get("name")
        remark = payload.get("remark")
        closed_on = payload.get("closed_on")
        
        

        if not name:
            return {
                "response": {
                    "status": 400,
                    "message": "Job Posting name is required",
                    "result": []
                }
            }

        # ---------------- CHECK EXIST ----------------
        if not frappe.db.exists("Job Opening", name):
            return {
                "response": {
                    "status": 404,
                    "message": "Job Posting not found",
                    "result": []
                }
            }
        doc = frappe.get_doc("Job Opening", name)
       	print("ddddddddddddddddd", closed_on)
       	if doc.status == 'Closed':
       		return {
				    "response": {
				        "status": 200,
				        "message": "Job is already Closed",
				        "result": doc.status
				    }
				}
        if closed_on:
        	if getdate(closed_on) <= getdate(doc.posted_on):
        		return {
				    "response": {
				        "status": 400,
				        "message": "Closed On must be after Publish Date",
				        "result": []
				    }
				}
		

        doc.status='Closed'
        doc.closes_on = closed_on
        doc.closed_on = closed_on
        doc.custom_remarks = remark
        doc.save(ignore_permissions=True)
        frappe.db.commit()
       
        return {
            "response": {
                "status": 200,
                "message": "Job Posting closed successfully",

            }
        }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Job Posting Close API Error"
        )

        return {
            "response": {
                "status": 1002,
                "message": "No data available",
                "result": []
            }
        }
