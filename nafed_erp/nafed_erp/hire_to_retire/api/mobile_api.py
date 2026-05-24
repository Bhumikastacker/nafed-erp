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
def dev_encrypt():
	"""
	Encrypt any plain JSON payload (DEV ONLY)
	"""
	from nafed_erp.utils.crypto import encrypt_payload

	payload = frappe.request.get_json()
	encrypted = encrypt_payload(payload)

	return {
		"response": encrypted
	}

@frappe.whitelist(allow_guest=True)
def debugDecrypt():
	"""
	DEBUG API – ONLY FOR DEVELOPMENT
	Decrypts encrypted request/response and returns plain JSON
	REMOVE IN PRODUCTION
	"""

	from nafed_erp.utils.crypto import decrypt_payload

	api_key = frappe.get_request_header("api-key")
	if api_key != frappe.conf.mobile_api_key:
		frappe.throw("Unauthorized", frappe.AuthenticationError)

	try:
		request_data = frappe.request.get_json() or {}
		encrypted = request_data.get("response") or request_data.get("request")

		if not encrypted:
			frappe.response.update({
				"status": 1002,
				"message": "Encrypted data not provided",
				"result": None
			})
			return

		decrypted = decrypt_payload(encrypted)

		frappe.response.update(decrypted)


	except Exception:
		frappe.log_error(frappe.get_traceback(), "debugDecrypt_ERROR")
		frappe.response.update({
			"status": 1002,
			"message": "Unable to decrypt data",
			"result": None
		})


@frappe.whitelist(allow_guest=True)
def encryptPayload():
	"""
	Encrypt plain JSON payload for mobile APIs
	DEV / POSTMAN USE ONLY
	"""

	from nafed_erp.utils.crypto import encrypt_payload

	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.throw("Unauthorized", frappe.AuthenticationError)

		request_data = frappe.request.get_json()
		if not request_data:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "No data to encrypt",
					"result": None
				})
			}

		encrypted = encrypt_payload(request_data)

		return {
			"response": encrypted
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "encryptPayload_ERROR")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "Encryption failed",
				"result": None
			})
		}


@frappe.whitelist(allow_guest=True)
def mobile_login():
    """
    Mobile Login API (Encrypted Request & Response with Token Management)
    """

    import frappe
    from datetime import timedelta
    from frappe.utils import now_datetime
    from nafed_erp.utils.crypto import encrypt_payload, decrypt_payload

    try:
        # 🔐 API KEY VALIDATION
        api_key = frappe.get_request_header("api-key")

        if api_key != frappe.conf.mobile_api_key:
            return {
                "response": encrypt_payload({
                    "status": 401,
                    "message": "Unauthorized",
                    "result": None
                })
            }

        # 🔓 DECRYPT REQUEST
        request_data = frappe.request.get_json() or {}
        encrypted_payload = request_data.get("request")

        if not encrypted_payload:
            return {
                "response": encrypt_payload({
                    "status": 1002,
                    "message": "No request data",
                    "result": None
                })
            }

        payload = decrypt_payload(encrypted_payload)

        username = payload.get("userName")
        password = payload.get("password")

        # 🔑 AUTHENTICATION
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        user = frappe.get_doc("User", frappe.session.user)

        # ============================================================
        # 🔁 TOKEN MANAGEMENT (Reuse / Expire / Regenerate)
        # ============================================================

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
            	print("ssssssssssssssssssssssssssssssssssss")
            	auth_token = existing_token.token
            else:
                # ❌ Expired → deactivate
                frappe.db.set_value(
                    "Mobile API Token",
                    existing_token.name,
                    "active",
                    0
                )
                frappe.db.commit()

        # 🔑 Generate new token if needed
        if not auth_token:
            auth_token = frappe.generate_hash(length=40)

            expiry = now_datetime() + timedelta(hours=24)

            # Cache token
            frappe.cache().set_value(
                f"auth_token:{auth_token}",
                frappe.session.user,
                expires_in_sec=86400
            )

            # Save token in DB
            doc = frappe.new_doc("Mobile API Token")
            doc.token = auth_token
            doc.user = frappe.session.user
            doc.expire_in = expiry
            doc.active = 1
            doc.insert(ignore_permissions=True)

            frappe.db.commit()

        # ============================================================
        # 👤 EMPLOYEE DETAILS
        # ============================================================

        employee = frappe.db.get_value(
            "Employee",
            {"user_id": user.name},
            [
                "employee_number",
                "employee_name",
                "cell_number",
                "personal_email",
                "date_of_joining",
                "designation",
                "department",
                "branch",
                "current_address"
            ],
            as_dict=True
        )

        role_id = 1 if "System Manager" in frappe.get_roles(user.name) else 2

        result = [{
            "userId": employee.employee_number if employee else user.name,
            "roleId": role_id,
            "fullName": employee.employee_name if employee else user.full_name,
            "mobileNo": employee.cell_number if employee else "",
            "emailId": employee.personal_email if employee else user.email,
            "dateOfJoining": employee.date_of_joining.strftime("%d-%b-%Y")
                if employee and employee.date_of_joining else "",
            "designation": employee.designation if employee else "",
            "division": employee.department if employee else "",
            "ofcLocation": employee.branch if employee else "",
            "address": employee.current_address if employee else "",
            "raName": "",
            "raId": "",
            "authToken": auth_token,
            "expired_in": "24 Hr"
        }]

        return {
            "response": encrypt_payload({
                "status": 200,
                "message": "Login successful",
                "result": result
            })
        }

    except frappe.AuthenticationError:
        return {
            "response": encrypt_payload({
                "status": 1001,
                "message": "Invalid username or password",
                "result": None
            })
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "mobile_login_ERROR")
        return {
            "response": encrypt_payload({
                "status": 1002,
                "message": "Login failed exception",
                "result": None
            })
        }

