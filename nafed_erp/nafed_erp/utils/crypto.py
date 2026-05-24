import json
import base64
import os
import frappe
from Crypto.Cipher import AES
from datetime import datetime, date


def _get_secret_key():
    """
    Must be 32 bytes for AES-256
    Stored securely in site_config.json
    """
    secret = frappe.conf.mobile_api_secret
    if not secret or len(secret) < 32:
        raise Exception("mobile_api_secret must be at least 32 characters")
    return secret[:32].encode()

def make_json_safe(data):
    """
    Recursively convert datetime/date objects to ISO strings
    """
    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    else:
        return data


def encrypt_payload(data: dict) -> str:
    key = _get_secret_key()
    iv = os.urandom(12)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    safe_data = make_json_safe(data)
    plaintext = json.dumps(safe_data).encode("utf-8")

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    encrypted = iv + tag + ciphertext

    return base64.b64encode(encrypted).decode("utf-8")

    


def decrypt_payload(encrypted_data: str) -> dict:
    """
    Decrypts encrypted string and returns dictionary
    """
    key = _get_secret_key()
    raw = base64.b64decode(encrypted_data)

    iv = raw[:12]
    tag = raw[12:28]
    ciphertext = raw[28:]

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)

    return json.loads(decrypted.decode("utf-8"))
