# Copyright (c) 2026
#frappe-bench/frappe-bench$ ./env/bin/pip install python-docx

import frappe
from frappe.utils import get_site_path, strip_html
from frappe.utils.file_manager import save_file

import frappe

@frappe.whitelist()
def export_multiple_docx(doctype, docnames):
    import json
    from datetime import datetime
    from html2docx import html2docx
    from bs4 import BeautifulSoup
    from frappe.utils.file_manager import save_file

    if isinstance(docnames, str):
        docnames = json.loads(docnames)

    full_html = ""

    for i, name in enumerate(docnames):
        doc = frappe.get_doc(doctype, name)

        html_content = doc.get("text_editor_uton") or ""
        soup = BeautifulSoup(html_content, "html.parser")

        # 🔥 IMAGE FIX BLOCK
        for img in soup.find_all("img"):
            src = img.get("src", "")

            if not src:
                continue

            try:
                import os
                import base64
                from urllib.parse import urlparse

                if src.startswith("http"):
                    src = urlparse(src).path

                if src.startswith("/nafed.erp"):
                    src = src.replace("/nafed.erp", "")

                src = src.split("?")[0]

                if src.startswith("/files/") or src.startswith("/private/files/"):

                    file_path = frappe.get_site_path(src.lstrip("/"))

                    if os.path.exists(file_path):

                        with open(file_path, "rb") as f:
                            encoded = base64.b64encode(f.read()).decode("utf-8")

                        ext = src.split(".")[-1].lower()
                        if ext == "jpg":
                            ext = "jpeg"

                        img["src"] = f"data:image/{ext};base64,{encoded}"
                        img["style"] = "width:300px;"

            except Exception as e:
                frappe.log_error(f"Image error: {src}\n{str(e)}")

        full_html += str(soup)

        if i != len(docnames) - 1:
            full_html += '<p style="page-break-after: always;"></p>'

    docx_file = html2docx(full_html, title=f"{doctype} Export")

    file_name = f"{doctype}_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    file_doc = save_file(
        file_name,
        docx_file.getvalue(),
        doctype,
        docnames[0],
        is_private=0
    )

    return file_doc.file_url
    
    


class AnnualReport(frappe.model.document.Document):
    pass
