# # Copyright (c) 2026, CSM Technologies Pvt Ltd
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today


class ChequeBook(Document):

    def validate(self):
        self.validate_cheque_range()
        self.calculate_total_cheques()
        self.set_clear_date()


    def before_insert(self):
        self.generate_cheque_leaves()

    # -------------------------
    # Validate Cheque Range
    # -------------------------
    def validate_cheque_range(self):

        if not self.cheque_start_no or not self.cheque_end_no:
            return

        try:
            start = int(self.cheque_start_no)
            end = int(self.cheque_end_no)
        except ValueError:
            frappe.throw(_("Cheque Start No and Cheque End No must be numbers"))

        if start > end:
            frappe.throw(_("Cheque Start No cannot be greater than Cheque End No"))

    # -------------------------
    # Calculate Total Cheques
    # -------------------------
    def calculate_total_cheques(self):

        if not self.cheque_start_no or not self.cheque_end_no:
            self.total_cheques = 0
            return

        try:
            start = int(self.cheque_start_no)
            end = int(self.cheque_end_no)
        except ValueError:
            self.total_cheques = 0
            return

        self.total_cheques = end - start + 1

    # -------------------------
    # Generate Cheque Leaves
    # -------------------------
    def generate_cheque_leaves(self):

        if self.cheque_leaves:
            return

        if not self.cheque_start_no or not self.cheque_end_no:
            return

        start = int(self.cheque_start_no)
        end = int(self.cheque_end_no)

        for i in range(start, end + 1):
            self.append("cheque_leaves", {
                "cheque_no": i,
                "status": "Available",
                "cheque_date": today(),  # ✅ aaj ki date
            })


    def set_clear_date(self):
        for row in self.cheque_leaves:
            # Agar status Cleared ho aur clear_date empty ho
            if row.status == "Cleared" and not row.clear_date:
                row.clear_date = today()

            # Optional: agar status wapas change ho jaye to clear_date hata do
            elif row.status != "Cleared":
                row.clear_date = None
