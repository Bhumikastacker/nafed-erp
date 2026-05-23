// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Dispatch Receipt", {
// 	refresh(frm) {

// 	},
// });// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dispatch Receipt", {
    refresh: async function(frm) {

        console.log("DISPATCH FLOW LOADED");

        $(".purchase-flow-wrapper").remove();

        if (frm.is_new()) return;

        let current_step = await get_current_step(frm);

        let steps = [
            "Draft",
            "Lot Receipt",
            "Goods Receipt Notes ",
            "Purchase Invoice",
            "Payment Entry",
            "Completed"
        ];

        let html = `
            <div class="purchase-flow-wrapper" style="
                background:#fff;
                padding:24px 20px;
                border-radius:12px;
                margin-bottom:20px;
                border:1px solid #e5e7eb;
                box-shadow:0 1px 3px rgba(0,0,0,0.08);
                overflow-x:auto;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:flex-start;
                    position:relative;
                    min-width:1100px;
                ">
        `;

        steps.forEach((step, index) => {

            let active = index <= current_step;

            html += `
                <div style="
                    flex:1;
                    text-align:center;
                    position:relative;
                ">

                    ${
                        index < steps.length - 1
                        ? `
                            <div style="
                                position:absolute;
                                top:18px;
                                left:50%;
                                width:100%;
                                height:3px;
                                background:${active ? '#28a745' : '#d1d5db'};
                                z-index:1;
                            "></div>
                        `
                        : ``
                    }

                    <div style="
                        width:38px;
                        height:38px;
                        border-radius:50%;
                        margin:auto;
                        background:${active ? '#28a745' : '#cbd5e1'};
                        color:#fff;
                        line-height:38px;
                        position:relative;
                        z-index:2;
                        font-weight:bold;
                    ">
                        ${index + 1}
                    </div>

                    <div style="
                        margin-top:10px;
                        font-size:13px;
                        font-weight:600;
                        color:${active ? '#28a745' : '#6b7280'};
                    ">
                        ${step}
                    </div>

                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        // THIS IS IMPORTANT
        $(html).prependTo(frm.page.main);
    }
});


// ======================================================
// GET CURRENT STEP
// ======================================================

async function get_current_step(frm) {

    if (frm.doc.docstatus === 0) {
        return 0;
    }

    if (frm.doc.docstatus === 1) {

        // PURCHASE RECEIPT CREATED
        if (frm.doc.receipt_id) {

            // PURCHASE INVOICE CREATED
            if (frm.doc.invoice_id) {

                // PAYMENT COMPLETED
                if (frm.doc.status === "Payment Completed") {
                    return 5;
                }

                // PAYMENT ENTRY
                return 4;
            }

            // PURCHASE RECEIPT DONE
            return 2;
        }

        // LOT RECEIPT DONE
        return 1;
    }

    return 0;
}
