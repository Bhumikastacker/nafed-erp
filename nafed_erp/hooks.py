app_name = "nafed_erp"
app_title = "Nafed ERP"
app_publisher = "CSM Technologies Pvt Ltd"
app_description = "Nafed ERP"
app_email = "contact@csmtech.com"
app_license = "mit"
app_logo_url = "/assets/nafed_erp/images/nafed.jpg"

website_context = {
    "favicon": "/assets/nafed_erp/images/favicon.png",
    "splash_image": "/assets/nafed_erp/images/logo.png",
}
 
# ------------------
# Desk Includes
# ------------------
 
# app_include_css = [
#     "nafed_erp.bundle.css",
# ]
app_include_css = [
    "/assets/nafed_erp/css/nafed_erp.css",
    "/assets/nafed_erp/css/nafed_light.css",
    "/assets/nafed_erp/css/nafed_dark.css"
    # "/assets/nafed_erp/css/top_menu.css",
]
app_include_js = ["nafed_erp.bundle.js",
                  "assets/nafed_erp/js/addons.js",
                  "assets/nafed_erp/js/global_submit_popup.js",
                  "assets/nafed_erp/js/global_noting_sheet.js"]
                #   "/assets/nafed_erp/js/pos_override.js"]
                

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "nafed_erp",
# 		"logo": "/assets/nafed_erp/logo.png",
# 		"title": "Nafed ERP",
# 		"route": "/nafed_erp",
# 		"has_permission": "nafed_erp.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nafed_erp/css/light_green.css"
# app_include_js = "/assets/nafed_erp/js/nafed_erp.js"

# include js, css files in header of web template
# web_include_css = "/assets/nafed_erp/css/light_green.css"
# web_include_js = "/assets/nafed_erp/js/nafed_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nafed_erp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views


# ------------------
# Page JS
# ------------------

page_js = {
    "organizational-chart": "public/js/organizational_chart_override.js"
    
}

# ------------------
# Doctype JS
# ------------------

doctype_js = {
    "Employee Checkin": "public/js/employee_checkin.js",
    "Leave Encashment": "public/js/leave_encashment.js",
    "Employee": "public/js/employee.js",
    "Employee Grade": "public/js/employee_grade.js",
    "Account": "public/js/account_custom.js",
    "Account Update Request": "public/js/account_update_request.js",
    "Payroll Entry": "public/js/payroll_entry.js",
    "Company": "public/js/company.js",
    "Travel Request": "public/js/travel_request.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Expense Claim": "public/js/expense_claim.js",
    "Staffing Plan": "public/js/staffing_plan.js",
    "Job Requisition": "public/js/job_requisition.js",
    "Leave Application": "public/js/leave_application.js",
    "Employee Separation": "public/js/employee_sepration.js",
    "Job Opening": "public/js/job_opening.js",
    "Interview": "public/js/interview.js",
    "Job Applicant": "public/js/job_applicant.js",
    "Project": "public/js/project.js",
    "Task": "public/js/task.js",
    "Supplier": "public/js/supplier.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "Appraisal": "public/js/appraisal.js",
    "leave_allocation": "public/js/leave_allocation.js",
    "Budget": "public/js/budget.js",
    "loan product": "public/js/loan_product.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Sales Order": "public/js/sales_order.js",
    "Quotation": "public/js/quotation.js",
    "Loan Application": "public/js/loan_application.js",
    "Material Request": "public/js/material_request.js",
    "Salary Structure": "public/js/salary_structure.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Goal": "public/js/goal.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Customer": "public/js/customer.js",
    "Request for Quotation": "public/js/request_for_quotation.js",
    "Material Request": "public/js/material_request.js",
    "Stock Entry": "public/js/stock_entry.js",
    "Purchase Receipt": ["public/js/purchase_receipt.js"]
                        #   "public/js/purchase_receipt_dashboard.js"]
}
doctype_list_js = {
    "Material Request": "public/js/material_request_list.js"
}

