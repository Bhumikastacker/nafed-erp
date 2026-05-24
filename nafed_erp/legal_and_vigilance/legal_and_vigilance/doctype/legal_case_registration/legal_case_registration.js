// Copyright (c) 2026, CSM Technologies Pvt Ltd
// For license information, please see license.txt

frappe.ui.form.on("Legal Case Registration", {
    async refresh(frm) {
        frm.clear_custom_buttons();
       
        // ------------------------------------------------
        // REGISTER CASE (ONLY PLACE WHERE SAVE IS ALLOWED)
        // ------------------------------------------------
        if (frm.doc.status === 'Draft' ) {
            frm.add_custom_button(
                __('Register Case'),
                () => {
                    frm.set_value('status', 'Registered');
                    frm.save();
                },
                __('Actions')
            );
        }

        // ------------------------------------------------
        // ACTIONS FOR REGISTERED CASE
        // ------------------------------------------------
        if (frm.doc.status === 'Registered' ) {

            frm.add_custom_button(
                __('Link Child Case to This Case'),
                () => open_link_child_dialog(frm),
                __('Actions')
            );

            frm.add_custom_button(
                __('Assign Case to Law Firm'),
                () => open_assign_case_dialog(frm),
                __('Actions')
            );
            frm.add_custom_button(
                __('Schedule Hearing '),
                () => open_hearing_dialog(frm),
                __('Actions')
            );
            frm.add_custom_button(
                __('Update Case Status'),
                () => open_case_status_update_dialog(frm),
                __('Actions')
            );
           
           // =======================================================
            // ✅ FIXED: CASE OUTCOME RECORDING (NO REDIRECT)
            // =======================================================
            frm.add_custom_button(
                __('Case Outcome Recording'),
                () => open_outcome_recording_dialog(frm),
                __('Actions')
            );
        }
        // -------------------------------
        // NOTING SHEET BUTTON
        // -------------------------------
        if (frm.doc.status === "Registered") {

            frm.add_custom_button(
                __("Add Noting"),
                function () {

                    frappe.prompt(
                        [
                            {
                                fieldname: "remark_text",
                                fieldtype: "Text Editor",
                                label: "Add Noting",
                                reqd: 0
                            }
                        ],
                        function(values) {

                            let text = $("<div>").html(values.remark_text).text().trim();

                            if (!text) {
                                frappe.msgprint({
                                    title: __("Validation Error"),
                                    message: __("Please add some noting. Empty not allowed."),
                                    indicator: "red"
                                });
                                return;
                            }

                            let row = frm.add_child("remarks");

                            row.action_taken_by = frappe.session.user;
                            row.action_taken_on = frappe.datetime.get_today();
                            row.remarks = values.remark_text;

                            frm.refresh_field("remarks");
                            frm.save().then(() => {
                                // set_noting_permissions(frm);
                            });
                        },
                        __("Noting"),
                        __("Submit")
                    );
                },
                __("Actions")
            );
        }
        
        ensure_view_mode(frm);
        load_case_hierarchy(frm);
        load_case_timeline(frm);
        load_case_documents(frm);
    },

    view_mode(frm) {
        load_case_timeline(frm);
        load_case_documents(frm);
    }
});
// =======================================================
// CASE OUTCOME RECORDING (CUSTOM QUICK ENTRY, NO NAVIGATION)
// =======================================================
function open_outcome_recording_dialog(frm) {
    frappe.prompt(
        [
            {
                fieldname: 'outcome_type',
                fieldtype: 'Select',
                label: 'Outcome Type',
                options: '\nJudgment\nSettlement\nWithdrawal\nOther',
                reqd: 1
            },
            {
                fieldname: 'custom_outcome_type',
                fieldtype: 'Data',
                label: 'Specify Outcome Type',
                depends_on: 'eval:doc.outcome_type == "Other"',
                reqd: 0
            },
            {
                fieldname: 'outcome_date',
                fieldtype: 'Date',
                label: 'Outcome Date',
                default: frappe.datetime.nowdate(),
                reqd: 1
            },
            {
                fieldname: 'settlement_amount',
                fieldtype: 'Currency',
                label: 'Reward / Settlement Amount',
                depends_on: 'eval:doc.outcome_type == "Settlement"'
            }
        ],
        (values) => {
            frappe.call({
                method: 'nafed_erp.legal_and_vigilance.doctype.case_outcome_recording_and__closure_processing.case_outcome_recording_and__closure_processing.create_outcome_with_hearing_1',
                args: {
                    case_id: frm.doc.name,
                    outcome_type: values.outcome_type,
                    other_outcome_type:
                        values.outcome_type === "Other"
                            ? values.custom_outcome_type || null
                            : null,
                    outcome_date: values.outcome_date,
                    settlement_amount: values.settlement_amount || 0
                },
                callback() {
                    frappe.show_alert({
                        message: __('Outcome recorded successfully'),
                        indicator: 'green'
                    });

                    // Stay on same form
                    load_case_timeline(frm);
                }
            });
        },
        __('Case Outcome Recording'),
        __('Save')
    );
}