# 2) Applied Leave Summary
@frappe.whitelist(allow_guest=True)
def get_leave_requests_summary():
	try:
		# ---------------- API KEY ----------------
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		print("aaaaaaaaaaaaaaaaaaaaa", user)
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": None
				})
			}
			
			
		request_data = frappe.request.get_json()
	  
		encrypted_payload = request_data.get("request")
		payload = decrypt_payload(encrypted_payload)

	   
		if not encrypted_payload:
		   
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		# ---------------- INPUT PARAMS ----------------
		
		user_id = payload.get('userId')
		year = int(payload.get("year") or datetime.now().year)
		month = int(payload.get("month") or datetime.now().month)

		# ---------------- USER → EMPLOYEE ----------------
		print(user_id, year, month)
		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			[
				"name",
				"employee_name",
				"personal_email",
				"cell_number",
				"designation",
				"department",
				"branch"
			],
			as_dict=True
		)
		print(employee)
		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Employee does not exist",
					"result": []
				})
			}
		# ---------------- DATE RANGE ----------------
		start_date = datetime(year, month, 1)
		last_day = calendar.monthrange(year, month)[1]
		end_date = datetime(year, month, last_day)

		# ---------------- LEAVE QUERY ----------------
		leaves = frappe.db.sql("""
			SELECT
				name,
				employee_name,
				leave_type,
				description,
				from_date,
				to_date,
				total_leave_days,
				status,
				leave_approver,
				modified
			FROM `tabLeave Application`
			WHERE employee = %s
			  AND from_date BETWEEN %s AND %s
			ORDER BY from_date ASC
		""", (employee.name, start_date, end_date), as_dict=True)

		result = []
		for leave in leaves:
			result.append({
				"leaveID": leave.name,
				"employee": leave.employee_name,
				"appliedBy": "1",
				"leaveType": leave.leave_type,
				"reason": leave.description or "",
				"startDate": leave.from_date.strftime("%d-%m-%Y"),
				"endDate": leave.to_date.strftime("%d-%m-%Y"),
				"requestedDays": str(leave.total_leave_days),
				"status": leave.status,
				"pendingAt": leave.leave_approver if leave.status == "Leave Requested" else "",
				"actionTakenOn": leave.modified.strftime("%d-%m-%Y"),
				"remarks": leave.custom_remarks or ""
			})
		
		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Data fetched successfully",
				"result": result
			})
		}
	


	except Exception:
		frappe.log_error(frappe.get_traceback(), "Leave API (Encrypted)")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		}


#3
@frappe.whitelist(allow_guest=True)
def get_leaves_to_approve():
	try:
		# ---------------- API KEY ----------------
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Invalid API Key",
					"result": []
				})
			}

		# ---------------- AUTH TOKEN ----------------
		auth_token = frappe.get_request_header("Auth-Token")
		if not auth_token:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Auth token missing",
					"result": []
				})
			}

		# ---------------- REQUEST PAYLOAD ----------------
		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")
		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1004,
					"message": "Encrypted payload missing",
					"result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)
		user_email = payload.get("userId")  # Approver's email
		year = int(payload.get("year") or datetime.now().year)
		month = int(payload.get("month") or datetime.now().month)

		# ---------------- VALIDATE APPROVER ----------------
		approver_exists = frappe.db.exists("User", {"email": user_email})
		if not approver_exists:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "Approver not found",
					"result": []
				})
			}

		# ---------------- DATE RANGE ----------------
		start_date = datetime(year, month, 1)
		last_day = calendar.monthrange(year, month)[1]
		end_date = datetime(year, month, last_day)
		status_map = {
			"Rejected": "3",
			"Approved": "2",
			"Leave Requested": "1",
			"Cancelled": "4"
		}
		# ---------------- LEAVES QUERY ----------------
		leaves = frappe.db.sql("""
			SELECT
				name,
				employee,
				employee_name,
				leave_type,
				description,
				from_date,
				to_date,
				total_leave_days,
				status,
				leave_approver,
				custom_remarks,
				modified
			FROM `tabLeave Application`
			WHERE leave_approver = %s
			  AND from_date BETWEEN %s AND %s
			ORDER BY from_date ASC
		""", (user_email, start_date, end_date), as_dict=True)

		# ---------------- FORMAT RESULT ----------------
		result = []
		print(leaves)
		for lv in leaves:
			print("sssssssssssssss", lv.custom_remarks,lv)
			result.append({
				"employee": lv.employee_name,
				"employeeID": lv.employee,
				"appliedBy": "2",  # 2 = Applied to approver
				"leaveId": lv.name,
				"leaveType": lv.leave_type,
				"reason": lv.description or "",
				"startDate": lv.from_date.strftime("%d-%m-%Y"),
				"endDate": lv.to_date.strftime("%d-%m-%Y"),
				"requestedDays": str((lv.total_leave_days)),
				"status":status_map.get(lv.status, "1"),
				"pendingAt": lv.employee_name if lv.status == "Leave Requested" else "",
				"actionTakenBy": get_action_user(lv),
				"actionTakenOn": lv.modified.strftime("%d-%m-%Y"),
				"remarks": lv.custom_remarks
			})


		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Success",
				"result": result
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Leave API (Encrypted)")
		return {
			"response": encrypt_payload({
				"status": 500,
				"message": "Internal Server Error",
				"result": []
			})
		}


# ---------------- HELPER ----------------
def get_action_user(leave):
	if leave.status == "Approved":
		return f"Approved by {leave.leave_approver}"
	elif leave.status == "Rejected":
		return f"Rejected by {leave.leave_approver}"
	return ""


@frappe.whitelist(allow_guest=True)
def empLeaveDetails():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		   
		
	
		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")
		
		if not encrypted_payload:

			return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		}
			
		payload = decrypt_payload(encrypted_payload)
		
		leaveId = payload.get("leaveId")
		employeeID = payload.get("employeeID")
		userId = payload.get("userId")

		if not frappe.db.exists("Leave Application", leaveId):
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}
			

		leave = frappe.get_doc("Leave Application", leaveId)
		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": employeeID},
			[
				"name",
				"employee_name",
				"personal_email",
				"cell_number",
				"designation",
				"department",
				"branch"
			],
			as_dict=True
		)
		print("ssssssssssssssssssssss")
		total_allocated = frappe.db.get_value("Leave Allocation", 
			{"employee": employee.name, "leave_type": leave.leave_type, "docstatus": 1}, 
			"total_leaves_allocated") or 0
		
		balance_before = flt(leave.leave_balance)  
		applied_days = flt(leave.total_leave_days)
		remaining = balance_before - applied_days

		result = ({
			"empName": employee.employee_name,
			"employeeID": employee.name,
			"leaveID": leave.name,
			"empCompany": employee.company,
			"leaveTypeId": leave.leave_type,
			"AppliedBy": leave.owner,
			"totalLeave": str(total_allocated),
			"applied": str(applied_days),
			"granted": str(applied_days) if leave.status == "Approved" else "0",
			"remaining": str(remaining),
			"leaveFrom": formatdate(leave.from_date, "dd-MMM-yyyy"), 
			"leaveTo": formatdate(leave.to_date, "dd-MMM-yyyy"),     
			"duration": str(applied_days),
			"reason": (leave.description or "").strip()          
		})
		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Data fetched successfully",
				"result": result
			})
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "empLeaveDetails API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		}