# ------------------
# Icons
# ------------------
app_include_icons = [
    "nafed_erp/icons/symbol/procure-to-pay.svg",
    "nafed_erp/icons/symbol/order-management.svg",
    "nafed_erp/icons/symbol/hire-to-retire.svg",
    "nafed_erp/icons/symbol/finance-and-accounts.svg",
    "nafed_erp/icons/symbol/estates.svg",
    "nafed_erp/icons/symbol/information-technology.svg",
    "nafed_erp/icons/symbol/project-management.svg",
    "nafed_erp/icons/symbol/legal-and-vigilance.svg",
    "nafed_erp/icons/symbol/meeting-and-coordination.svg",
    "nafed_erp/icons/symbol/extension-and-bd.svg",
    "nafed_erp/icons/symbol/production.svg",
    "nafed_erp/icons/symbol/erp-next-integrations.svg",
    "nafed_erp/icons/symbol/nafed-erp-dashboard.svg",
    "nafed_erp/icons/symbol/loans.svg",
    "nafed_erp/icons/symbol/visitors.svg",
    "nafed_erp/icons/symbol/import-and-export.svg",
 
]


# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "nafed_erp.utils.jinja_methods",
# 	"filters": "nafed_erp.utils.jinja_filters"
# }

fixtures = [
    # {"dt": "Property Setter"}]
# {"doctype": "Custom HTML Block"},
# # # 	{"doctype": "DocType", "filters": [["name", "in", ["User"]]]},
# # #     {"doctype": "Document Naming Rule", "filters": [["document_type", "in", ["Property Survey"]]]}
    # {"dt": "Workflow"},
    # {"dt": "Workflow Action Master"},
    # {"dt": "Workflow State"},
    # {"dt": "Role"},
#  {"dt": "Translation"},

# #     # {"dt": "Client Script"}
    
# #     # {
# #     #     "dt": "Notification",
# #     #     "filters": [
# #     #         ["name", "in", ["Probition period Notification", "HR Notification", "Salary Requisition"]]
# #     #     ]
# #     # }
# #     # ,
# #     # {"doctype": "Document Naming Rule", "filters": [["document_type", "in", ["Property Survey"]]]}

# #     # {"dt": "Server Script"},
# #     # {"dt": "Notification", "filters": [["name", "=", "Probition period Notification"]]}

]

fixtures = [
    {"dt": "Property Setter"},
    {"dt": "Client Script"},
    {"dt": "Server Script"}
]


# Installation
# ------------

# before_install = "nafed_erp.install.before_install"
# after_install = "nafed_erp.install.nafed_custom_html_block_data.after_install"

# Uninstallation
# ------------

# before_uninstall = "nafed_erp.uninstall.before_uninstall"
# after_uninstall = "nafed_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "nafed_erp.utils.before_app_install"
# after_app_install = "nafed_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "nafed_erp.utils.before_app_uninstall"
# after_app_uninstall = "nafed_erp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nafed_erp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes


# ------------------
# Override Classes
# ------------------

override_doctype_class = {
    "Payroll Entry": "nafed_erp.finance_and_accounts.doc_events.payroll_entry.CustomPayrollEntry",
    "Loan": "nafed_erp.pf_trust.overrides.loan.CustomLoan",
    "Loan Application": "nafed_erp.pf_trust.overrides.loan_application.CustomLoanApplication"
}

# ------------------
# Document Events
# ------------------

