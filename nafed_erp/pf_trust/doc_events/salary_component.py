import frappe

def validate(doc, method):
    validate_single_pf_flag_in_document(doc)
    validate_unique_pf_components_system_wide(doc)


def validate_single_pf_flag_in_document(doc):
    """
    Ensure only ONE PF checkbox is selected
    within the same Salary Component
    """
    selected_flags = sum([
        bool(doc.custom_is_employee_pf_component),
        bool(doc.custom_is_employer_pf_component),
        bool(doc.custom_is_voluntary_pf_component),
    ])

    if selected_flags > 1:
        frappe.throw(
            "Only one PF component checkbox can be selected in a Salary Component"
        )


def validate_unique_pf_components_system_wide(doc):
    """
    Ensure only ONE Salary Component exists
    for each PF type across the system
    """
    pf_flags = {
        "custom_is_employee_pf_component": "Employee",
        "custom_is_employer_pf_component": "Employer",
        "custom_is_voluntary_pf_component": "Voluntary",
    }

    for field, label in pf_flags.items():
        if doc.get(field):
            exists = frappe.db.exists(
                "Salary Component",
                {
                    field: 1,
                    "name": ["!=", doc.name]
                }
            )

            if exists:
                frappe.throw(
                    f"Only one Salary Component can be marked as {label} PF Component"
                )


@frappe.whitelist()
def get_salary_component_custom(doctype, txt, searchfield, start, page_len, filters):
    sc = frappe.qb.DocType("Salary Component")
    sca = frappe.qb.DocType("Salary Component Account")

    conditions = (
        (sc.type == filters.get("component_type"))
        & (sc.disabled == 0)
        & (sc[searchfield].like(f"%{txt}%") | sc.name.like(f"%{txt}%"))
    )

    # ✅ Add your custom filter
    if "custom_is_additional_deduction_component" in filters:
        conditions = conditions & (
            sc.custom_is_additional_deduction_component
            == filters.get("custom_is_additional_deduction_component")
        )

    salary_components = (
        frappe.qb.from_(sc)
        .left_join(sca)
        .on(sca.parent == sc.name)
        .select(sc.name, sca.account, sca.company)
        .where(conditions)
        .limit(page_len)
        .offset(start)
    ).run(as_dict=True)

    accounts = []
    for component in salary_components:
        if not component.company:
            accounts.append((component.name, component.account, component.company))
        else:
            if component.company == filters.get("company"):
                accounts.append((component.name, component.account, component.company))

    return accounts