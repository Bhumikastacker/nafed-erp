# # File: nafed_erp/nafed_erp/api/esamridhi_client.py

# import frappe
# import requests
# from frappe import _
# from frappe.utils import now_datetime, add_to_date
# import json

# class EsamridhiClient:
#     def __init__(self):
#         self.settings = frappe.get_single("E-Samridhi Settings")
#         self.base_url = self.settings.domain.rstrip('/')
#         self.token = None
        
#     def get_token(self, force_refresh=False):
#         """Get valid token - either from cache or new login"""
        
#         # Check if existing token is still valid
#         if not force_refresh and self.settings.current_token:
#             if self.settings.token_expiry and self.settings.token_expiry > now_datetime():
#                 return self.settings.current_token
        
#         # Get new token
#         login_url = f"{self.base_url}/api/v1/esamridhi/auth/login"
        
#         payload = {
#             "username": self.settings.username,
#             "password": self.settings.get_password("password")  # Frappe decrypts password
#         }
        
#         try:
#             response = requests.post(
#                 login_url,
#                 json=payload,
#                 headers={"Content-Type": "application/json"},
#                 timeout=30
#             )
#             response.raise_for_status()
            
#             token = response.json().get("jwtToken")
            
#             # Save token in settings
#             self.settings.current_token = token
#             self.settings.token_expiry = add_to_date(None, hours=24)  # Token valid for 24 hours
#             self.settings.save(ignore_permissions=True)
            
#             frappe.log_error(f"New E-Samridhi token obtained", "E-Samridhi Integration")
#             return token
            
#         except requests.exceptions.RequestException as e:
#             frappe.log_error(f"E-Samridhi Login Failed: {str(e)}", "E-Samridhi Integration")
#             frappe.throw(_("Failed to authenticate with E-Samridhi: {0}").format(str(e)))
    
#     def make_request(self, endpoint, params=None):
#         """Make authenticated request to E-Samridhi API"""
        
#         token = self.get_token()
        
#         url = f"{self.base_url}{endpoint}"
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }
        
#         try:
#             response = requests.get(url, headers=headers, params=params, timeout=30)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             frappe.log_error(f"API Request Failed: {url} - {str(e)}", "E-Samridhi Integration")
#             raise
    
#     def sync_farmers(self, from_date, to_date):
#         """Fetch farmers from E-Samridhi"""
#         all_farmers = []
#         page_no = 1
#         page_size = 100
        
#         while True:
#             params = {
#                 "fromDate": from_date,
#                 "toDate": to_date,
#                 "pageNo": page_no,
#                 "pageSize": page_size
#             }
            
#             response = self.make_request("/api/v1/esamridhi/farmers", params)
            
#             if response.get("status") == "SUCCESS":
#                 data = response.get("data", {})
#                 records = data.get("records", [])
                
#                 if records:
#                     all_farmers.extend(records)
                
#                 # Check pagination
#                 pagination = data.get("pagination", {})
#                 if page_no >= pagination.get("totalPages", 0):
#                     break
                    
#                 page_no += 1
#             else:
#                 break
        
#         return all_farmers
    
#     # Add similar methods for crops, lots, dispatches, whr, payments