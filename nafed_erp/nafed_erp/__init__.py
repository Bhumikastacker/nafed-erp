__version__ = "0.0.2"
from hrms.hr.doctype.staffing_plan.staffing_plan import StaffingPlan
from nafed_erp.hire_to_retire.doc_events.staffing_plan import custom_set_job_requisitions
StaffingPlan.set_job_requisitions = custom_set_job_requisitions