doc_events = {

    # "Nafed Training Meeting": {
    #     "after_insert": "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.add_meeting_link_comment",
    #     "on_update": "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.add_meeting_link_comment"
    # },

    # "Training Requisition": {
    #     "validate": "nafed_erp.overrides.training_requisition.validate_employee_details"
    # },

    "Training Session": {
        "on_submit": "nafed_erp.hire_to_retire.doctype.training_session.training_session.send_invites"
    },

    "Employee": {
        "validate": [
            "nafed_erp.hire_to_retire.doc_events.employee.validate",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_reports_to",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_age",
            "nafed_erp.hire_to_retire.doc_events.employee.update_user_permission",
           # "nafed_erp.hire_to_retire.doc_events.employee.validate_dates",
            # "nafed_erp.hire_to_retire.doc_events.employee.validate_pf_distribution",
            "nafed_erp.overrides.employee.validate_employee_name",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_unique_deductions",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_uan_number",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_aadhar_num",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_unique_pan",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_person_to_be_contacted",
            "nafed_erp.hire_to_retire.doc_events.employee.validate_relation",
        ],
       # "on_update": "nafed_erp.hire_to_retire.doc_events.employee_retirement.create_employee_separation_on_retirement"
    },

    "Employee Category": {
        "validate": "nafed_erp.hire_to_retire.doc_events.employee_category.validate_category_name"
    },

    "Employee Transfer": {
        "validate": "nafed_erp.hire_to_retire.doc_events.employee_transfer.validate_transfer_date"
    },

    "Leave Application": {
        "validate": "nafed_erp.hire_to_retire.doc_events.leave_application.validate",
        "on_submit": "nafed_erp.hire_to_retire.doc_events.leave_application.on_submit_status_validation"
    },

    "Attendance": {
        "on_submit": "nafed_erp.hire_to_retire.doc_events.attendance.process_leave_rules"
    },

    "Leave Encashment": {
        "validate": [
            "nafed_erp.hire_to_retire.doc_events.leave_encashment.set_encashment_amount",
            "nafed_erp.hire_to_retire.doc_events.leave_encashment.set_encashment_year_on_save"
        ],
        "before_submit": "nafed_erp.hire_to_retire.doc_events.leave_encashment.set_encashment_date"
    },

    "Leave Policy Assignment": {
        "validate": "nafed_erp.hire_to_retire.doc_events.leave_policy_assignment.validate_assignment_dates"
    },

    "Payment Entry": {
        "on_submit": [
            "nafed_erp.hire_to_retire.doc_events.payment_entry.update_payment_entry_id",
            "nafed_erp.admin.doc_events.payment_entry.update_payment_related_status",
            "nafed_erp.hire_to_retire.doctype.branch_payment_request.branch_payment_request.update_payment_request_status"
        ]
    },

    # "Appraisal": {
    #     "before_save": [
    #         # "nafed_erp.hire_to_retire.doc_events.appraisal.set_current_fiscal_year",
    #         # "nafed_erp.hire_to_retire.doc_events.appraisal.update_user_ids",
    #         # "nafed_erp.hire_to_retire.doc_events.appraisal.calculate_section_abc_reporting",
    #         # "nafed_erp.hire_to_retire.doc_events.appraisal.update_grade_value_in_reporting_reviewing"
    #     ]
    # },

    "Travel Request": {
        "on_submit": "nafed_erp.hire_to_retire.doc_events.travel_request.fill_submission_date",
        "validate": [
            "nafed_erp.hire_to_retire.doc_events.travel_request.set_total_minutes",
            "nafed_erp.hire_to_retire.doc_events.travel_request.validate_advance_amount",
            "nafed_erp.hire_to_retire.doc_events.travel_request.validate_travel_request_ltc_period"
        ],
        "on_cancel": "nafed_erp.hire_to_retire.doc_events.travel_request.cancel_linked_employee_advance"
    },

    "Payroll Entry": {
        "validate": "nafed_erp.finance_and_accounts.doc_events.payroll_entry.validate_payroll_creation",
        "on_submit": "nafed_erp.finance_and_accounts.doc_events.payroll_entry.automate_payroll_entry_for_all_child_companies"
    },

    "Interview": {
        "on_submit": "nafed_erp.hire_to_retire.doc_events.interview.validate_interview_feedback",
        "validate": [
            "nafed_erp.hire_to_retire.doc_events.interview.validate_scheduled_on_date",
            "nafed_erp.hire_to_retire.doc_events.interview.validate_interview_time"
        ]
    },
    
    "Interview Type": {
        "validate": "nafed_erp.hire_to_retire.doc_events.interview_type.validate_interview_type_name",
        "before_rename": "nafed_erp.hire_to_retire.doc_events.interview_type.validate_interview_type_name"
    },

    "Expense Claim": {
        "on_submit": "nafed_erp.hire_to_retire.doc_events.expense_claim.set_expense_claim_reference_in_travel_request",
        "on_cancel": "nafed_erp.hire_to_retire.doc_events.expense_claim.remove_expense_claim_reference_in_travel_request"
    },

    "Task": {
        "validate": "nafed_erp.project_management.doc_events.task.validate"
    },

    "Project": {
        "validate": "nafed_erp.project_management.doc_events.project.validate"
    },

    "Employee Separation": {
        "validate": "nafed_erp.hire_to_retire.doc_events.employee_sepration.validate",
        "before_submit": "nafed_erp.hire_to_retire.doc_events.employee_sepration.before_submit"
    },

    "Salary Component": {
        "validate": "nafed_erp.pf_trust.doc_events.salary_component.validate"
    },

    "Journal Entry": {
        "on_submit": "nafed_erp.pf_trust.doc_events.journal_entry.on_journal_entry_submit"
    },

    "Sales Order": {
        "on_submit": "nafed_erp.admin.doc_events.sales_order.sales_order_on_submit"
    },

    "Supplier": {
        "after_insert": "nafed_erp.admin.doc_events.supplier.disable_supplier"
    },

    "Purchase Receipt": {
        "on_submit": ["nafed_erp.admin.doc_events.purchase_receipt.purchase_receipt_on_submit_all",
        "nafed_erp.admin.doc_events.purchase_receipt.update_batch_expiry_from_pr"]
    },

    "Purchase Invoice": {
        "validate": "nafed_erp.project_management.doc_events.project.validate_purchase_invoice",
        "on_submit": ["nafed_erp.project_management.doc_events.project.update_billing_on_submit",
                     "nafed_erp.admin.doc_events.purchase_invoice.update_dispatch_receipt_invoice"],
        "on_cancel": "nafed_erp.project_management.doc_events.project.revert_billing_on_cancel"
    },

    "Supplier Group": {
        "validate": "nafed_erp.pf_trust.doc_events.supplier_group.validate"
    },

    "Loan Application": {
        "validate": "nafed_erp.pf_trust.doc_events.loan_application.validate"
    },
    "Item": {
        "after_insert": "nafed_erp.production.doc_events.item.create_service_item_for_subcontracting"
    },
    "BOM": {
        "on_submit": "nafed_erp.production.doc_events.bom.create_subcontracting_bom"
    },
    "Vendor Registration": {
        "on_update_after_submit": "nafed_erp.procure_to_pay.doctype.vendor_registration.vendor_registration.on_update_after_submit"
    },
    
    "Salary Slip": {
        "validate": "nafed_erp.finance_and_accounts.doc_events.salary_slip.fetch_employee_deductions",
        "on_submit": "nafed_erp.finance_and_accounts.doc_events.salary_slip.fix_ytd_mtd_after_submit"
    },

    "Job Opening": {
        "validate": "nafed_erp.hire_to_retire.doc_events.job_opening.validate"
    },
    
    "Job Applicant": {
        "validate": "nafed_erp.hire_to_retire.doc_events.job_applicant.validate"
    },

    "Goal": {
        "validate": "nafed_erp.hire_to_retire.doc_events.goal.validate_goal_dates"
    },

    # "Seed Certification": {
    #     "on_update": "nafed_erp.procure_to_pay.doctype.seed_certification.seed_certification.on_update"
    # }
    "Dispatch Details": {
    "on_submit": "nafed_erp.procure_to_pay.doctype.dispatch_details.dispatch_details.update_jwo_dispatch_status"
},
    "Sales Invoice": {
        "on_submit": "nafed_erp.procure_to_pay.api.sales_invoice.update_jwo_invoice_status"
    },
    "Request for Quotation": {
        "validate": ["nafed_erp.procure_to_pay.doc_events.request_for_quotation.validate_suppliers",
                     "nafed_erp.procure_to_pay.doc_events.request_for_quotation.validate_unique_supplier_emails"],
        "on_submit": "nafed_erp.procure_to_pay.doc_events.request_for_quotation.on_submit_send_web_form"
    },
     "Stock Entry": {
        "validate": "nafed_erp.procure_to_pay.api.stock_entry.calculate_indent_data"
    }


}