# 5) Leave Reject / Approve
@frappe.whitelist(allow_guest=True)
def takeLeaveAction():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)

		leave_id = payload.get("leaveId")
		user_id = payload.get("userId")          
		employee_id = payload.get("employeeID") 
		action = str(payload.get("action"))
		remarks = payload.get("remarks")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": employee_id},
			["name"],
			as_dict=True
		)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Employee does not exist",
					"result": []
				})
			}

		if not frappe.db.exists("Leave Application", leave_id):
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "Leave ID not found",
					"result": []
				})
			}

		doc = frappe.get_doc("Leave Application", leave_id)

		if doc.docstatus != 0:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": f"Leave is already {doc.status}",
					# "result": []
				})
			}

		if action == "1":
			doc.status = "Approved"
			msg = "Leave Approved successfully"
		else:
			doc.status = "Rejected"
			msg = "Leave Rejected successfully"

		doc.custom_remarks = remarks
		doc.save(ignore_permissions=True)
		doc.submit()

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": msg,
				# "result": []
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "takeLeaveAction API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		}




# def get_action_user(leave):
#     if leave.status == "Approved":
#         return "Approved by User name"
#     elif leave.status == "Rejected":
#         return "Rejected by User name"
#     return ""


# 6 Get Leave Types
@frappe.whitelist(allow_guest=True)
def GetLeaveTypes():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)

		employeeId = payload.get("employeeId")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": employeeId},
			"name"
		)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "Employee does not exist",
					"result": []
				})
			}


		all_leave_types = frappe.get_all(
			"Leave Type",
			fields=["name", "leave_type_name", "is_lwp"]
		)

		if not all_leave_types:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		allocations = frappe.get_all(
			"Leave Allocation",
			filters={
				"employee": employee,
				"docstatus": 1
			},
			fields=["leave_type", "total_leaves_allocated"]
		)

		alloc_map = {a.leave_type: a.total_leaves_allocated for a in allocations}

		result = []
		for lt in all_leave_types:
			result.append({
				"leaveTypeId": lt.name,
				"leaveTypeName": lt.leave_type_name,
				"maxAllowed": int(alloc_map.get(lt.name, 0)),
				"isPaid": False if lt.is_lwp else True
			})

		if not result:
			return {
				"response": encrypt_payload({
					"status": 200,
					"message": "NO data available",
					"result": []
				})
			}

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Data fetched successfully",
				"result": result
			})
		}


	except Exception:
		frappe.log_error(frappe.get_traceback(), "GetLeaveTypes API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		} 


# 7) 
@frappe.whitelist(allow_guest=True)
def GetLeaveBalance():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)

		employeeId = payload.get("employeeId")
		financialYear = payload.get("financialYear")
		leaveTypeId = payload.get("leaveTypeId")


		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": employeeId},
			"name"
		)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "Employee does not exist",
					"result": []
				})
			}

		try:
			years = financialYear.split("-")
			start_date = f"{years[0]}-04-01"
			end_yr = years[1] if len(years[1]) == 4 else f"20{years[1]}"
			end_date = f"{end_yr}-03-31"
		except Exception:
			start_date = f"{datetime.now().year}-01-01"
			end_date = f"{datetime.now().year}-12-31"

		alloted_leave = frappe.db.get_value(
			"Leave Allocation",
			{
				"employee": employee,
				"leave_type": leaveTypeId,
				"from_date": ["<=", end_date],
				"to_date": [">=", start_date],
				"docstatus": 1
			},
			"total_leaves_allocated"
		) or 0

		if alloted_leave == 0:
			result = {
				 "status": 200,
				"result": result,
				"message": "No data available"
			}
			return encrypt_payload(result)

		applied = frappe.db.sql("""
			SELECT SUM(total_leave_days)
			FROM `tabLeave Application`
			WHERE employee = %s
			  AND leave_type = %s
			  AND status IN ('Open', 'Leave Requested')
			  AND from_date >= %s AND to_date <= %s
		""", (employee, leaveTypeId, start_date, end_date))[0][0] or 0

		granted = frappe.db.sql("""
			SELECT SUM(total_leave_days)
			FROM `tabLeave Application`
			WHERE employee = %s
			  AND leave_type = %s
			  AND status = 'Approved'
			  AND docstatus = 1
			  AND from_date >= %s AND to_date <= %s
		""", (employee, leaveTypeId, start_date, end_date))[0][0] or 0

		result = {
			"leaveTypeId": leaveTypeId,
			"leaveTypeName": leaveTypeId,
			"allotedLeave": str(alloted_leave),
			"applied": str(applied),
			"granted": str(granted),
			"remaining": str(flt(alloted_leave) - flt(granted))
		}
	   

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Data fetched successfully",
				"result": result
			})
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "GetLeaveBalance API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": []
			})
		}


