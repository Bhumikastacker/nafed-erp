# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, get_first_day, get_last_day, add_months

# OPS score bands from SRS
OPS_BANDS = [
    (90, 101, 'Excellent'),
    (75,  90, 'Good'),
    (60,  75, 'Satisfactory'),
    (40,  60, 'Needs Improvement'),
    (0,   40, 'Poor'),
]

# Default KPI weightages from SRS
DEFAULT_WEIGHTAGES = {
    'Timeliness of Delivery':           20,
    'Quality Compliance':               20,
    'Quantity Accuracy':                15,
    'Documentation & Invoice Accuracy': 15,
    'Response to Queries':              10,
    'Contract Adherence':               10,
    'Financial Discipline':             10,
}


class VendorPerformanceRecord(Document):

    def validate(self):
        self.set_defaults()
        self.validate_vendor_active()
        self.validate_period_dates()
        self.validate_kpi_scores()
        self.calculate_ops()
        self.set_rating_category()
        self.set_tender_eligibility()
        self.check_ops_trend()
        self.auto_fetch_vendor_details()

    def on_submit(self):
        self.set_approval_meta()
        self.update_vendor_performance_score()
        self.restrict_poor_vendor()
        self.notify_officers()

    # ═══════════════════════════════════════════════════
    # VALIDATE METHODS
    # ═══════════════════════════════════════════════════

    def set_defaults(self):
        if not self.vendor_performance_id:
            count = frappe.db.count('Vendor Performance Record') + 1
            self.vendor_performance_id = f'VPR-{today().replace("-","")}-{count:04d}'
        if not self.initiated_by:
            self.initiated_by = frappe.session.user
        if not self.kpi_scores:
            self.populate_default_kpi_rows()

    def populate_default_kpi_rows(self):
        """Auto-fill 7 KPI rows with default weightages on new record."""
        for param, weight in DEFAULT_WEIGHTAGES.items():
            self.append('kpi_scores', {
                'kpi_parameter': param,
                'weightage':     weight,
                'score':         0,
                'data_source':   'Manual',
            })

    def auto_fetch_vendor_details(self):
        if self.vendor_id:
            result = frappe.db.get_value(
                'Vendor Registration', self.vendor_id,
                ['vendor_name', 'vendor_code'], as_dict=True
            )
            if result:
                self.vendor_name = result.vendor_name
                self.vendor_code = result.vendor_code

    def validate_vendor_active(self):
        if not self.vendor_id:
            return
        state = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'workflow_state'
        )
        if state not in ('Active', 'HO Approved'):
            frappe.throw(
                f'Vendor {self.vendor_id} is not Active (status: {state}). '
                f'Cannot evaluate inactive vendor.'
            )

    def validate_period_dates(self):
        if self.period_start_date and self.period_end_date:
            if self.period_end_date <= self.period_start_date:
                frappe.throw('Period End Date must be after Period Start Date')

    def validate_kpi_scores(self):
        if not self.kpi_scores:
            return

        total_weight = 0
        for row in self.kpi_scores:
            row.score     = row.score     or 0
            row.weightage = row.weightage or 0

            if row.score and (row.score < 0 or row.score > 5):
                frappe.throw(
                    f'Score for {row.kpi_parameter} must be between 1 and 5. '
                    f'Got: {row.score}'
                )

            if row.weightage <= 0:
                frappe.throw(
                    f'Weightage for {row.kpi_parameter} must be greater than 0.'
                )

            total_weight += row.weightage
            # Normalize score to 0-100 scale: (score/5) × weightage
            row.weighted_score = round((row.score / 5) * row.weightage, 2)

        if round(total_weight) != 100:
            self.data_mismatch_flag = 1
            self.missing_data_notes = (
                f'KPI weightages sum to {total_weight:.1f}%, not 100%.'
            )
            frappe.throw(
                f'Total KPI weightage must equal 100%. '
                f'Current total: {total_weight:.1f}%'
            )

    def calculate_ops(self):
        if not self.kpi_scores:
            self.overall_performance_score = 0
            return

        scored_rows = [r for r in self.kpi_scores if r.score and r.score > 0]

        if len(scored_rows) < len(self.kpi_scores):
            self.missing_data_flag = 1
            unscored = [r.kpi_parameter for r in self.kpi_scores
                        if not r.score or r.score == 0]
            self.missing_data_notes = f'Unscored KPIs: {", ".join(unscored)}'

        # OPS = Σ (score/5 × weightage) — gives 0-100 scale
        ops = sum((r.score / 5) * r.weightage
                  for r in self.kpi_scores if r.score)
        self.overall_performance_score = round(ops, 2)

    def set_rating_category(self):
        ops = self.overall_performance_score or 0
        for low, high, label in OPS_BANDS:
            if low <= ops < high:
                self.rating_category = label
                return
        self.rating_category = 'Poor'

    def set_tender_eligibility(self):
        ops = self.overall_performance_score or 0
        self.tender_eligible = 0 if ops < 40 else 1

    def check_ops_trend(self):
        if not self.vendor_id:
            return

        prev = frappe.db.sql("""
            SELECT overall_performance_score
            FROM `tabVendor Performance Record`
            WHERE vendor_id = %(vendor_id)s
            AND docstatus = 1
            AND name != %(name)s
            ORDER BY period_end_date DESC
            LIMIT 1
        """, {'vendor_id': self.vendor_id, 'name': self.name or 'NEW'},
        as_dict=True)

        if prev:
            prev_ops = prev[0].overall_performance_score or 0
            self.previous_ops = prev_ops
            current = self.overall_performance_score or 0
            if current > prev_ops + 2:
                self.ops_trend = 'Improved'
            elif current < prev_ops - 2:
                self.ops_trend = 'Declined'
            else:
                self.ops_trend = 'Stable'

    # ═══════════════════════════════════════════════════
    # ON SUBMIT METHODS
    # ═══════════════════════════════════════════════════

    def set_approval_meta(self):
        self.db_set('reviewed_by', frappe.session.user, update_modified=False)
        self.db_set('review_date', today(),             update_modified=False)

    def update_vendor_performance_score(self):
        """Write approved OPS back to Vendor Registration master record."""
        frappe.db.set_value(
            'Vendor Registration', self.vendor_id, {
                'performance_score':    self.overall_performance_score,
                'rating_category':      self.rating_category,
                'last_evaluation_date': today(),
            }
        )
        frappe.db.commit()
        frappe.msgprint(
            f'Performance score {self.overall_performance_score} '
            f'({self.rating_category}) saved to vendor master.',
            indicator='green'
        )

    def restrict_poor_vendor(self):
        """SRS: Poor vendors auto-restricted from tender participation."""
        if (self.overall_performance_score or 0) < 40:
            frappe.db.set_value(
                'Vendor Registration', self.vendor_id,
                'tender_blocked', 1
            )
            frappe.db.commit()
            frappe.msgprint(
                f'Vendor {self.vendor_code} OPS < 40. '
                f'Auto-blocked from tender participation.',
                indicator='red'
            )
        else:
            frappe.db.set_value(
                'Vendor Registration', self.vendor_id,
                'tender_blocked', 0
            )
            frappe.db.commit()

    def notify_officers(self):
        ho_users = frappe.get_all(
            'Has Role',
            filters={'role': 'HO Procurement Officer'},
            pluck='parent'
        )
        if ho_users:
            frappe.sendmail(
                recipients=ho_users,
                subject=f'Vendor Performance Approved — {self.vendor_name}',
                message=(
                    f'Vendor: {self.vendor_name} ({self.vendor_code})\n'
                    f'Period: {self.period_start_date} to {self.period_end_date}\n'
                    f'OPS Score: {self.overall_performance_score}\n'
                    f'Rating: {self.rating_category}\n'
                    f'Tender Eligible: {"Yes" if self.tender_eligible else "No"}\n'
                    f'Trend: {self.ops_trend or "First Evaluation"}'
                )
            )


