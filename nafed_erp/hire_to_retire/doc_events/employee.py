import frappe,re
from frappe import _
from frappe.utils import getdate, today



def validate_dates(doc, method=None):
    # Start vs End Date
    if doc.custom_start_date and doc.custom_end_date:
        if doc.custom_end_date < doc.custom_start_date:
            frappe.throw(
                ("End Date cannot be earlier than Start Date")
            )

    # Start Date vs Date of Joining
    if doc.date_of_joining and doc.custom_start_date:
        if doc.custom_start_date < doc.date_of_joining:
            frappe.throw(
                ("Start Date cannot be earlier than Date of Joining")
            )

def validate(doc, method):
    """Auto-generate full name (hb_name) from salutation and name parts."""
    name_parts = []
    

    if doc.salutation:
        name_parts.append(doc.salutation.strip())
    if doc.first_name:
        name_parts.append(doc.first_name.strip())
    if doc.middle_name:
        name_parts.append(doc.middle_name.strip())
    if doc.last_name:
        name_parts.append(doc.last_name.strip())

    full_name = " ".join(name_parts)

    if full_name:
        doc.custom_hb_name = full_name
    else:
        return
    if doc.reports_to and doc.custom_reviewing_officer:
        reporting_user = frappe.db.get_value(
            "Employee",
            doc.reports_to,
            "user_id"
        )

        if reporting_user and reporting_user == doc.custom_reviewing_officer:
            frappe.throw(
                ("Reporting  and Reviewing Officer cannot be the same user.")
            )
            

def validate_age(self, method=None):

    # Ensure field exists and has a value
    if not getattr(self, "date_of_birth", None):
        return  # skip if empty

    dob = getdate(self.date_of_birth)
    today_date = getdate(today())

    # Calculate age safely
    age = (today_date - dob).days // 365

    if age < 18:
        frappe.throw("Employee must be at least 18 years old.")

    return age

def update_user_permission(doc, method):
    report_user_id = frappe.db.get_value("Employee", doc.reports_to, "user_id")
    if not doc.custom_reviewing_officer:
        return
    if not report_user_id:
        frappe.throw(f"Kindly set user id in {doc.reports_to} employe")

    # delete old + duplicate permissions
    frappe.db.delete("User Permission", {"for_value": doc.name, "applicable_for": "Appraisal"})

    # create new permission
    frappe.get_doc({
        "doctype": "User Permission",
        "user": doc.custom_reviewing_officer,
        "allow": "Employee",
        "for_value": doc.name,
        "applicable_for": "Appraisal"
    }).insert(ignore_permissions=True)
    frappe.get_doc({
        "doctype": "User Permission",
        "user": report_user_id,
        "allow": "Employee",
        "for_value": doc.name,
        "applicable_for": "Appraisal"
    }).insert(ignore_permissions=True)


def validate_reports_to(doc, method):
    emp = doc.name
    reports_to = doc.reports_to
    secondary = doc.custom_other_reports_to_employee_id or []

    if reports_to and reports_to == emp:
        frappe.throw("Employee cannot report to themselves")

    seen = set()

    for row in secondary:
        if reports_to and row.employee == reports_to:
            frappe.throw("Reports To cannot also be in Secondary Reports To")

        if row.employee == emp:
            frappe.throw("Employee cannot be in their own Secondary Reports To")

        if row.employee in seen:
            frappe.throw("Duplicate employee found in Secondary Reports To")

        seen.add(row.employee)



# -----------------------------
# PF Distribution Validation
# -----------------------------


# ------------------------------------------------
# Common Helper: No Duplicate Rows in Child Table
# ------------------------------------------------
def validate_no_duplicate_rows(child_table, fields, table_name):
    seen = set()

    for idx, row in enumerate(child_table, start=1):
        key = tuple(row.get(field) for field in fields)

        # Skip completely empty rows
        if not any(key):
            continue

        if key in seen:
            frappe.throw(
                f"Duplicate entry found in <b>{table_name}</b> at row <b>{idx}</b>. "
                "Same data cannot be entered twice."
            )

        seen.add(key)

# ------------------------------------
# Employee Validate (MAIN ENTRY POINT)
# ------------------------------------
def validate(doc, method):
    # Educational Qualification
    validate_no_duplicate_rows(
        doc.education,
        ["school_university", "level", "year_of_passing"],
        "Educational Qualification"
    )

    # External Work History
    validate_no_duplicate_rows(
        doc.external_work_history,
        ["company", "designation"],
        "Previous Work Experience"
    )

    # Internal Work History
    validate_no_duplicate_rows(
        doc.internal_work_history,
        ["branch", "department", "designation", "from_date", "to_date"],
        "History In Company"
    )


    # ✅ Employee Suspension Period
    validate_no_duplicate_rows(
        doc.custom_employee_suspension_period,
        ["period_from", "period_to", "basic_salary_percentage"],
        "Employee Suspension Period"
    )

def validate_unique_deductions(doc,method):
    seen = set()

    for row in doc.custom_deduction:
        # Choose the field that defines uniqueness
        key = row.deduction  # change this field accordingly

        if key in seen:
            frappe.throw(f"Duplicate entry found in Salary Deduction: {key}")
        
        seen.add(key)

# ========================================
# UAN Number: Exactly 12 numeric digits
# ========================================
def validate_uan_number(doc, method):
    if doc.custom_uan_number:

        # Check if it's only digits AND exactly 12 in length
        if not doc.custom_uan_number.isdigit() or len(doc.custom_uan_number) != 12:
            frappe.throw(_("UAN Number must be exactly 12 numeric digits."))



def validate_person_to_be_contacted(doc, method):
    if doc.person_to_be_contacted:
    	print(";;;;;;;;;;;;;;;;;;;;;")
    	if not re.match(r'^[A-Za-z\s]+$', doc.person_to_be_contacted):
            frappe.throw("Only alphabets are allowed in Emergency Contact Name")
            
def validate_relation(doc, method):
    if doc.relation:
    	print(";;;;;;;;;;;;;;;;;;;;;")
    	if not re.match(r'^[A-Za-z\s]+$', doc.relation):
            frappe.throw("Only alphabets are allowed in Relation")
            
def validate_emergency_phone_number(doc, method):
    if not re.match(r'^(\+91)?[6-9]\d{9}$', doc.emergency_phone_number):
        frappe.throw("Invalid Emergency Phone")
        
# ========================================
# Aadhar Number: Exactly 12 numeric digits
# ========================================
def validate_aadhar_num(doc, method):
    if doc.custom_aadhar_number:

        # Check if it's only digits AND exactly 12 in length
        if not doc.custom_aadhar_number.isdigit() or len(doc.custom_aadhar_number) != 12:
            frappe.throw(_("Aadhar Number must be exactly 12 numeric digits."))
        

        if doc.custom_aadhar_number == doc.custom_uan_number:
            frappe.throw(_("Aadhar Number and UAN Number cannot be the same"))


# ============================
# Duplicate PAN card validate
# ============================
def validate_unique_pan(doc, method):
    if doc.pan_number:
        # Check if another employee has the same PAN
        duplicate_exists = frappe.db.exists("Employee", {
            "pan_number": doc.pan_number,
            "name": ["!=", doc.name] 
        })
        
        if duplicate_exists:
            frappe.throw(_("PAN Number {0} already exists for another employee. Duplicate PAN is not allowed.").format(doc.pan_number))