# 9) Update Profile 
@frappe.whitelist(allow_guest=True)
def requestProfileUpdate():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized"
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Unable sent profile update request"
				})
			}

		payload = decrypt_payload(encrypted_payload)

		user_id = str(payload.get("userId") or "").strip()
		mob_no = str(payload.get("mobNo") or "").strip()
		email_id = str(payload.get("emailId") or "").strip()
		new_emergency_contact_name = str(payload.get("new_emergency_contact_name") or "").strip()
		new_emergency_phone = str(payload.get("new_emergency_phone") or "").strip()
		new_relation = str(payload.get("new_relation") or "").strip()
		new_present_city = str(payload.get("new_present_city") or "").strip()
		new_present_pin = str(payload.get("new_present_pin") or "").strip()
		new_present_state = str(payload.get("new_present_state") or "").strip()
		new_present_street = str(payload.get("new_present_street") or "").strip()
		new_present_telephone_number = payload.get("new_present_telephone_number")
		new_current_address_is = str(payload.get("new_current_address_is") or "").strip()
		new_current_address = str(payload.get("new_current_address") or "").strip()
		new_permanent_city = str(payload.get("new_permanent_city") or "").strip()
		new_permanent_pin = str(payload.get("new_permanent_pin") or "").strip()
		new_permanent_state = str(payload.get("new_permanent_state") or "").strip()
		custom_permanent_street = str(payload.get("custom_permanent_street") or "").strip()
		new_permanent_street = str(payload.get("new_permanent_street") or "").strip()
		current_address = str(payload.get("current_address") or "").strip()
		new_permanent_telephone_number = payload.get("new_permanent_telephone_number")
		old_permanent_address = str(payload.get("old_permanent_address") or "").strip()
		new_permanent_address = str(payload.get("new_permanent_address") or "").strip()
		new_permanent_address_is = str(payload.get("new_permanent_address_is") or "").strip()

		if not all([user_id, mob_no, email_id]):
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Unable sent profile update request"
				})
			}

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			"name"
		)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "User does not exist"
				})
			}

		if not re.match(r"^\d{10}$", mob_no):
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Unable sent profile update request"
				})
			}

		if not re.match(r"[^@]+@[^@]+\.[^@]+", email_id):
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "Unable sent profile update request"
				})
			}
			
		if new_emergency_contact_name:

			if not re.match(r'^[A-Za-z\s]+$', new_emergency_contact_name):
				return {
					"response": encrypt_payload({
						"status": 1001, 
						"message": "Only alphabets are allowed in Emergency Contact Name", 
						"result": None
					})
				}
		        

		if new_emergency_phone:
			if not re.match(r'^[A-Za-z\s]+$', new_emergency_phone):
				return {
					"response": encrypt_payload({
						"status": 1001, 
						"message": "Only alphabets are allowed in Relation ", 
						"result": None
					})
				}
	        

		if not re.match(r'^(\+91)?[6-9]\d{9}$', new_relation):
			return {
					"response": encrypt_payload({
						"status": 1001, 
						"message": "Invalid Emergency Phone", 
						"result": None
					})
				}	
		print("jjjjjjjjj",new_present_city)
		doc = frappe.new_doc("Employee Update Request")
		doc.employee = employee
		doc.new_mobile = mob_no
		doc.new_email = email_id
		doc.new_present_city = new_present_city
		doc.new_present_pin = new_present_pin
		doc.new_present_telephone_number = new_present_telephone_number
		doc.new_present_state = new_present_state
		doc.new_present_street = new_present_street
		doc.current_address = current_address
		doc.new_current_address = new_current_address
		doc.new_current_address_is = new_current_address_is
		#doc.custom_same_as_present_address = new_present_city
		doc.new_permanent_city = new_permanent_city
		doc.new_permanent_pin = new_permanent_pin
		doc.new_permanent_telephone_number = new_permanent_telephone_number
		doc.new_permanent_state = new_permanent_state
		doc.new_permanent_state = new_permanent_state
		doc.new_permanent_address = new_permanent_address
		doc.new_permanent_address_is = new_permanent_address_is
		doc.new_permanent_street =new_permanent_street
		
		doc.new_emergency_contact_name = new_emergency_contact_name
		doc.new_emergency_phone = new_emergency_phone
		doc.new_relation = new_relation
		frappe.set_user("Administrator")


		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		from frappe.model.workflow import get_transitions

		transitions = get_transitions(doc)
		print("ssssssssssss",transitions)
		if transitions:
			action = transitions[0].get("action")
			apply_workflow(doc, action)

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Profile update request sent successfully",
				"result":doc.name
			})
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Profile Update API Error")
		return {
			"response": encrypt_payload({
				"status": 500,
				"message": str(e)
			})
		}


