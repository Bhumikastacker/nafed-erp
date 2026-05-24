// console.log("Custom Org Chart JS loaded");

// // Function to append custom fields for each node
// function appendCustomFields() {
//     if ($(".child-node .node-meta").length === 0) {
//         setTimeout(appendCustomFields, 500);
//         return;
//     }

//     $(".child-node .node-meta").each(function () {
//         let node_id = $(this).closest(".node-card").attr("id");
//         if (!node_id) return;

//         // Avoid duplicates
//         if ($(this).find(".custom-node-info").length > 0) return;

//         frappe.db.get_doc("Employee", node_id).then(emp => {
//             const html = `
//                 <div class="node-info d-flex flex-row custom-node-info">
//                     <div class="node-title text-muted ellipsis">Division&nbsp;·&nbsp;</div>
//                     <div class="node-connections text-muted ellipsis">${emp.custom_division || "N/A"}</div>
                    
                    
//                 </div>
//                 <div class="node-info d-flex flex-row custom-node-info">
//                    <div class="node-title text-muted ellipsis">Grade&nbsp;·&nbsp;</div>
//                     <div class="node-connections text-muted ellipsis">${emp.grade || "N/A"}</div><br/>
//                 </div>
//                 <div class="node-info d-flex flex-row mb-1 custom-node-info">
//                     <div class="node-title text-muted ellipsis">Reports To&nbsp;·&nbsp;</div>
//                     <div class="node-connections text-muted ellipsis">${emp.reports_to || "N/A"}</div>
//                 </div>
//                  <div class="node-info d-flex flex-row mb-1 custom-node-info">
//                     <div class="node-title text-muted ellipsis"> Other Reports To&nbsp;·&nbsp;</div>
//                     <div class="node-connections text-muted ellipsis">${emp.custom_other_reports_to_employee_id || "N/A"}</div>
//                 </div>
//             `;
//             $(this).find(".node-info").last().after(html);
//         });
//     });
// }


// function drawDynamicArrows() {
//     const svg = document.querySelector("#arrows");
//     const container = document.querySelector("#hierarchy-chart-wrapper");
//     const connectors = document.querySelector("#connectors");

//     if (!svg || !container || !connectors) return;

//     connectors.innerHTML = ""; // Clear old arrows

//     const parentNodes = document.querySelectorAll(".node-card[data-parent='']");

//     parentNodes.forEach(parent => {
//         const parentRect = parent.getBoundingClientRect();
//         const parentX = parentRect.right - container.getBoundingClientRect().left + 10;
//         const parentY = parentRect.top - container.getBoundingClientRect().top + parentRect.height / 2;

//         const parentId = parent.id;
//         const childNodes = document.querySelectorAll(`.node-card[data-parent='${parentId}']`);

//         childNodes.forEach(child => {
//             const childRect = child.getBoundingClientRect();
//             const childX = childRect.left - container.getBoundingClientRect().left - 10;
//             const childY = childRect.top - container.getBoundingClientRect().top + childRect.height / 2;

//             let midX1 = parentX + 40;
//             let midX2 = childX - 40;

//             const d = `
//                 M ${parentX},${parentY}
//                 L ${midX1},${parentY}
//                 a10,10 0 0 1 10,10
//                 L ${midX1},${childY}
//                 a10,10 1 0 0 10,10
//                 L ${childX},${childY}
//             `;

//             const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
//             path.setAttribute("d", d.trim());
//             path.setAttribute("data-parent", parentId);
//             path.setAttribute("data-child", child.id);
//             path.setAttribute("class", "active-connector");
//             path.setAttribute("marker-start", "url(#arrowstart-active)");
//             path.setAttribute("marker-end", "url(#arrowhead-active)");

//             connectors.appendChild(path);
//         });
//     });
// }



// // Run initially on page load
// $(document).ready(function () {
//     appendCustomFields();
//     setTimeout(drawDynamicArrows, 1000);
// });

// // Hook into Expand All button click
// $(document).on("click", 'button[data-label="Expand%20All"], button[data-label="Collapse%20All"]', function () {
//     // Wait for DOM update after expand/collapse
//     setTimeout(appendCustomFields, 500);
//     setTimeout(drawDynamicArrows, 1000);
// });



console.log("Custom Org Chart JS loaded");

function appendCustomFields() {
    if ($(".child-node .node-meta").length === 0) {
        setTimeout(appendCustomFields, 500);
        return;
    }

    $(".child-node .node-meta").each(function () {
        const node_id = $(this).closest(".node-card").attr("id");
        if (!node_id) return;

        // Prevent duplicate injection
        if ($(this).find(".custom-node-info").length) return;

        frappe.db.get_doc("Employee", node_id).then(emp => {

            // ✅ CHILD TABLE MULTISELECT HANDLING
            let otherReportsTo = "N/A";

            if (
                emp.custom_other_reports_to_employee_id &&
                emp.custom_other_reports_to_employee_id.length
            ) {
                otherReportsTo = emp.custom_other_reports_to_employee_id
                    .map(row => row.employee)
                    .filter(Boolean)
                    .join(", ");
            }

            const html = `
                <div class="node-info d-flex flex-row custom-node-info">
                    <div class="node-title text-muted">Division ·</div>
                    <div class="node-connections text-muted">${emp.custom_division || "N/A"}</div>
                </div>

                <div class="node-info d-flex flex-row custom-node-info">
                    <div class="node-title text-muted">Grade ·</div>
                    <div class="node-connections text-muted">${emp.grade || "N/A"}</div>
                </div>

                <div class="node-info d-flex flex-row custom-node-info">
                    <div class="node-title text-muted">Reports To ·</div>
                    <div class="node-connections text-muted">${emp.reports_to || "N/A"}</div>
                </div>

                <div class="node-info d-flex flex-row custom-node-info">
                    <div class="node-title text-muted">Other Reports To ·</div>
                    <div class="node-connections text-muted">${otherReportsTo}</div>
                </div>
            `;

            $(this).find(".node-info").last().after(html);
        });
    });
}

// Initial load
$(document).ready(function () {
    appendCustomFields();
});

// Re-run on expand / collapse
$(document).on(
    "click",
    'button[data-label="Expand%20All"], button[data-label="Collapse%20All"]',
    function () {
        setTimeout(appendCustomFields, 600);
    }
);

