// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property", {
    zone: function(frm) {
        if (frm.doc.zone) {
            frm.set_value('branch', '');
            frm.fields_dict['branch'].get_query = function(doc) {
                return {
                    filters: {
                        'custom_zone': doc.zone 
                    }
                };
            };
            frm.refresh_field('branch');
        }
    },
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
             frm.add_custom_button(
                    __("Create Survey"),
                    () =>
                        frappe.set_route("List", "Property Survey", {
                            'property_id': frm.doc.name,
                            'survey_date': frappe.datetime.now_date()
                        }),
                    __("Take Action")
                );
                frm.add_custom_button(
                    __("Add Tax & Compliances"),
                    () =>
                        frappe.set_route("List", "Property Tax and Compliances", {
                            'property_id': frm.doc.name,
                        }),
                    __("Take Action")
                );
                frm.add_custom_button(
                    __("Add Financial Expenditure"),
                    () =>
                        frappe.set_route("List", "Property Financial Expenditures", {
                            'property_id': frm.doc.name,
                        }),
                    __("Take Action")
                );
                frm.add_custom_button(
                    __("Add Property Historical Brief"),
                    () =>
                        frappe.set_route("List", "Property Historical Brief", {
                            'property_id': frm.doc.name,
                        }),
                    __("Take Action")
                );
                frm.add_custom_button(
                    __("Title Verification"),
                    () =>
                        frappe.set_route("List", "Title Verification", {
                            'property_id': frm.doc.name,
                        }),
                    __("Take Action")
                );
        }
    }
});
