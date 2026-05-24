// frappe.ui.form.on("Legal Case Court Order", {
//   refresh(frm) {
//     if (frm.is_new()) return;

//     frm.add_custom_button(
//       __("Create Compliance Task"),
//       () => open_compliance_task_dialog(frm),
//       __("Actions")
//     );
//   }
// });
// function open_compliance_task_dialog(frm) {
//   frappe.prompt(
//     [
//         {
//         fieldname: "task_title",
//         fieldtype: "Data",
//         label: "Task Title",
//         reqd: 1
//       },
//       {
//         fieldname: "assigned_to",
//         fieldtype: "Link",
//         label: "Assigned To",
//         options: "User",
//         reqd: 1
//       },
//       {
//         fieldname: "order_id",
//         fieldtype: "Data",
//         label: "Order ID",
//         default: frm.doc.name,
//         read_only: 1
//       },
//       {
//         fieldname: "case_id",
//         fieldtype: "Data",
//         label: "Case ID",
//         default: frm.doc.case_id,
//         read_only: 1
//       },
//       {
//         fieldname: "deadline_date",
//         fieldtype: "Date",
//         label: "Compliance Deadline",
//         reqd: 1
//       },
//       {
//         fieldname: "reminder_date",
//         fieldtype: "Date",
//         label: "Reminder Date"
//       },
//       {
//         fieldname: "status",
//         fieldtype: "Select",
//         label: "Status",
//         options: "Pending\nCompleted\nOverdue",
//         default: "Pending",
//         reqd: 1
//       }
//     ],
//     async (values) => {
//       try {
//         // 1) Create compliance task
//       const res = await frappe.call({
//   method: "frappe.client.insert",
//   args: {
//     doc: {
//       doctype: "Case Compliance Task",   
//       parenttype: "Legal Case Court Order",
//       parent: frm.doc.name,
//       parentfield: "case_compliance_task",         
//       case_id: frm.doc.case_id,
//       court_order: frm.doc.name,
//       assigned_to: values.assigned_to,
//       deadline_date: values.deadline_date,
//       reminder_date: values.reminder_date,
//       status: values.status,
//       task_title : values.task_title
//     }
//   }
// });


//         const task_id = res.message?.name; // COM-YYYY-xxxxx

//         // 2) Append in child table (replace 'compliance_tasks' with your table fieldname)
//         const row = frm.add_child("case_compliance_task");
//         row.case_compliance_task = task_id;
//         row.status = values.status;
//         row.assigned_to = values.assigned_to;
//         row.deadline_date = values.deadline_date;
//         row.task_title = values.task_title


//         frm.refresh_field("case_compliance_task");

//         // 3) Save parent doc so the child row persists
//         await frm.save();

//         frappe.msgprint({
//           title: __("Compliance Task Created"),
//           message: __("Compliance Task ID: <b>{0}</b> and added to the order.", [task_id]),
//           indicator: "green"
//         });
//       } catch (e) {
//         frappe.msgprint({
//           title: __("Error"),
//           message: e.message || __("Failed to create compliance task."),
//           indicator: "red"
//         });
//       }
//     },
//     __("Create Compliance Task"),
//     __("Create")
//   );
// }



frappe.ui.form.on("Legal Case Court Order", {
  refresh(frm) {
    if (frm.is_new()) return;

    frm.add_custom_button(
      __("Create Compliance Task"),
      () => open_compliance_task_dialog(frm),
      __("Actions")
    );
  }
});

function open_compliance_task_dialog(frm) {
  frappe.prompt(
    [
      {
        fieldname: "task_title",
        fieldtype: "Data",
        label: "Task Title",
        reqd: 1
      },
      {
        fieldname: "assigned_to",
        fieldtype: "Link",
        label: "Assigned To",
        options: "User",
        reqd: 1
      },
      {
        fieldname: "order_id",
        fieldtype: "Data",
        label: "Order ID",
        default: frm.doc.name,
        read_only: 1
      },
      {
        fieldname: "case_id",
        fieldtype: "Data",
        label: "Case ID",
        default: frm.doc.case_id,
        read_only: 1
      },
      {
        fieldname: "deadline_date",
        fieldtype: "Date",
        label: "Compliance Deadline",
        reqd: 1
      },
      {
        fieldname: "reminder_date",
        fieldtype: "Date",
        label: "Reminder Date"
      },
      {
        fieldname: "status",
        fieldtype: "Select",
        label: "Status",
        options: "Pending\nCompleted\nOverdue",
        default: "Pending",
        reqd: 1
      }
    ],
    async (values) => {
      try {
        // ✅ Add child row ONLY (no API insert)
        const row = frm.add_child("case_compliance_task");

        row.task_title = values.task_title;
        row.assigned_to = values.assigned_to;
        row.deadline_date = values.deadline_date;
        row.reminder_date = values.reminder_date;
        row.status = values.status;
        row.case_id = frm.doc.case_id;
        row.court_order = frm.doc.name;

        frm.refresh_field("case_compliance_task");

        // ✅ Save parent ONCE
        await frm.save();

        frappe.msgprint({
          title: __("Compliance Task Created"),
          message: __("Compliance Task has been added successfully."),
          indicator: "green"
        });

      } catch (e) {
        frappe.msgprint({
          title: __("Error"),
          message: e.message || __("Failed to create compliance task."),
          indicator: "red"
        });
      }
    },
    __("Create Compliance Task"),
    __("Create")
  );
}

