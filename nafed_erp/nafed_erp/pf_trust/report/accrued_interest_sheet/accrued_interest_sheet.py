# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.utils import date_diff, flt, getdate

def execute(filters=None):
	if not filters: filters = {}
	
	columns = get_columns()
	data = []
	
	# ========================================
	# Fetch filter values from the report UI
	# ========================================
	to_date = filters.get("to_date") or frappe.utils.today()
	mode_filter = filters.get("interest_mode")
	investment_filter = filters.get("investment")
	security_filter = filters.get("name_of_security")

	# =====================================
	# conditions based on selected filters
	# =====================================
	conditions = ""
	if mode_filter:
		conditions += " AND pfi.interest_mode = %(selected_mode)s"
	
	if investment_filter:
		conditions += " AND pfi.investment = %(selected_inv)s"
	
	if security_filter:
		conditions += " AND pfi.name_of_security LIKE %(selected_sec)s"
	
	# =============================
	# Fetch Parent Investment Data
	# =============================
	query = f"""
		SELECT 
			pfi.name, pfi.invoice_number, pfi.invoice_date, pfi.face_value, 
			pfi.coupon_rate as rate, pfi.total_amount, pfi.investment, pfi.investment_category,
			cat.investment_category_name,pfi.interest_mode,pfi.name_of_security,
			inv.investment_name as particulars
		FROM 
			`tabPF Investment` pfi
		LEFT JOIN `tabInvestment Category` cat ON pfi.investment_category = cat.name
		LEFT JOIN `tabInvestment` inv ON pfi.investment = inv.name
		WHERE 
			pfi.company = %(company)s {conditions} AND pfi.docstatus < 2
		ORDER BY 
			cat.investment_category_name ASC, pfi.invoice_date ASC
	"""
	
	investments = frappe.db.sql(query, {
			"company": filters.get("company"),
			"selected_mode": mode_filter,
			"selected_inv": investment_filter,
			"selected_sec": f"%{security_filter}%" if security_filter else None
		}, as_dict=1)

	current_category = None
	serial_no = 1
	cat_invested_total = 0
	cat_face_total = 0
	cat_interest_total = 0

	for d in investments:
		
		cat_label = d.get("investment_category_name") or "OTHERS"
		if cat_label != current_category:
			if current_category:
				data.append({
					"sn": "", "invoice_number": "<b>TOTAL</b>",
					"total_amount": cat_invested_total, "face_value": cat_face_total, "interest_accrued": cat_interest_total
				})
				cat_invested_total = 0; cat_face_total = 0; cat_interest_total = 0

			current_category = cat_label
			data.append({"sn": "", "invoice_number": f"<b>{current_category.upper()}</b>"})
			serial_no = 1 

		# ==========================================
		# Fetch Child Table Data (Maturity Details)
		# ==========================================
		child_rows = frappe.get_all("Maturity Details", 
			filters={"parent": d.get("name")}, 
			fields=["investment_period_from", "investment_period_to"],
			order_by="idx asc")

		if not child_rows:
			child_rows = [{"investment_period_from": d.get("invoice_date"), "investment_period_to": ""}]

		for row_idx, child in enumerate(child_rows):
			from_date = child.get("investment_period_from") or d.get("invoice_date")

			days = date_diff(to_date, from_date) if from_date else 0
			if days < 0: days = 0 
			
			# ==========================================
			# Interest Calculation
			# Formula:
			# Interest = Face Value × Rate × Days / 365
			# ==========================================
			interest = (flt(d.get("face_value")) * (flt(d.get("rate")) / 100) * flt(days)) / 365

			if row_idx == 0:
				cat_invested_total += flt(d.get("total_amount"))
				cat_face_total += flt(d.get("face_value"))

			cat_interest_total += interest

			# =========================================
			# Append the data row to the report result
			# =========================================
			data.append({
				"sn": serial_no if row_idx == 0 else "", 
				"invoice_number": d.get("name"),
				"supplier_inv": d.get("invoice_number"),
				"invoice_date": d.get("invoice_date"),
				"total_amount": d.get("total_amount") if row_idx == 0 else 0,
				"face_value": d.get("face_value") if row_idx == 0 else 0,
				"rate": f"{flt(d.get('rate'), 2)}%",
				"maturity_date": child.get("investment_period_to"),
				"interest_mode": d.get("interest_mode"),
				"particulars": d.get("particulars") or d.get("investment"),
				"from_date": from_date,
				"to_date": to_date,
				"no_of_days": days,
				"interest_accrued": interest
			})
			if row_idx == 0: serial_no += 1

	if investments:
		data.append({
			"sn": "", "invoice_number": "<b>TOTAL</b>",
			"total_amount": cat_invested_total, "face_value": cat_face_total, "interest_accrued": cat_interest_total
		})

	return columns, data

def get_columns():
	return [
		{"label": "S.N.", "fieldname": "sn", "fieldtype": "Data", "width": 80},
		{"label": "Voucher No.", "fieldname": "invoice_number", "fieldtype": "Data", "width": 160},
		{"label": "Supplier Invoice No.", "fieldname": "supplier_inv", "fieldtype": "Data", "width": 160},
		{"label": "Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 100},
		{"label": "Amount Invested", "fieldname": "total_amount", "fieldtype": "Currency", "width": 130},
		{"label": "Face Value", "fieldname": "face_value", "fieldtype": "Currency", "width": 130},
		{"label": "Rate (%)", "fieldname": "rate", "fieldtype": "Data", "width": 100},
		{"label": "Maturity Date", "fieldname": "maturity_date", "fieldtype": "Date", "width": 120},
		{"label": "Interest Mode", "fieldname": "interest_mode", "fieldtype": "Data", "width": 120},
		{"label": "Particulars", "fieldname": "particulars", "fieldtype": "Data", "width": 200},
		{"label": "From Date", "fieldname": "from_date", "fieldtype": "Date", "width": 110},
		{"label": "To Date", "fieldname": "to_date", "fieldtype": "Date", "width": 110},
		{"label": "No. of Days", "fieldname": "no_of_days", "fieldtype": "Int", "width": 90},
		{"label": "Interest Accrued", "fieldname": "interest_accrued", "fieldtype": "Currency", "width": 140}
	]