// =======================================================
// UC_LEG_007 + UC_LEG_008 — UPDATE CASE STATUS (CORRECT)
// =======================================================
function open_case_status_update_dialog(frm) {
    frappe.prompt(
        [
            
            {
                fieldname: 'case_status',
                fieldtype: 'Select',
                label: 'Case Status',
                options: 'In Progress\nAwaiting Order\nHearing Completed\nCompliance Pending\nOther',
                default: frm.doc.case_status,
                reqd: 1
            },
            {
                fieldname: 'other_case_status',
                fieldtype: 'Data',
                label: 'Specify Case Status',
                depends_on: 'eval:doc.case_status == "Other"',
                reqd: 0
            },
            {
                fieldname: 'description',
                fieldtype: 'Small Text',
                label: 'Description',
                reqd: 1
            }
        ],
        (values) => {
            if (values.case_status === "Other") {
                values.other_case_status = values.other_case_status
                    ? values.other_case_status.trim()
                    : null;
            } else {
                values.other_case_status = null;
            }
            frappe.call({
                method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_registration.legal_case_registration.update_case_status',
                args: {
                    case_id: frm.doc.name,
                    case_status: values.case_status,
                    other_case_status: values.other_case_status,
                    description: values.description
                },
                callback() {
                    frappe.show_alert({
                        message: __('Case status updated successfully'),
                        indicator: 'green'
                    });

                    // NO save, NO reload
                    load_case_timeline(frm);
                }
            });
        },
        __('Update Case Status'),
        __('Update')
    );
}

// =======================================================
// LINK CHILD CASE
// =======================================================
function open_link_child_dialog(frm) {
    frappe.prompt(
        [
            {
                fieldname: 'child_case',
                fieldtype: 'Link',
                label: 'Child Case',
                options: 'Legal Case Registration',
                reqd: 1
            },
            {
                fieldname: 'link_type',
                fieldtype: 'Select',
                label: 'Link Type',
                options: 'Appeal\nRelated\nExecution\nOther',
                reqd: 1
            },
            {
                fieldname: 'other_link_type',
                fieldtype: 'Data',
                label: 'Specify Other',
                depends_on: 'eval:doc.link_type=="Other"',
                reqd: 0
            }

        ],
        (values) => {
            frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'Legal Case Link',
                        parent_case: frm.doc.name,
                        child_case: values.child_case,
                        link_type: values.link_type,  // ✅ always valid
                        other_link_type: values.link_type === "Other"
                            ? values.other_link_type
                            : null,
                        status: 'Active'
                    }
                },
                callback() {
                    frappe.show_alert({
                        message: __('Child case linked successfully'),
                        indicator: 'green'
                    });
                    load_case_hierarchy(frm);
                }
            });
        },
        __('Link Child Case'),
        __('Create Link')
    );
}

// =======================================================
// ASSIGN CASE
// =======================================================
function open_assign_case_dialog(frm) {

    let d = frappe.prompt(
        [
            {
                fieldname: 'lawyer',
                fieldtype: 'Link',
                label: 'Law Firm ',
                options: 'Legal Advocates',
                reqd: 1,
            },
                // onchange: function () {
                //     let lawyer = d.get_value('lawyer');

    //                 if (lawyer) {
    //                     frappe.db.get_value(
    //                         'Legal Advocates',
    //                         lawyer,
    //                         'advocate_type',
    //                         (r) => {
    //                             if (r && r.advocate_type) {
    //                                 d.set_value('advocate_type', r.advocate_type);
    //                             }
    //                         }
    //                     );
    //                 } else {
    //                     d.set_value('advocate_type', null);
    //                 }
    //             }
    //         },

            

            {
                fieldname: 'permission_start_date',
                fieldtype: 'Date',
                label: 'Permission Start Date',
                default: frappe.datetime.nowdate(),
                reqd: 1
            },

            {
                fieldname: 'delegation_status',
                fieldtype: 'Select',
                label: 'Delegation Status',
                options: 'Primary\nDelegated',
                default: 'Primary'
            },
            {
                fieldname: 'remarks',
                fieldtype: 'Small Text',
                label: 'Remarks'
            }
        ],
        (values) => {
            frappe.call({
                method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_assignment.legal_case_assignment.assign_case',
                args: {
                    case_id: frm.doc.name,
                    lawyer: values.lawyer,
                    

                    permission_start_date: values.permission_start_date,
                    delegation_status: values.delegation_status,
                    remarks: values.remarks
                },
                callback() {
                    frappe.show_alert({
                        message: __('Case assigned successfully'),
                        indicator: 'green'
                    });
                    frm.reload_doc();
                }
            });
        },
        __('Assign Case'),
        __('Assign')
    );
}