# 10)View Profile
@frappe.whitelist(allow_guest=True)
def viewProfile():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized"
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		
		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")
		
		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1003, 
					"message": "Encrypted payload missing", 
					"result": None
				})
			}
			
		payload = decrypt_payload(encrypted_payload)
		user_id = payload.get("userId")

		if not user_id:
			return {
				"response": encrypt_payload({
					"status": 1002, 
					"message": "User ID is required", 
					"result": None
				})
			}

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			"name"
				)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1001, 
					"message": "User does not exist", 
					"result": None
				})
			}

		emp = frappe.get_doc("Employee", employee)


		academic_list = []
		professional_list = []
		if hasattr(emp, 'education') and emp.education:
			for edu in emp.education:
				if edu.get("custom_personal_qualification"):
					academic_list.append(cstr(edu.get("custom_personal_qualification")))
				if edu.get("custom_professional_qualification"):
					professional_list.append(cstr(edu.get("custom_professional_qualification")))
		
		academic_str = ", ".join(academic_list)
		professional_str = ", ".join(professional_list)

		increment_month_str = ""
		#if hasattr(emp, 'custom_increment_record') and emp.custom_increment_record:
		#	last_record = emp.custom_increment_record[-1]
		#	inc_date = last_record.get("increment_date") or last_record.get("date")
		#	if inc_date:
		#		increment_month_str = formatdate(inc_date, "MMMM")

		nominee_name = cstr(emp.custom_gisnominee) 
		
		if not nominee_name and hasattr(emp, 'custom_dependent') and emp.custom_dependent:
			for dept in emp.custom_dependent:
				current_name = dept.get("dependent_name") or dept.get("name_of_dependent") or dept.get("name")
				
				is_nominee = dept.get("pf_nominee") or dept.get("is_nominee")
				
				if current_name:
					if is_nominee:
						nominee_name = current_name
						break 
					elif not nominee_name:
						nominee_name = current_name

		father_husband_name = cstr(emp.middle_name) if emp.middle_name else cstr(emp.custom_hb_name)
		
		

		

		result = {
			"personalDetails": {
				"fatherOrHusbandName": father_husband_name,
				"gender": cstr(emp.gender),
				"dob": formatdate(emp.date_of_birth, "dd-MMM-yyyy") if emp.date_of_birth else "",
				"bloodGroup": cstr(emp.blood_group),
				"category": cstr(emp.custom_social_category) or cstr(emp.custom_employee_category),
				"aadharNo": cstr(emp.custom_aadhar_number),
				"panNo": cstr(emp.pan_number),
				"professionalQualification": professional_str, 
				"academicQualification": academic_str,
				"person_to_be_contacted": emp.person_to_be_contacted,
				"emergency_phone_number": emp.emergency_phone_number,
				"relation": emp.relation
			},
			"reportingDetails": [
				{
					"name": cstr(emp.custom_reports_to_employee_name),
					"Id": cstr(emp.reports_to),
					"reportingType": "Reporting 1 (Leave)"
				}
			],
			"addressDetails": {
				"presentAddress": {
					"address": cstr(emp.current_address),
					"state": cstr(emp.custom_present_state),
					"street":cstr(emp.custom_present_street),
					"city": cstr(emp.custom_pcity),
					"pin": cstr(emp.custom_ppin),
					"custom_telph": cstr(emp.custom_telph),
					"current_accommodation_type": cstr(emp.current_accommodation_type)
				},
				"permanentAddress": {
					"address": cstr(emp.permanent_address),
					"state": cstr(emp.custom_permanent_state),
					"city": cstr(emp.custom_pmtcity),
					"pin": cstr(emp.custom_pmtpin),
					"street":cstr(emp.custom_permanent_street),
					"custom_telph": cstr(emp.custom_permanent_telephone_number),
					"current_accommodation_type": cstr(emp.permanent_accommodation_type)
				}
			},
			"jobDetails": {
				"branch": cstr(emp.branch),
				"department": cstr(emp.department),
				"designation": cstr(emp.designation),
				"section": cstr(emp.custom_section),
				"fileNo": cstr(emp.employee_number),
				"idMark": cstr(emp.custom_id_mark)
			},
			"nomineeDetails": {
				"nominee": nominee_name
			},
			"salaryDetails": {
				"payScale": cstr(emp.custom_pay_band),
				"incrementMonth": increment_month_str,
				"seniorityCode": cstr(emp.custom_sen_code) or cstr(emp.custom_cadre_code),
				"passportNo": cstr(emp.passport_number)
			},
			"pfDetails": {
				"pfNo": cstr(emp.provident_fund_account),
				"epfoMemberId": cstr(emp.custom_epfo_member_id),
				"uanNo": cstr(emp.custom_uan_number),
				"dateOfJoining": formatdate(emp.date_of_joining, "dd-MMM-yyyy") if emp.date_of_joining else ""
			}
		}

		return {
			"response": encrypt_payload({
				"status": 200, 
				"message": "Success", 
				"result": result
			})
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "View Profile API Error")
		return {
			"response": encrypt_payload({
				"status": 1002, 
				"message": f"Data processing error: {str(e)}", 
				"result": []
			})
		}

@frappe.whitelist(allow_guest=True)
def submitChildAllowance():
	try:
		api_key = frappe.get_request_header("api-key")

		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": []
				})
			}

		# ===============================
		# 2️⃣ USER TOKEN VALIDATION
		# ===============================
		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized users",
					"result": None
				})
			}

		payload = frappe.form_dict
		if not payload:
			return {"response": encrypt_payload({
				"status": 1003,
				"message": "Payload missing",
				"result": None
			})}

		emp_id = payload.get("empId")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": emp_id},
			["name", "status"],
			as_dict=True
		)

		if not employee:
			return {"response": encrypt_payload({"status": 1001, "message": "User does not exist"})}

		if employee.status != "Active":
			return {"response": encrypt_payload({"status": 1003, "message": "Employee not active"})}

		doc = frappe.new_doc("Children Allowance Declaration")
		doc.employee = employee.name
		doc.date_of_application = getdate(payload.get("dateOfApplication"))
		doc.order_no = payload.get("orderNo")
		doc.original_receipt_no = payload.get("originalReceiptNo")
		doc.remarks = payload.get("remark")
		doc.salary_component = "Children Education Allowance"
		doc.amount = flt(payload.get("amount")) or 0

		# Handle child details
		child_details = payload.get("childDetails") or []

		if isinstance(child_details, str):
			try:
				child_details = json.loads(child_details)
			except:
				child_details = []

		for child in child_details:
			dob = child.get("dateOfBirth")
			doc.append("children_details", {
				"child_name": child.get("childName"),
				"date_of_birth": getdate(dob) if dob else None,
				"school_name": child.get("schoolUniversity"),
				"class_studying_in": child.get("class")
			})

		doc.insert(ignore_permissions=True)
		
		files = frappe.request.files

		if files:

			# Single receipt
			receipt = files.get("receipt")

			if receipt and receipt.filename:

				file_doc = save_file(
					receipt.filename,
					receipt.stream.read(),
					doc.doctype,
					doc.name,
					is_private=0
				)

				doc.upload_receiptno = file_doc.file_url

			# Multiple documents
			receipt_docs = files.getlist("receiptDocs")

			if receipt_docs:
				for f in receipt_docs:

					if not f or not f.filename:
						continue

					save_file(
						f.filename,
						f.stream.read(),
						doc.doctype,
						doc.name,
						is_private=0
					)

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {"response": encrypt_payload({
			"status": 200,
			"message": "Success",
			"result": []
		})}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Child Allowance API Error")
		return {"response": encrypt_payload({
			"status": 1002,
			"message": f"Unable to submit: {str(e)}"
		})}


