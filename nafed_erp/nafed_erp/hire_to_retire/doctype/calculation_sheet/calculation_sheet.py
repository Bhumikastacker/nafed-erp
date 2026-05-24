# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CalculationSheet(Document):
    @frappe.whitelist()
    def calculate_dynamic_arrears(self):
        # --- ARREAR & RECOVERY LOGIC (UNTOUCHED) ---
        comp = self.salary_component
        curr_pct = flt(self.current_compensation_)
        revised_pct = flt(self.revised_compensation_)
        
        if self.type == "Arrears" and revised_pct <= curr_pct:
            frappe.msgprint("For Arrears, the revised percentage should be higher.")
            return []

        if self.type == "Recoveries" and revised_pct >= curr_pct:
            frappe.msgprint("For Recoveries, the revised percentage should be lower.")
            return []

        employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "custom_basic_pay"])
        arrear_list = []

        for emp in employees:
            basic = flt(emp.get("custom_basic_pay"))

            if basic > 0:
                prev_amt = basic * (curr_pct / 100)
                rev_amt = basic * (revised_pct / 100)
                arrear_list.append({
                    "employee": emp.name, "component": comp,
                    "previous_amount": prev_amt, "revised_amount": rev_amt 
                })
        return arrear_list

    @frappe.whitelist()
    def get_ex_gratia_data(self):
        # --- EX-GRATIA LOGIC (UNTOUCHED) ---
        if not self.salary_component_details: return []
        selected_comps = [d.salary_component for d in self.salary_component_details]
        filters = {"status": "Active"}
        if self.employment_type: filters["employment_type"] = self.employment_type

        employees = frappe.get_all("Employee", filters=filters, fields=["name", "custom_basic_pay"])

        data = []
        for emp in employees:
            ss_name = frappe.db.get_value("Salary Structure Assignment", {"employee": emp.name, "docstatus": 1}, "salary_structure")
            basic_pay = flt(emp.get("custom_basic_pay"))
            res = {"employee": emp.name, "basic": 0, "da": 0, "hra": 0, "total": 0}

            temp_dict = {}
            if ss_name:
                sal_details = frappe.get_all("Salary Detail", filters={"parent": ss_name}, fields=["salary_component", "amount"])
                temp_dict = {sd.salary_component: flt(sd.amount) for sd in sal_details}

                for sc in selected_comps:
                    val = basic_pay if sc == "Basic" else temp_dict.get(sc, 0)

                    if val == 0 and sc == "Dearness Allowance":
                        pct = frappe.db.get_value("Salary Component", sc, "custom_default_percentage_")
                        val = basic_pay * (flt(pct or 60) / 100)

                    if sc == "Basic": 
                        res["basic"] = val

                    elif sc == "Dearness Allowance": 
                        res["da"] = val

                    elif sc == "House Rent Allowance": 
                        res["hra"] = val
                        
                    res["total"] += val
            if res["total"] > 0: data.append(res)
        return data

    @frappe.whitelist()
    def create_additional_salaries(self):
        # --- BULK CREATION LOGIC ---
        success_count = 0
        
        # 1. Decide source table
        if self.type in ["Arrears", "Recoveries"]:
            source_table = self.component_details
        else:
            source_table = self.ex_gratia_result_table

        for d in source_table:
            # 2. Decide Amount field based on your new names
            if self.type == "Ex-Gratia":
                amt_to_pay = flt(d.get("ex_gratia_manual_amount") or 0)
                target_comp = self.salary_component_details[0].salary_component
            else:
                amt_to_pay = flt(d.get("final_amount") or 0)
                target_comp = self.salary_component

            if amt_to_pay > 0 and frappe.db.exists("Salary Structure Assignment", {"employee": d.employee, "docstatus": 1}):
                try:
                    add_sal = frappe.get_doc({
                        "doctype": "Additional Salary", "employee": d.employee, "salary_component": target_comp,
                        "payroll_date": self.payroll_entry_date, "amount": flt(amt_to_pay, 2), "company": self.company,
                        "ref_doctype": "Calculation Sheet", "ref_docname": self.name, "overwrite_salary_structure_amount": 0
                    })
                    add_sal.insert(ignore_permissions=True)
                    add_sal.submit()
                    success_count += 1
                except: continue
        
        frappe.msgprint(f"Process Finished: {success_count} entries created.")
        return success_count