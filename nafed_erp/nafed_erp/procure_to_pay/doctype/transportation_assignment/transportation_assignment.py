# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class TransportationAssignment(Document):
# 	pass

import re
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class TransportationAssignment(Document):
    def validate(self):
        """
        The validate method runs every time the document is saved.
        """
        self.check_transporter_blacklist()
        self.validate_transport_mode_fields()
        # self.validate_vehicle_number()
        self.validate_mobile_number()

    def check_transporter_blacklist(self):
        if self.transporter_name:

            # Fetching the 'on_hold' status from the Supplier master
            is_on_hold = frappe.db.get_value("Supplier", self.transporter_name, "on_hold")
            if is_on_hold:
                frappe.throw(_("Transporter {0} is currently ON HOLD / BLACKLISTED! Assignment cannot be created.").format(self.transporter_name))

    def validate_transport_mode_fields(self):
        total_qty = sum(flt(item.dispatch_quantity) for item in self.items)
        capacity = flt(self.vehicle_capacity)
        
        if capacity > 0 and total_qty > capacity:
            # frappe.msgprint(_("Warning: Total Dispatch Quantity ({0}) exceeds Vehicle Capacity ({1})").format(total_qty, vehicle_capacity))

            frappe.throw(_("Overloaded! Total Quantity ({0}) exceeds Capacity ({1})").format(total_qty, capacity))

    # =========================
    # Vehicle number Validation 
    # =========================
    
    # def validate_vehicle_number(self):
    #     if self.transportation_mode == "Truck":
    #         if not self.vehicle_number:
    #             frappe.throw(_("Vehicle Number is required for Truck."))

    #         # Normalize (remove spaces/dashes)
    #         vehicle = self.vehicle_number.replace(" ", "").replace("-", "").upper()
    #         pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'

    #         if not re.match(pattern, vehicle):
    #             frappe.throw(_("Invalid Vehicle Number format: {0}").format(self.vehicle_number))
    

    # =========================
    # Mobile number Validation 
    # =========================
    def validate_mobile_number(self):
        if self.mobile_no:
            pattern = r'^[6-9]\d{9}$'

            if not re.match(pattern, self.mobile_no):
                frappe.throw(_("Enter valid mobile number (10 digits starting with 6-9)"))