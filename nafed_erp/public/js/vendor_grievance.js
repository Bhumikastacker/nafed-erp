// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Grievance', {

    setup: function(frm) {
        frm.set_query('vendor_id', function() {
            if (frappe.user_roles.includes('Vendor') && !frm.doc.raised_by_officer) {
                return { filters: { email_id: frappe.session.user } };
            }
            return { filters: { workflow_state: ['in', ['Active', 'HO Approved']] } };
        });
        if (frm.is_new() && frappe.user_roles.includes('Vendor')) {
            frappe.db.get_value('Vendor Registration',
                { email_id: frappe.session.user }, 'name',
                function(v) { if (v && v.name) frm.set_value('vendor_id', v.name); }
            );
        }
    },

    refresh: function(frm) {
        frm.trigger('control_field_visibility');
        frm.trigger('show_status_banner');
    },

    raised_by_officer: function(frm) {
        frm.set_value('vendor_id', '');
        frm.set_value('vendor_name', '');
        frm.set_df_property('vendor_id', 'hidden', 0);
        frm.set_df_property('vendor_id', 'read_only', 0);
        frm.refresh_field('vendor_id');
        if (frm.doc.raised_by_officer) {
            frappe.msgprint({ message: 'Please select the Vendor ID for whom you are raising this grievance.', indicator: 'blue' });
        }
    },

    vendor_id: function(frm) {
        if (!frm.doc.vendor_id) return;
        frappe.db.get_value('Vendor Registration', frm.doc.vendor_id,
            ['vendor_name', 'workflow_state'], function(v) {
                if (v) {
                    frm.set_value('vendor_name', v.vendor_name);
                    if (!['Active', 'HO Approved'].includes(v.workflow_state)) {
                        frappe.msgprint({ message: 'Warning: Vendor is not Active.', indicator: 'red' });
                    }
                }
            });
    },

    control_field_visibility: function(frm) {
        const roles = frappe.user_roles;
        const state = frm.doc.workflow_state || 'Draft';
        const is_vendor         = roles.includes('Vendor');
        const is_branch_officer = roles.includes('Branch Officer');
        const is_ho_admin       = roles.includes('HO Admin');
        const is_system_manager = roles.includes('System Manager') || roles.includes('Administrator');
        const after_submitted = ['Submitted','Under Review','Resolved','Reopened','HO Review','Closed'];
        const after_resolved  = ['Resolved','Reopened','HO Review','Closed'];
        const after_reopened  = ['Reopened','HO Review','Closed'];

        function show_field(f) {
            if (frm.fields_dict[f]) {
                frm.fields_dict[f].$wrapper.removeClass('hide-control').show();
                frm.set_df_property(f, 'hidden', 0);
            }
        }
        function hide_field(f) {
            if (frm.fields_dict[f]) {
                frm.fields_dict[f].$wrapper.addClass('hide-control').hide();
                frm.set_df_property(f, 'hidden', 1);
            }
        }
        function ro(f, val) { frm.set_df_property(f, 'read_only', val); }

        if (is_branch_officer || is_system_manager) {
            ['vendor_id','vendor_name','grievance_type','description','reference_documents',
             'invoices','delivery_notes','photos_as_supporting_proof','raised_by_officer',
             'sla_status','acknowledgement_deadline','resolution_deadline',
             'submission_date','fund_requisition_id'].forEach(show_field);
            if (after_submitted.includes(state)) {
                ['assigned_officer','initial_remarks','resolution_type','resolution_details',
                 'proposed_action','evidence_documents','resolution_date','resolved_by'].forEach(show_field);
            } else {
                ['assigned_officer','initial_remarks','resolution_type','resolution_details',
                 'proposed_action','evidence_documents','resolution_date','resolved_by'].forEach(hide_field);
            }
            if (after_resolved.includes(state)) {
                ['vendor_satisfaction','reopen_reason'].forEach(function(f){ show_field(f); ro(f,1); });
            } else {
                ['vendor_satisfaction','reopen_reason'].forEach(hide_field);
            }
            if (after_reopened.includes(state)) {
                ['ho_response','ho_closed_by','ho_closed_date'].forEach(show_field);
                if (!is_system_manager) ro('ho_response', 1);
            } else {
                ['ho_response','ho_closed_by','ho_closed_date'].forEach(hide_field);
            }
            ro('vendor_id', 1); ro('vendor_name', 1);
        }

        if (is_ho_admin) {
            ['vendor_id','vendor_name','grievance_type','description','reference_documents',
             'invoices','delivery_notes','photos_as_supporting_proof','raised_by_officer',
             'sla_status','acknowledgement_deadline','resolution_deadline','submission_date',
             'fund_requisition_id','assigned_officer','initial_remarks','resolution_type',
             'resolution_details','proposed_action','evidence_documents',
             'resolution_date','resolved_by'].forEach(show_field);
            if (after_resolved.includes(state)) {
                ['vendor_satisfaction','reopen_reason'].forEach(function(f){ show_field(f); ro(f,1); });
            } else {
                ['vendor_satisfaction','reopen_reason'].forEach(hide_field);
            }
            if (after_reopened.includes(state)) {
                ['ho_response','ho_closed_by','ho_closed_date'].forEach(show_field);
            } else {
                ['ho_response','ho_closed_by','ho_closed_date'].forEach(hide_field);
            }
            ['vendor_id','vendor_name','grievance_type','description',
             'resolution_type','resolution_details'].forEach(function(f){ ro(f,1); });
        }

        if (is_vendor) {
            ['vendor_id','vendor_name','grievance_type','description','reference_documents',
             'invoices','delivery_notes','photos_as_supporting_proof'].forEach(show_field);
            ['sla_status','acknowledgement_deadline','resolution_deadline','submission_date',
             'raised_by_officer','fund_requisition_id','assigned_officer','initial_remarks',
             'proposed_action','evidence_documents','resolution_date','resolved_by',
             'ho_closed_by','ho_closed_date'].forEach(hide_field);
            if (after_resolved.includes(state)) {
                ['resolution_type','resolution_details'].forEach(function(f){ show_field(f); ro(f,1); });
                show_field('vendor_satisfaction'); ro('vendor_satisfaction',1);
                show_field('reopen_reason'); ro('reopen_reason', after_reopened.includes(state)?1:0);
            } else {
                ['resolution_type','resolution_details','vendor_satisfaction','reopen_reason'].forEach(hide_field);
            }
            if (after_reopened.includes(state)) {
                show_field('ho_response'); ro('ho_response',1);
            } else {
                hide_field('ho_response');
            }
            if (state !== 'Draft') {
                ['vendor_id','vendor_name','grievance_type','description'].forEach(function(f){ ro(f,1); });
            }
            if (after_resolved.includes(state)) {
                [100,400,800].forEach(function(d){
                    setTimeout(function(){
                        ['vendor_satisfaction','reopen_reason'].forEach(function(f){
                            if (frm.fields_dict[f]) frm.fields_dict[f].$wrapper.removeClass('hide-control').show();
                        });
                        if (after_reopened.includes(state) && frm.fields_dict['ho_response'])
                            frm.fields_dict['ho_response'].$wrapper.removeClass('hide-control').show();
                    }, d);
                });
            }
        }
    },

    show_status_banner: function(frm) {
        frm.set_intro('');
        const cfg = {
            'Draft':        {c:'grey',   m:'Draft — fill details and submit your grievance'},
            'Submitted':    {c:'blue',   m:'Submitted — awaiting Branch Officer review'},
            'Under Review': {c:'purple', m:'Under review by Branch Officer'},
            'Resolved':     {c:'green',  m:'Resolved — select Vendor Satisfied or Vendor Not Satisfied from Actions. If not satisfied, fill Reopen Reason first.'},
            'Reopened':     {c:'orange', m:'Reopened — escalated to HO Admin'},
            'HO Review':    {c:'orange', m:'Under HO Admin review'},
            'Closed':       {c:'green',  m:'Grievance closed successfully'},
            'Rejected':     {c:'red',    m:'Rejected by Branch Officer'},
        };
        const s = cfg[frm.doc.workflow_state];
        if (s) frm.set_intro(s.m, s.c);
        if (frm.doc.sla_status === 'SLA Breached')
            frm.set_intro('SLA BREACHED — Immediate action required!', 'red');
    },

});