@frappe.whitelist(allow_guest=True)
def SubmitLeaveRequest():
	try:
		# ===============================
		# 1️⃣ API KEY VALIDATION
		# ===============================
		api_key = frappe.get_request_header("api-key")

		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": []
				})
			}

		# ===============================
		# 2️⃣ USER TOKEN VALIDATION
		# ===============================
		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		# ===============================
		# 3️⃣ REQUEST DATA (JSON OR FORM)
		# ===============================
		payload =frappe.form_dict
		
		


		if not payload:
			return {"response": encrypt_payload({
				"status": 1001,
				"message": "payload missing"
			})}



		user_id = payload.get("userId")

		# ===============================
		# 4️⃣ EMPLOYEE FETCH
		# ===============================
		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			["name", "reports_to", "company", "department"],
			as_dict=True
		)
		print("sssssssssssssssss", employee, user_id,payload)
		if not employee:
			return {"response": encrypt_payload({
				"status": 1003,
				"message": "User does not exist"
			})}
			
		

		# ===============================
		# 5️⃣ DATE FORMAT CONVERSION
		# ===============================
		half_day_date = ""
		try:
			start_date = datetime.strptime(
				payload.get("startDate"), "%d-%m-%Y"
			).strftime("%Y-%m-%d")
			if payload.get("halfdayDate"):
				half_day_date = datetime.strptime(
				payload.get("halfdayDate"), "%d-%m-%Y"
			).strftime("%Y-%m-%d")

			end_date = datetime.strptime(
				payload.get("endDate"), "%d-%m-%Y"
			).strftime("%Y-%m-%d")

		except Exception:
			return {"response": encrypt_payload({
				"status": 1001,
				"message": "Invalid Date Format. Use DD-MM-YYYY"
			})}
			
			
		existing_leave = frappe.get_all(
			"Leave Application",
			filters={
			"employee": employee.name,
			"status": ["in", ['Approved', 'Leave Requested']],
			"from_date": ["<=", end_date],
			"to_date": [">=", start_date],
			},
			fields=["name"]
		)
		if existing_leave:

			return {"response": encrypt_payload({
				"status": 1004,
				"message": "Leave already applied for selected dates",
				"result": []
			})}
				
		
		existing_leave = frappe.db.sql("""
			SELECT name
			FROM `tabLeave Application`
			WHERE employee = %s
			AND docstatus in ('Approved', 'Leave Requested')
			AND (
				(%s BETWEEN from_date AND to_date)
				OR (%s BETWEEN from_date AND to_date)
				OR (from_date BETWEEN %s AND %s)
			)
		""", (
			employee.name,
			start_date,
			end_date,
			start_date,
			end_date
		), as_dict=True)
		print("ddddddddddddddddd", existing_leave)
		if existing_leave:

			return {"response": encrypt_payload({
				"status": 1004,
				"message": "Leave already applied for selected dates",
				"result": []
			})}
		
		# ===============================
		# 6️⃣ CREATE LEAVE APPLICATION
		# ===============================
		leave_app = frappe.new_doc("Leave Application")
		leave_app.employee = employee.name
		leave_app.leave_type = payload.get("leaveTypeId")
		leave_app.from_date = start_date
		leave_app.to_date = end_date
		leave_app.description = payload.get("reason")
		leave_app.posting_date = getdate()
		leave_app.company = employee.company
		leave_app.department = employee.department

		# Leave Approver
		#if employee.reports_to:
		#	leave_app.leave_approver = frappe.db.get_value(
		#		"Employee", employee.reports_to, "user_id"
		#	)

		# ===============================
		# 7️⃣ HALF DAY LOGIC
		# ===============================
		if str(payload.get("leaveFromType")) == "1" and half_day_date:
			leave_app.half_day = 1
			leave_app.half_day_date = half_day_date

			leave_app.custom_half_day_type = (
				"First Half"
				if str(payload.get("fromHalfDayType")) == "1"
				else "Second Half"
			)

		# ===============================
		# 8️⃣ INSERT DOCUMENT
		# ===============================
		try:
			leave_app.insert(ignore_permissions=True)

		except frappe.exceptions.ValidationError as ve:
			error_msg = str(ve).lower()

			if any(word in error_msg for word in ["balance", "insufficient", "not enough"]):
				return {"response": encrypt_payload({
					"status": 1002,
					"message": "Insufficient leave balance"
				})}

			return {"response": encrypt_payload({
				"status": 1001,
				"message": str(ve)
			})}

		# ===============================
		# 9️⃣ FILE ATTACHMENT (OPTIONAL)
		# ===============================
		file_base64 = payload.get("fileBase64")
		file_name = payload.get("doc") or payload.get("fileName")

		if file_base64 and file_name:
			try:
				# Remove base64 header if present
				if "," in file_base64:
					file_base64 = file_base64.split(",")[1]

				decoded_file = base64.b64decode(file_base64)

				save_file(
					file_name,
					decoded_file,
					"Leave Application",
					leave_app.name,
					is_private=0
				)

			except Exception:
				frappe.log_error(
					frappe.get_traceback(),
					"Leave API Attachment Error"
				)

		# ===============================
		# 🔟 SUCCESS RESPONSE
		# ===============================
		return {"response": encrypt_payload({
			"status": 200,
			"message": "Leave Request Applied Successfully",
			"leave_id": leave_app.name
		})}

	# ===============================
	# ❌ GLOBAL ERROR HANDLER
	# ===============================
	except Exception as e:
		frappe.log_error(
			frappe.get_traceback(),
			"SubmitLeaveRequest API Error"
		)

		return {"response": encrypt_payload({
			"status": 1001,
			"message": f"Unable to apply leave: {str(e)}"
		})}

# 11) Child Allowance Declaration
@frappe.whitelist(allow_guest=True)
def childAllowance():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"Result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		hr_setting_amt = frappe.db.get_single_value(
			"HR Settings",
			"children_allowance_amount"
		)
		print("dddddddddddddddd",hr_setting_amt)
		if not hr_setting_amt:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO setting Amount available",
					"Result": None
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"Result": None
				})
			}

		payload = decrypt_payload(encrypted_payload)
		user_id = payload.get("userId")

		employee_master = frappe.db.get_value(
			"Employee",
			{"employee_number": str(user_id)},
			["name", "employee_name", "designation", "company"],
			as_dict=True
		)

		if not employee_master:
			return {"response": encrypt_payload({"status": 1001, "message": "User does not exist", "Result": None})}

		allowance_record = frappe.db.get_value(
			"Children Allowance Declaration",
			{"employee": employee_master.name},  
			["salary_component", "amount", "status", "workflow_state"],
			as_dict=True,
			order_by="creation desc"
		)


		if not allowance_record:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"Result": None
				})
			}

		final_status = (
			allowance_record.workflow_state
			or allowance_record.status
			or "draft"
		)

		result_data = {
			"empId": user_id,
			"empName": employee_master.employee_name,
			"desg": employee_master.designation,
			"company": employee_master.company,
			"salaryComponent": allowance_record.salary_component or "Children Education Allowance",
			"amount": str(int(flt(hr_setting_amt))),
			"status": final_status.lower()
		}

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Success",
				"Result": result_data
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "childAllowance API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"Result": []
			})
		}