# ── STANDALONE SCHEDULER FUNCTION ─────────────────────────────
# Outside class — called by hooks.py scheduler_events

def auto_initiate_monthly_evaluation():
    """
    Auto-initiate evaluation cycle on 1st of every month.
    Creates Draft Vendor Performance Record for all active vendors.
    """
    today_date = today()
    first_day  = get_first_day(add_months(today_date, -1))
    last_day   = get_last_day(add_months(today_date, -1))

    active_vendors = frappe.get_all(
        'Vendor Registration',
        filters={'workflow_state': ['in', ['Active', 'HO Approved']]},
        fields=['name', 'vendor_name', 'vendor_code']
    )

    created = 0
    for vendor in active_vendors:
        exists = frappe.db.exists('Vendor Performance Record', {
            'vendor_id':         vendor.name,
            'period_start_date': first_day,
            'period_end_date':   last_day,
        })
        if exists:
            continue

        doc = frappe.get_doc({
            'doctype':          'Vendor Performance Record',
            'vendor_id':         vendor.name,
            'vendor_name':       vendor.vendor_name,
            'vendor_code':       vendor.vendor_code,
            'evaluation_period': 'Monthly',
            'evaluation_type':   'Scheduled',
            'period_start_date': first_day,
            'period_end_date':   last_day,
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        created += 1

    frappe.db.commit()
    frappe.log_error(
        f'Monthly evaluation: {created} records created for {first_day} to {last_day}',
        'Vendor Performance Scheduler'
    )


@frappe.whitelist()
def auto_fetch_module_scores(vendor_id, start_date, end_date):
    """
    Fetch performance data from integrated ERPNext modules.
    Called from JS 'Fetch Module Data' button.
    Returns dict of KPI parameter -> auto_score (1-5 scale).
    """
    scores = {}

    # 1. TIMELINESS OF DELIVERY
    delivery_data = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN pr.posting_date <= po.schedule_date THEN 1 ELSE 0 END) as on_time
        FROM `tabPurchase Receipt` pr
        JOIN `tabPurchase Order` po ON pr.purchase_order = po.name
        WHERE pr.supplier = (
            SELECT vendor_code FROM `tabVendor Registration` WHERE name = %(vendor_id)s
        )
        AND pr.posting_date BETWEEN %(start)s AND %(end)s
        AND pr.docstatus = 1
    """, {'vendor_id': vendor_id, 'start': start_date, 'end': end_date}, as_dict=True)

    if delivery_data and delivery_data[0].total:
        rate = delivery_data[0].on_time / delivery_data[0].total
        scores['Timeliness of Delivery'] = round(rate * 5, 1)

    # 2. QUANTITY ACCURACY
    qty_data = frappe.db.sql("""
        SELECT
            SUM(pri.qty) as received,
            SUM(poi.qty) as ordered
        FROM `tabPurchase Receipt Item` pri
        JOIN `tabPurchase Receipt` pr ON pri.parent = pr.name
        JOIN `tabPurchase Order Item` poi ON pri.purchase_order_item = poi.name
        WHERE pr.supplier = (
            SELECT vendor_code FROM `tabVendor Registration` WHERE name = %(vendor_id)s
        )
        AND pr.posting_date BETWEEN %(start)s AND %(end)s
        AND pr.docstatus = 1
    """, {'vendor_id': vendor_id, 'start': start_date, 'end': end_date}, as_dict=True)

    if qty_data and qty_data[0].ordered:
        rate = min(qty_data[0].received / qty_data[0].ordered, 1.0)
        scores['Quantity Accuracy'] = round(rate * 5, 1)

    # 3. FINANCIAL DISCIPLINE
    payment_data = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN pe.posting_date <= pi.due_date THEN 1 ELSE 0 END) as on_time
        FROM `tabPayment Entry` pe
        JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
        JOIN `tabPurchase Invoice` pi ON per.reference_name = pi.name
        WHERE pe.party = (
            SELECT vendor_name FROM `tabVendor Registration` WHERE name = %(vendor_id)s
        )
        AND pe.posting_date BETWEEN %(start)s AND %(end)s
        AND pe.docstatus = 1
    """, {'vendor_id': vendor_id, 'start': start_date, 'end': end_date}, as_dict=True)

    if payment_data and payment_data[0].total:
        rate = payment_data[0].on_time / payment_data[0].total
        scores['Financial Discipline'] = round(rate * 5, 1)

    return scores