// =======================================================
// SCHEDULE HEARING
// ======================================================
function open_hearing_dialog(frm) {
    frappe.prompt(
        [
            {
                fieldname: 'hearing_date',
                fieldtype: 'Date',
                label: 'Hearing Date',
                reqd: 1
            },
            {
                fieldname: 'has_next_hearing',
                fieldtype: 'Check',
                label: 'Has Next Hearing?'
            },
            {
                fieldname: 'next_hearing_date',
                fieldtype: 'Date',
                label: 'Next Hearing Date',
                depends_on: 'eval:doc.has_next_hearing == 1',
                mandatory_depends_on: 'eval:doc.has_next_hearing == 1'
            },
            {
                fieldname: 'hearing_type',
                fieldtype: 'Select',
                label: 'Hearing Type',
                options: 'Admission\nArgument\nFinal\nCompliance\nOther',
                reqd: 1
            },
            {
                fieldname: 'other_hearing_type',
                fieldtype: 'Data',
                label: 'Specify Hearing Type',
                depends_on: 'eval:doc.hearing_type == "Other"',
                reqd: 0
            },
            {
                fieldname: 'venue',
                fieldtype: 'Data',
                label: 'Court / Venue',
                default: frm.doc.jurisdiction || '',
                reqd: 1
            },
            {
                fieldname: 'advocate',
                fieldtype: 'Link',
                label: 'Advocate',
                options: 'Legal Advocates',
                default: frm.doc.assigned_advocate || '',
                reqd: 1
            },
            {
                fieldname: 'remarks',
                fieldtype: 'Small Text',
                label: 'Remarks'
            }
            
        ],
        (values) => {
            if (values.has_next_hearing === 1) {

                if (!values.next_hearing_date) {
                    frappe.throw(__('Next Hearing Date is required'));
                }

                const hearing_date =
                    frappe.datetime.str_to_obj(values.hearing_date);
                const next_hearing_date =
                    frappe.datetime.str_to_obj(values.next_hearing_date);

                if (next_hearing_date <= hearing_date) {
                    frappe.throw(__('Next Hearing Date must be after Hearing Date'));
                }
            }
            if (values.hearing_type === "Other") {
                values.other_hearing_type = values.other_hearing_type
                ? values.other_hearing_type.trim()
                : null;
            } else {
                values.other_hearing_type = null;
            }
            frappe.call({
                method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_hearing.legal_case_hearing.schedule_hearing',
                args: {
                    case_id: frm.doc.name,
                    ...values
                },
                callback() {
                    frappe.show_alert({
                        message: __('Hearing scheduled successfully'),
                        indicator: 'green'
                    });
                }
            });
        },
        __('Schedule Hearing'),
        __('Schedule')
    );
}
// =======================================================
// VIEW MODE
// =======================================================
function ensure_view_mode(frm) {
    if (!frm.doc.view_mode) {
        frm.doc.view_mode = 'Individual';
        frm.refresh_field('view_mode');
    }
}

// =======================================================
// PARENT / CHILD VIEW
// =======================================================
function load_case_hierarchy(frm) {
    frappe.call({
        method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_link.legal_case_link.get_case_hierarchy',
        args: { case_id: frm.doc.name },
        callback(r) {
            let html = '';

            if (r.message?.parent) {
                html += `<p><b>Parent Case:</b> <a href="/app/legal-case-registration/${r.message.parent}">${r.message.parent}</a></p>`;
            }

            if (r.message?.children?.length) {
                html += '<p><b>Child Cases:</b></p><ul>';
                r.message.children.forEach(child => {
                    html += `<li><a href="/app/legal-case-registration/${child.case_id}">${child.case_id}</a> <span class="text-muted">(${child.link_type})</span></li>`;
                });
                html += '</ul>';
            }

            if (!html) html = '<p class="text-muted">No related cases</p>';

            frm.fields_dict.related_cases_html.$wrapper.html(html);
        }
    });
}

// =======================================================
// TIMELINE
// =======================================================
function load_case_timeline(frm) {
    frappe.call({
        method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_link.legal_case_link.get_case_timeline',
        args: { case_id: frm.doc.name, view_mode: frm.doc.view_mode },
        callback(r) {
            let html = '<ul class="case-timeline">';
            (r.message || []).forEach(row => {
                html += `<li><b>${row.creation}</b> : ${row.communication_type || 'Note'} - ${row.subject || ''} <span class="text-muted">[${row.case_id}]</span></li>`;
            });
            html += '</ul>';
            frm.fields_dict.case_timeline_html.$wrapper.html(html);
        }
    });
}

// =======================================================
// DOCUMENTS
// =======================================================
function load_case_documents(frm) {
    frappe.call({
        method: 'nafed_erp.legal_and_vigilance.doctype.legal_case_link.legal_case_link.get_case_documents',
        args: { case_id: frm.doc.name, view_mode: frm.doc.view_mode },
        callback(r) {
            let html = '<ul class="case-documents">';
            (r.message || []).forEach(file => {
                html += `<li><a href="${file.file_url}" target="_blank">${file.file_name}</a> <span class="text-muted">[${file.attached_to_name}]</span></li>`;
            });
            html += '</ul>';
            frm.fields_dict.case_documents_html.$wrapper.html(html);
        }
    });
}
