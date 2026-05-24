// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Requisition", {
    refresh(frm) {
        // Filter Account field based on Branch
        frm.set_query("debit_account", function() {
            return {
                filters: {
                    company: frm.doc.branch   // or 'branch' → adjust to your field
                }
            };
        });
        frm.set_query("credit_account", function() {
            return {
                filters: {
                    company: frm.doc.branch   // or 'branch' → adjust to your field
                }
            };
        });
        frm.set_query("cost_center", function() {
            return {
                filters: {
                    company: frm.doc.branch   // or 'branch' → adjust to your field
                }
            };
        });
        if (frm.doc.workflow_state === "Approved" && frm.doc.docstatus === 1 && frm.doc.external_type!="Study Tours") {

            frm.add_custom_button("Create Learning Path", function () {

                frappe.model.with_doctype("Learning Path", () => {
                    let lp = frappe.model.get_new_doc("Learning Path");

                    // Map parent field
                    lp.requisition = frm.doc.name;

                    // Map child table
                    lp.employee_details = [];
                    frm.doc.employee_details.forEach(emp => {
                        lp.employee_details.push({
                            employee: emp.employee,
                            employee_name: emp.employee_name,
                            company_email: emp.company_email,
                            personal_email: emp.personal_email
                        });
                    });

                    // Open the new Learning Path form
                    frappe.set_route("Form", "Learning Path", lp.name);
                });

            });
        }
        if (frm.doc.docstatus != 1 && frm.doc.external_type !== "Study Tours") {
        frm.add_custom_button("Fetch Employees", function() {
            frappe.call({
                method: "nafed_erp.hire_to_retire.doctype.training_requisition.training_requisition.get_employees",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        // Clear existing child table
                        frm.clear_table("employee_details");
                        
                        // Add fetched employees with all fields
                        r.message.forEach(emp => {
                            let row = frm.add_child("employee_details");
                            
                            // Set all fields (using the field names from your child table)
                            row.employee = emp.name || emp.employee;  // Employee ID
                            row.employee_name = emp.employee_name;     // Employee Name
                            row.company_email = emp.company_email || "";  // Company Email
                            row.personal_email = emp.personal_email || "";  // Personal Email
                            row.designation = emp.designation || "";    // Designation
                            row.department = emp.department || "";      // Department
                            
                            // Add any other fields your child table has
                            // row.custom_field = emp.custom_field;
                        });
                        
                        // Refresh the child table
                        frm.refresh_field("employee_details");
                        
                        // Show success message
                        frappe.show_alert({
                            message: __("{0} Employees added successfully", [r.message.length]),
                            indicator: 'green'
                        });
                    } else {
                        frappe.show_alert({
                            message: __("No employees found"),
                            indicator: 'orange'
                        });
                    }
                },
                error: function(err) {
                    frappe.msgprint(__("Error fetching employees: " + err.message));
                }
            });                });
            }
        },
        external_type: function(frm) {
            frm.refresh();
        }
    });