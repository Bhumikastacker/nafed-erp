# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class Property(Document):
    def before_insert(self):
            if not self.branch:
                frappe.throw("Branch is not selected. Please select a valid branch.")
            
            branch = frappe.get_doc('Branch', self.branch)
            if not branch.custom_branch_code:
                frappe.throw("Branch Code is not set for the selected branch. Please ensure it is properly configured.")
            
            branch_code = branch.custom_branch_code
            self.naming_series = self.generate_naming_series(branch_code)
            self.set_branch_code_sequence(branch_code)

    def on_update(self):
            if not self.branch:
                frappe.throw("Branch is not selected. Please select a valid branch.")
            
            branch = frappe.get_doc('Branch', self.branch)
            if not branch.custom_branch_code:
                frappe.throw("Branch Code is not set for the selected branch. Please ensure it is properly configured.")
            
            branch_code = branch.custom_branch_code
            if self.naming_series:
                pass
            else:
                self.naming_series = self.generate_naming_series(branch_code)
            self.set_branch_code_sequence(branch_code)

    def generate_naming_series(self, branch_code):
            """Generate the naming series format."""
            return f"EST/{branch_code}/"

    def set_branch_code_sequence(self, branch_code):
            """Set the next available sequence for the Property naming series."""
            latest_property = frappe.get_all(
                'Property',
                filters={'naming_series': ['like', f"EST/{branch_code}/%"]},
                fields=['naming_series'],
                order_by="creation desc",
                limit=1
            )
            print(latest_property)
            next_sequence = 1
            if latest_property:
                # Extracting the sequence from the last property document
                last_sequence = latest_property[0].naming_series.split('/')[-1]
                print(last_sequence)
                if last_sequence.isdigit():
                    next_sequence = int(last_sequence) + 1
            
            # Formatting the sequence to be 5 digits
            formatted_sequence = str(next_sequence).zfill(5)

            # Update the naming series with the correct sequence
            self.naming_series = f"EST/{branch_code}/{formatted_sequence}"
