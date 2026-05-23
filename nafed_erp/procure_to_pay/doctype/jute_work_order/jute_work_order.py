import frappe
from frappe.model.document import Document

class JuteWorkOrder(Document):

    def validate(self):
        self.calculate_totals()

    def before_submit(self):
        self.calculate_totals()

    def calculate_totals(self):

        total_qty = 0

        for row in self.delivery_location_table:
            total_qty += row.gunny_bags_req or 0

        rate = 0

        if self.gunny_bag_details_table:
            item = self.gunny_bag_details_table[0]

            rate = (
                item.unit_price
                or getattr(item, "rate", 0)
                or 0
            )

        self.total_quantity = total_qty
        self.total_price = total_qty * rate