# ------------------
# Scheduler
# ------------------

scheduler_events = {

    "daily": [
        "frappe.email.doctype.notification.notification.trigger_daily_alerts",
        "nafed_erp.hire_to_retire.doctype.confirmation_letter.confirmation_letter.create_daily_confirmation_letters",
        "nafed_erp.finance_and_accounts.scheduled_tasks.company.custom_auto_period_closing_voucher_creation",
        "nafed_erp.procure_to_pay.api.fumigation_alert.send_due_alerts",
        "nafed_erp.procure_to_pay.api.fumigation_alert.update_overdue_treatments"
    ],

    "hourly": [
        "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.update_trainer_availability"
    ],

    "cron": {

        "0 10 * * *": [
            "nafed_erp.hire_to_retire.doc_events.sql_attendance_sync.fetch_and_create_employee_checkin"
        ],

        "0 15 * * *": [
            "nafed_erp.hire_to_retire.doc_events.sql_attendance_sync.fetch_and_create_employee_checkin"
        ],

        "*/30 * * * *": [
            "nafed_erp.e_samridhi_background_jobs.scheduler.run_esamridhi_jobs"
        ],

        "0 8 * * *": [
            "nafed_erp.procure_to_pay.doctype.vendor_amendment_request.vendor_amendment_request.auto_expire_stale_requests"
        ],

        "0 6 1 * *": [
            "nafed_erp.procure_to_pay.doctype.vendor_performance_record.vendor_performance_record.auto_initiate_monthly_evaluation"
        ],
         "*/5 * * * *": [
            "nafed_erp.procure_to_pay.doctype.price_discovery.price_discovery.run_price_discovery_scheduler"
        ]
    }

}

