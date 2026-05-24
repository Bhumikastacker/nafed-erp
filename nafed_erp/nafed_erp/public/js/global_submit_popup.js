

/* AFTER SUBMIT POPUP */

// let last_docstatus = {};

// $(document).on("form-refresh", function (e, frm) {

//     if (!(frm.doc.name in last_docstatus)) {
//         last_docstatus[frm.doc.name] = frm.doc.docstatus;
//         return;
//     }

//     if (last_docstatus[frm.doc.name] === 0 && frm.doc.docstatus === 1) {

//         frappe.msgprint({
//             title: "Submitted",
//             message: frm.doctype + " has been submitted successfully",
//             indicator: "green"
//         });

//     }

//     last_docstatus[frm.doc.name] = frm.doc.docstatus;

// });