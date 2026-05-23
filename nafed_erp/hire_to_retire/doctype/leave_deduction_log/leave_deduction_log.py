import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class LeaveDeductionLog(Document):
    def on_submit(self):
        create_leave_ledger_entry(employee=self.employee,
            leave_type=self.leave_type,
            deduction_unit=self.deduction_unit,
            docname=self.name,
            doctype=self.doctype)

    def on_cancel(self):
        # Delete any Leave Ledger Entries linked to this log
        frappe.db.sql(
            """
            DELETE FROM `tabLeave Ledger Entry`
            WHERE
                transaction_type = %s
                AND transaction_name = %s
            """,
            (self.doctype, self.name),
        )
        frappe.db.commit()
        frappe.msgprint(f"Leave Ledger Entry linked to {self.name} has been deleted.")

def create_leave_ledger_entry(employee, leave_type, deduction_unit, docname, doctype):
    
    entry_date = getdate(frappe.utils.now())
    employee_company = frappe.db.get_value("Employee", employee, "company")
    if not employee_company:
        frappe.throw(f"Company not found for employee {employee}")

    ledger = frappe.new_doc("Leave Ledger Entry")
    ledger.employee = employee
    ledger.leave_type = leave_type
    ledger.transaction_type = doctype
    ledger.transaction_name = docname
    ledger.leaves = deduction_unit
    ledger.from_date = entry_date
    ledger.to_date = entry_date
    ledger.company = employee_company

    ledger.insert(ignore_permissions=True)
    ledger.submit()