# 13) View Child Allowance
@frappe.whitelist(allow_guest=True)
def viewChildAllowance():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"Result": []
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"Result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)
		user_id = payload.get("userId")

		emp_master = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			["name", "employee_name", "designation", "company"],
			as_dict=True
		)


		if not emp_master:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "User does not exist",
					"Result": []
				})
			}

		allowance_record = frappe.get_all(
			"Children Allowance Declaration",
			filters={"employee": emp_master.name},
			fields=[
				"name", "employee", "employee_name", "designation", "company",
				"salary_component", "amount", "status", "workflow_state",
				"date_of_application", "order_no",
				"original_receipt_no", "upload_receiptno", "remarks"
			],
			order_by="creation desc",
			limit=1
		)

		if not allowance_record:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"Result": []
				})
			}

		doc = allowance_record[0]

		child_records = frappe.get_all(
			"Children Details",
			filters={"parent": doc.name},
			fields=[
				"child_name", "date_of_birth",
				"school_name", "class_studying_in"
			]
		)

		child_details_list = []
		for child in child_records:
			child_details_list.append({
				"childName": child.child_name,
				"dateOfBirth": child.date_of_birth.strftime("%d-%b-%Y") if child.date_of_birth else "",
				"school/university": child.school_name or "",
				"class": child.class_studying_in or ""
			})

		final_status = doc.workflow_state or doc.status or "draft"
		attached_files = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": "Children Allowance Declaration",
				"attached_to_name": doc.name
			},
			fields=["file_name", "file_url"]
		)


		result_list = []
		for file in attached_files:
		  
			print("aaaaaaaaaaaaaaaaaaaaaaaa", attached_files)
			result_list.append({
				"title": file.file_name,
				"docUrl": get_url(file.file_url or "")
			})

		result_data = {
			"empId": doc.employee,
			"empName": doc.employee_name or emp_master.employee_name,
			"desg": doc.designation or emp_master.designation,
			"company": doc.company or emp_master.company,
			"salaryComponent": doc.salary_component or "Children Education Allowance",
			"amount": str(int(flt(doc.amount))),
			"status": final_status.lower(),
			"dateOfApplication": doc.date_of_application.strftime("%d-%b-%Y") if doc.date_of_application else "",
			"orderNo": doc.order_no or "",
			"originalReceiptNo": doc.original_receipt_no or "",
			"uploadReceipt": result_list,
			"remark": doc.remarks or "",
			"childDetails": child_details_list
		}

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Success",
				"result": [result_data]
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "viewChildAllowance API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"Result": []
			})
		}

# 14) Final Settlement Document 
@frappe.whitelist(allow_guest=True)
def viewDocument():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": []
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO Payload data available",
					"result": []
				})
			}

		payload = decrypt_payload(encrypted_payload)
		user_id = payload.get("userId")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			"name"
		)

		if not employee:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "User does not exist",
					"result":[]
				})
			}

		doctype_name = "Full and Final Statement"

		settlement_record = frappe.db.get_value(
			doctype_name,
			{"employee": employee},
			"name",
			order_by="creation desc"
		)

		if not settlement_record:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": None
				})
			}

		attached_files = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": doctype_name,
				"attached_to_name": settlement_record
			},
			fields=["file_name", "file_url"]
		)

		if not attached_files:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO file data available",
					"result": None
				})
			}

		result_list = []
		for file in attached_files:
		  
			print("aaaaaaaaaaaaaaaaaaaaaaaa", attached_files)
			result_list.append({
				"title": file.file_name,
				"docUrl": get_url(file.file_url or "")
			})

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Success",
				"result": result_list
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "viewDocument API Error")
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "NO data available",
				"result": None
			})
		}






@frappe.whitelist(allow_guest=True)
def get_branch_list():
	try:
		# Validate API Key
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		# Validate Auth Token
		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": None
				})
			}

		# Read request payload
		request_data = frappe.request.get_json() or {}
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "No data available",
					"result": None
				})
			}

		payload = decrypt_payload(encrypted_payload)
		user_id = payload.get("userId")

		# Fetch Branches
		branches = frappe.get_all(
			"Branch",
			fields=["branch", "custom_branch_code", "custom_zone"]
		)

		if not branches:
			return {
				"response": encrypt_payload({
					"status": 1001,
					"message": "Branch does not exist",
					"result": []
				})
			}

		result_list = []
		for data in branches:
			result_list.append({
				"branchName": data.branch,          # fixed typo
				"branchCode": data.custom_branch_code,
				"zone": data.zone
			})

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Success",
				"result": result_list
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Branch API Error")
		frappe.local.response["http_status_code"] = 500
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "Internal Server Error",
				"result": None
			})
		}
	

