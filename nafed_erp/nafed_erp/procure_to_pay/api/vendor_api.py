import frappe
import requests
import re


@frappe.whitelist()
def fetch_bank_from_ifsc(ifsc):
    try:
        resp = requests.get(
            f'https://ifsc.razorpay.com/{ifsc.upper()}',
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                'verified':  True,
                'bank_name': data.get('BANK', ''),
                'branch':    data.get('BRANCH', ''),
            }
        return {'verified': False}
    except Exception as e:
        frappe.log_error(str(e), 'IFSC API Error')
        return {'verified': False, 'error': str(e)}


@frappe.whitelist()
def verify_gstin(gstin):
    # Format check first (free, no API needed)
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gstin.upper()):
        return {'verified': False, 'error': 'Invalid format'}
    # If GST Portal API key configured — call it
    # Otherwise return format-verified only
    return {'verified': True, 'format_only': True}


@frappe.whitelist()
def verify_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, pan.upper()):
        return {'verified': False, 'error': 'Invalid format'}
    return {'verified': True, 'format_only': True}
