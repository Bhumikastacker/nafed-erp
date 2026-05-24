// frappe.ui.form.on("Purchase Receipt", {
//     refresh(frm) {

//         console.log("PR FLOW JS LOADED");

//         // REMOVE OLD FLOW FIRST
//         frm.page.main.find(".purchase-flow-wrapper").remove();

//         // DON'T SHOW FOR NEW DOC
//         if (frm.is_new()) return;

//         setTimeout(async () => {

//             // EXTRA SAFETY REMOVE
//             frm.page.main.find(".purchase-flow-wrapper").remove();

//             let current_step = await get_current_step(frm);

//             let steps = [
//                 "Draft",
//                 "Purchase Receipt",
//                 "Purchase Invoice",
//                 "Payment Entry",
//                 "Completed"
//             ];

//             let html = `
//                 <div class="purchase-flow-wrapper" style="
//                     background:#fff;
//                     padding:24px 20px;
//                     border-radius:12px;
//                     margin-bottom:20px;
//                     border:1px solid #e5e7eb;
//                     box-shadow:0 1px 3px rgba(0,0,0,0.08);
//                     overflow-x:auto;
//                 ">

//                     <div style="
//                         display:flex;
//                         justify-content:space-between;
//                         align-items:flex-start;
//                         position:relative;
//                         width:100%;
//                         min-width:900px;
//                     ">
//             `;

//             steps.forEach((step, index) => {

//                 let active = index <= current_step;

//                 html += `
//                     <div style="
//                         flex:1;
//                         min-width:140px;
//                         text-align:center;
//                         position:relative;
//                     ">

//                         ${
//                             index < steps.length - 1
//                                 ? `
//                             <div style="
//                                 position:absolute;
//                                 top:18px;
//                                 left:50%;
//                                 width:100%;
//                                 height:3px;
//                                 background:${active ? '#28a745' : '#d1d5db'};
//                                 z-index:1;
//                             "></div>
//                         `
//                                 : ""
//                         }

//                         <div style="
//                             width:38px;
//                             height:38px;
//                             border-radius:50%;
//                             margin:auto;
//                             background:${active ? '#28a745' : '#cbd5e1'};
//                             color:white;
//                             line-height:38px;
//                             position:relative;
//                             z-index:2;
//                             font-weight:bold;
//                             font-size:14px;
//                             box-shadow:0 2px 6px rgba(0,0,0,0.15);
//                         ">
//                             ${index + 1}
//                         </div>

//                         <div style="
//                             margin-top:10px;
//                             font-size:13px;
//                             color:${active ? '#28a745' : '#6b7280'};
//                             font-weight:600;
//                         ">
//                             ${step}
//                         </div>

//                     </div>
//                 `;
//             });

//             html += `
//                     </div>
//                 </div>
//             `;

//             // INSERT ONLY ONCE
//             if (!frm.page.main.find(".purchase-flow-wrapper").length) {

//                 $(html).insertBefore(
//                     frm.page.main.find(".form-tabs")
//                 );
//             }

//         }, 300);
//     }
// });


// // =====================================================
// // GET CURRENT STEP
// // =====================================================

// async function get_current_step(frm) {

//     // STEP 0 → DRAFT
//     if (frm.doc.docstatus === 0) {
//         return 0;
//     }

//     // STEP 1 → PURCHASE RECEIPT SUBMITTED
//     if (frm.doc.docstatus === 1) {

//         // CHECK PURCHASE INVOICE
//         let pi = await frappe.db.get_list("Purchase Invoice", {
//             filters: {
//                 purchase_receipt: frm.doc.name,
//                 docstatus: 1
//             },
//             fields: ["name"],
//             limit: 1
//         });

//         // PURCHASE INVOICE FOUND
//         if (pi.length > 0) {

//             // STEP 2 → PURCHASE INVOICE CREATED

//             // CHECK PAYMENT ENTRY
//             let pe = await frappe.db.get_list("Payment Entry Reference", {
//                 filters: {
//                     reference_name: pi[0].name,
//                     reference_doctype: "Purchase Invoice"
//                 },
//                 fields: ["parent"],
//                 limit: 1
//             });

//             // PAYMENT ENTRY FOUND
//             if (pe.length > 0) {

//                 // STEP 4 → COMPLETED
//                 return 4;
//             }

//             // STEP 3 → ONLY PURCHASE INVOICE DONE
//             return 2;
//         }

//         // STEP 1 → ONLY PURCHASE RECEIPT DONE
//         return 1;
//     }

//     return 0;
// }