@frappe.whitelist(allow_guest=True)
def markAttendance():
	try:
		api_key = frappe.get_request_header("api-key")
		auth_token = frappe.get_request_header("Auth-Token")

		if api_key != frappe.conf.mobile_api_key or not auth_token:
			return {
			"response": encrypt_payload({
				"status": 401,
				"message": "Unauthorized",
				"result": []
			})
		}
		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": []
				})
			}

		data = decrypt_payload((frappe.request.get_json() or {}).get("request"))

		user_id = data.get("userID")
		attendance_type = data.get("attendanceType")
		attendance_date_str = data.get("attendanceDate")
		attendance_time = data.get("attendanceTime")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			["name", "employee_name", "branch"],
			as_dict=True
		)

		if not employee:
			return {
			"response": encrypt_payload({
				"status": 401,
				"message": "In valid User",
				"result": []
			})
		}

		# Fetch existing attendance
		attendance = frappe.db.sql("""
			SELECT name
			FROM `tabAttendance`
			WHERE employee = %s
			  AND attendance_date = STR_TO_DATE(%s, '%%d-%%m-%%Y')
			LIMIT 1
		""", (employee.name, attendance_date_str), as_dict=True)

		attendance_id = attendance[0]["name"] if attendance else None
		dt = datetime.strptime(f"{attendance_date_str} {attendance_time}","%d-%m-%Y %H:%M:%S")
		
		if attendance_type == "1":
			if not attendance_id:
				doc = frappe.new_doc("Attendance")
				doc.employee = employee.name
				doc.employee_name = employee.employee_name
				doc.branch = employee.branch
				doc.attendance_date = frappe.db.sql(
					"SELECT STR_TO_DATE(%s,'%%d-%%m-%%Y')",
					attendance_date_str
				)[0][0]
				doc.status = "Present"
				doc.in_time = dt
				doc.insert(ignore_permissions=True)
				frappe.db.commit()

				attendance_id = doc.name
				print("sssssssssssssssss",attendance_id)
				return{
					"response": encrypt_payload({
						"status": 200,
						"message":  "Punch In marked successfully",
						"result": attendance_id
					})
				}
				
				
			else:
				return {
					"response": encrypt_payload({
						"status": 200,
						"message":  "Punch In Already Exist",
						"result": attendance_id
					})
				}
					
		elif attendance_type == "2":
			if not attendance_id:
				return encrypt_payload({
					"status": 1002,
					"message": "Punch In not found"
				})

			frappe.db.set_value(
			"Attendance",
			attendance_id,
			"out_time",
			dt
			)

			frappe.db.commit()

			return {
					"response": encrypt_payload({
						"status": 200,
						"message":  "Out marked successfully",
						"result": attendance_id
					})
				}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Attendance API Error")
		return encrypt_payload({
			"status": 1002,
			"message": "Internal Server Error"
		})


@frappe.whitelist(allow_guest=True)
def getAttendanceHistory():
	
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}
		
		user = validate_auth_token()
		if not user:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": []
				})
			}

		request_data = frappe.request.get_json()
		encrypted_payload = request_data.get("request")

		if not encrypted_payload:
			return {
				"response": encrypt_payload({
					"status": 1002,
					"message": "NO data available",
					"result": []
				})
			}

		data = decrypt_payload(encrypted_payload)
		print("aaaaaaaaaaaaaaaaaaaaa")
		user_id = data.get("userId")
		year = int(data.get("year"))
		month = data.get("month")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			["name", "branch"],
			as_dict=True
		)

		if not employee:
			return {
			"response": encrypt_payload({
				"status": 401,
				"message": "Invalid user",
				"result": []
			})
		}

		
		month_no = datetime.strptime(month, "%B").month
		
		records = frappe.db.sql("""
			SELECT
				a.attendance_date,
				a.in_time,
				a.out_time,
				a.status
			FROM `tabAttendance` a
			WHERE a.employee = %s
			  AND YEAR(a.attendance_date) = %s
			  AND MONTH(a.attendance_date) = %s
			ORDER BY a.attendance_date
		""", (employee.name, year, month_no), as_dict=True)
		print("aaaaaaaaaaaaaaaaaaaaaw",records,employee.name)
		result = []
		for r in records:
			branch_code = frappe.db.get_value(
					"Branch",
					employee.branch,
					"custom_branch_code"
				)

			result.append({
				"branchName": employee.branch,
				"branchID": branch_code,
				"attendanceDate": r.attendance_date.strftime("%d-%m-%Y"),
				"punchInTime": r.custom_punch_in_time,
				"punchOutTime": r.custom_punch_out_time,
				"attendanceStatus": 3 if r.status == "Present" else 1,
				"finalAttendacneStatus": 1 if r.status == "Present" else 2
			})

		return {
					"response": encrypt_payload({
						"status": 200,
						"message":  "Attendance history fetched successfully",
						"result": result
					})
				}


	except Exception:
		frappe.log_error(frappe.get_traceback(), "Attendance API Error")
		frappe.local.response["http_status_code"] = 500
		return {
			"response": encrypt_payload({
				"status": 1002,
				"message": "Internal Server Error",
				"result": None
			})
		}
	


@frappe.whitelist(allow_guest=True)
def getSalarySlip():
	try:
		api_key = frappe.get_request_header("api-key")
		if api_key != frappe.conf.mobile_api_key:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized",
					"result": None
				})
			}

		# Validate Auth Token
		auth_token = frappe.get_request_header("Auth-Token")
		if not auth_token:
			frappe.local.response["http_status_code"] = 401
			return {
				"response": encrypt_payload({
					"status": 401,
					"message": "Unauthorized User",
					"result": None
				})
			}

		# Read request payload
		request_data = frappe.request.get_json() or {}
		encrypted_payload = request_data.get("request")
		data = decrypt_payload(encrypted_payload)
		user_id = data.get("userId")
		year = int(data.get("year"))
		month = data.get("month")

		employee = frappe.db.get_value(
			"Employee",
			{"employee_number": user_id},
			"name"
		)

		if not employee:
			return encrypt_payload({
				"status": 1001,
				"message": "Invalid user",
				"result": []
			})
		from datetime import date
		import calendar
		month_no = datetime.strptime(month, "%B").month
		last_day = calendar.monthrange(year, month_no)[1]

		from_date = date(year, month_no, 1)
		to_date = date(year, month_no, last_day)

		slips = frappe.get_all(
			"Salary Slip",
			filters={
				"employee": employee,
				"start_date": ["between", [
					from_date,
					to_date
				]]
			},
			fields=["name", "posting_date"]
		)

		result = []
		for s in slips:
			result.append({
				"salarySlipID": s.name,
				"year": year,
				"month": month,
				"salrySlipPath": f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Salary Slip&name={s.name}"
			})

		return {
			"response": encrypt_payload({
				"status": 200,
				"message": "Salary slip fetched successfully",
				"result": result
			})
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Salary Slip Error")
		return {
			"response": encrypt_payload({
				"status": 400,
				"message": "Unable to Fetch Salary slip ",
				"result": []
			})
		}
