# Copyright (c) 2026, CSM Technologies Pvt Ltd
# For license information, please see license.txt

import frappe
import csv
import json
from frappe.model.document import Document
from frappe.utils import now

MANDATORY_FIELDS = [
    "Case Category",
    "Party Name",
    "Jurisdiction",
    "Priority",
    "Branch",
    "Assigned Advocate",
    "Related PO / Contract Ref"
]

ERROR_REJECT_THRESHOLD = 30  # percent


class LegalCaseUploadBatch(Document):

    def before_insert(self):
        self.uploaded_by = frappe.session.user
        self.upload_date = now()
        self.validation_status = "Draft"

    # -------------------------
    # VALIDATE CSV UPLOAD
    # -------------------------
    @frappe.whitelist()
    def validate_upload(self):
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw("Not permitted")

        if not self.upload_file:
            frappe.throw("Please upload a CSV file")

        file_doc = frappe.get_doc("File", {"file_url": self.upload_file})
        file_path = file_doc.get_full_path()

        # Clear old staging records
        frappe.db.delete(
            "Legal Case Upload Staging",
            {"upload_batch": self.name}
        )

        total = errors = valid = 0

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for idx, row in enumerate(reader, start=1):
                total += 1
                row_errors = []

                for field in MANDATORY_FIELDS:
                    if not row.get(field):
                        row_errors.append(f"{field} missing")

                status = "Valid"
                if row_errors:
                    status = "Error"
                    errors += 1
                else:
                    valid += 1

                frappe.get_doc({
                    "doctype": "Legal Case Upload Staging",
                    "upload_batch": self.name,
                    "row_number": idx,
                    "validation_status": status,
                    "error_message": ", ".join(row_errors),
                    "mapped_payload": json.dumps(row)
                }).insert(ignore_permissions=True)

        self.case_count = valid
        self.error_rate = (errors / total) * 100 if total else 0

        if valid == 0:
            self.validation_status = "Failed"
        elif errors > 0:
            self.validation_status = "Partial"
        else:
            self.validation_status = "Passed"

        if self.error_rate > ERROR_REJECT_THRESHOLD:
            self.validation_status = "Failed"
            self.save()
            frappe.throw(
                f"Upload rejected. Error rate {self.error_rate:.2f}% exceeds policy limit."
            )

        self.save()

    # -------------------------
    # IMPORT VALID CASES
    # -------------------------
    @frappe.whitelist()
    def import_valid_cases(self):
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw("Not permitted")

        if self.validation_status not in ("Passed", "Partial"):
            frappe.throw("Validation not completed or failed")

        rows = frappe.get_all(
            "Legal Case Upload Staging",
            filters={
                "upload_batch": self.name,
                "validation_status": "Valid"
            },
            fields=["name", "mapped_payload"]
        )

        created_cases = []

        for r in rows:
            data = json.loads(r.mapped_payload)

            case = frappe.get_doc({
                "doctype": "Legal Case Registration",
                "case_category": data.get("Case Category"),
                "party_name": data.get("Party Name"),
                "opposing_party": data.get("Opposing Party"),
                "jurisdiction": data.get("Jurisdiction"),
                "priority": data.get("Priority"),
                "branch_name": data.get("Branch"),
                'related_po__contract_ref': data.get("Related PO / Contract Ref"),
                "agreement_type": data.get("Agreement Type"),
                "matter_value": data.get("Matter Value"),
                "assigned_advocate": data.get("Assigned Advocate"),
                "status": "Registered"
            })
            case.insert(ignore_permissions=True)

            frappe.db.set_value(
                "Legal Case Upload Staging",
                r.name,
                "created_case",
                case.name
            )

            created_cases.append(case.name)

        self.generate_summary(created_cases)

    def generate_summary(self, created_cases):
        summary = [
            ["Upload Batch", self.name],
            ["Uploaded By", self.uploaded_by],
            ["Created On", now()],
            ["Total Cases Created", len(created_cases)],
            ["Case IDs", ", ".join(created_cases)]
        ]

        content = "\n".join([",".join(map(str, r)) for r in summary])

        file = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{self.name}_summary.csv",
            "content": content,
            "attached_to_doctype": self.doctype,
            "attached_to_name": self.name
        }).insert(ignore_permissions=True)

        self.import_summary_file = file.file_url
        self.save()

        # frappe.sendmail(
        #     recipients=[self.uploaded_by],
        #     subject="Bulk Legal Case Upload Completed",
        #     message=f"""
        #     Upload Batch: {self.name}

        #     Status: {self.validation_status}
        #     Cases Imported: {len(created_cases)}
        #     """
        #             )


# -------------------------
# DOWNLOAD SAMPLE CSV
# -------------------------
@frappe.whitelist()
def download_sample_csv():
    content = (
        "Case Category,Party Name,Opposing Party,Jurisdiction,Priority,Branch,"
        "Related PO / Contract Ref,Agreement Type,Matter Value,Assigned Advocate\n"
    )

    frappe.response["filename"] = "legal_case_bulk_template.csv"
    frappe.response["filecontent"] = content
    frappe.response["type"] = "download"
