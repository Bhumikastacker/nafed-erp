# import frappe
# from frappe.utils import nowdate, flt

# def set_current_fiscal_year(doc, method):
#     # Get today's date
#     today = nowdate()

#     # Find fiscal year for today
#     fiscal_year = frappe.db.get_value(
#         "Fiscal Year",
#         {"year_start_date": ("<=", today), "year_end_date": (">=", today)},
#         "name"
#     )

#     if fiscal_year:
#         doc.custom_fiscal_year = fiscal_year

# # def update_user_ids(doc, method):
# #     # Step 1: Get reports_to (manager employee ID)
# #     reports_to_emp = frappe.db.get_value("Employee", doc.employee, "reports_to")
# #     reviewer_to_emp = frappe.db.get_value("Employee", doc.employee, "custom_reviewing_officer")

# #     if not reports_to_emp:
# #         frappe.throw(f"Please set Reports To Officer in Employee:- {doc.employee} ")

# #     if not reviewer_to_emp:
# #         frappe.throw(f"Please set Reviewer Officer in Employee:- {doc.employee} ")

# #     if reports_to_emp:
# #         manager_user_id = frappe.db.get_value("Employee", reports_to_emp, "user_id")
# #         if not manager_user_id:
# #             frappe.throw(f"Please set User ID in Reports to officer in employee:- {reports_to_emp}")
# #         doc.custom_reports_to_used_id = manager_user_id

# #     if reviewer_to_emp:
# #         doc.custom_reviewing_to_used_id = reviewer_to_emp


# def calculate_section_abc_reporting(doc, method=None):
#     # ------------------------------------Section A--------------------------------------------------------
#     #report Auhtority calculation
#     rows_report_sec_A = []

#     for r in doc.custom_assessment_rating:
#         if r.reporting_authority is None:
#             r.reporting_authority= 0
        
#         if r.reporting_authority > 10:
#             frappe.throw("Section A Reporting Authority rating cannot be greater than 10")
#         rows_report_sec_A.append(r.reporting_authority)

#     if not rows_report_sec_A:
#         doc.custom_reporting_authority_section_a = 0
#         return
    
#     total = sum(rows_report_sec_A)
#     final_val = ((total * 40) / 100) / len(rows_report_sec_A)

#     doc.custom_reporting_authority_section_a = final_val

#     #reviewing authority calculation
#     rows_review_sec_A = []

#     for r in doc.custom_assessment_rating:
#         if r.reviewing_authorityrefer_para_2_of_part_5 is None:
#             r.reviewing_authorityrefer_para_2_of_part_5 = 0

#         if r.reviewing_authorityrefer_para_2_of_part_5 > 10:
#             frappe.throw("Section A Reviewing Authority rating cannot be greater than 10")
#         rows_review_sec_A.append(r.reviewing_authorityrefer_para_2_of_part_5)

#     if not rows_review_sec_A:
#         doc.custom_reviewing_authority_section_a = 0
#         return

#     total = sum(rows_review_sec_A)
#     final_val = ((total * 40) / 100) / len(rows_review_sec_A)

#     doc.custom_reviewing_authority_section_a = final_val

#     # ------------------------------------Section B--------------------------------------------------------
#     #report Auhtority calculation
#     rows_report_sec_B = []

#     for r in doc.custom_assessment_of_personal_attributes:
#         if r.reporting_authority is None:
#             r.reporting_authority= 0

#         if r.reporting_authority > 10:
#             frappe.throw("Section B Reporting Authority rating cannot be greater than 10")
#         rows_report_sec_B.append(r.reporting_authority)

#     if not rows_report_sec_B:
#         doc.custom_reporting_authority_section_b = 0
#         return

#     total = sum(rows_report_sec_B)
#     final_val = ((total * 40) / 100) / len(rows_report_sec_B)

#     doc.custom_reporting_authority_section_b = final_val

#     #reviewing authority calculation
#     rows_review_sec_B = []

#     for r in doc.custom_assessment_of_personal_attributes:
#         if r.reviewing_authorityrefer_para_2_of_part_5 is None:
#             r.reviewing_authorityrefer_para_2_of_part_5 = 0

#         if r.reviewing_authorityrefer_para_2_of_part_5 > 10:
#             frappe.throw("Section B Reviewing Authority rating cannot be greater than 10")
#         rows_review_sec_B.append(r.reviewing_authorityrefer_para_2_of_part_5)

#     if not rows_review_sec_B:
#         doc.custom_reviewing_authority_section_b = 0
#         return

#     total = sum(rows_review_sec_B)
#     final_val = ((total * 40) / 100) / len(rows_review_sec_B)

#     doc.custom_reviewing_authority_section_b = final_val

#     # ------------------------------------Section C--------------------------------------------------------
#     #report Auhtority calculation
#     rows_report_sec_C = []

#     for r in doc.custom_assessment_of_functional_competency:
#         if r.reporting_authority is None:
#             r.reporting_authority= 0

#         if r.reporting_authority > 10:
#             frappe.throw("Section C Reporting Authority rating cannot be greater than 10")
#         rows_report_sec_C.append(r.reporting_authority)


#     if not rows_report_sec_C:
#         doc.custom_reporting_authority_section_c = 0
#         return

#     total = sum(rows_report_sec_C)
#     final_val = ((total * 40) / 100) / len(rows_report_sec_C)

#     doc.custom_reporting_authority_section_c = final_val

#     #reviewing authority calculation
#     rows_review_sec_c = []

#     for r in doc.custom_assessment_of_functional_competency:
#         if r.reviewing_authorityrefer_para_2_of_part_5 is None:
#             r.reviewing_authorityrefer_para_2_of_part_5 = 0
            
#         if r.reviewing_authorityrefer_para_2_of_part_5 > 10:
#             frappe.throw("Section C Reviewing Authority rating cannot be greater than 10")
#         rows_review_sec_c.append(r.reviewing_authorityrefer_para_2_of_part_5)

#     if not rows_review_sec_c:
#         doc.custom_reviewing_authority_section_c = 0
#         return

#     total = sum(rows_review_sec_c)
#     final_val = ((total * 40) / 100) / len(rows_review_sec_c)

#     doc.custom_reviewing_authority_section_c = final_val

# def update_grade_value_in_reporting_reviewing(doc, method=None):
#     #------------------------update in tab 4 for reporting officer-------------------------------------------------
#     total_reporting = doc.custom_reporting_authority_section_a + doc.custom_reporting_authority_section_b + doc.custom_reporting_authority_section_c
#     doc.custom_numeric_rating = total_reporting

#     #------------------------update in tab 5 for review officer-------------------------------------------------
#     total_reviewing = doc.custom_reviewing_authority_section_a + doc.custom_reviewing_authority_section_b + doc.custom_reviewing_authority_section_c
#     doc.custom_numeric_grading_part_5 = total_reviewing