# ------------------
# Overrides
# ------------------

override_whitelisted_methods = {
    "frappe.core.doctype.user.user.switch_theme": "nafed_erp.override.switch_theme",
    "hrms.hr.page.organizational_chart.organizational_chart.get_children": "nafed_erp.override.get_children1",
    "hrms.utils.hierarchy_chart.get_all_nodes": "nafed_erp.override.get_all_nodes1",
    "frappe.desk.search.get_link_title": "nafed_erp.override.get_link_title_guest",

}

override_doctype_dashboards = {
    "Staffing Plan": "nafed_erp.hire_to_retire.doc_events.staffing_plan.get_data"
}

# ------------------
# Monkey Patches
# ------------------

import nafed_erp.hire_to_retire.patches.leave_application
import nafed_erp.hire_to_retire.patches.payroll_entry

# ------------------
# After Migrate
# ------------------

# after_migrate = "nafed_erp.hire_to_retire.doc_events.hr_settings.create_custom_fields"
after_migrate = [
    "nafed_erp.hire_to_retire.doc_events.hr_settings.create_custom_fields",
    "nafed_erp.utils.noting_sheet.add_noting_sheet_to_all_modules",
    "nafed_erp.utils.noting_sheet.remove_noting_sheet_from_auction"
]

import hrms.payroll.doctype.salary_slip.salary_slip_loan_utils as loan_salary_utils 
import nafed_erp.pf_trust.overrides.loan_override as loan_company_bypass



loan_salary_utils._get_loan_details = loan_company_bypass.custom_get_loan_details


# hooks.py — add this
# doc_events = {
#     "Payment Entry": {
#         "on_submit": "nafed_erp.procure_to_pay.doctype.incidental_claim.incidental_claim.on_payment_submit",
#         "on_cancel": "nafed_erp.procure_to_pay.doctype.incidental_claim.incidental_claim.on_payment_cancel"
#     }
# }
