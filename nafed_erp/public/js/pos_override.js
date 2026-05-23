// console.log("🔥 SAFE BARCODE PATCH");

// frappe.after_ajax(() => {

//     if (!erpnext?.PointOfSale) return;

//     const POS = erpnext.PointOfSale;

//     const original = POS.prototype.scan_barcode;

//     POS.prototype.scan_barcode = async function(barcode) {

//         console.log("📦 Scan:", barcode);

//         // 🔥 check barcode table first
//         let res = await frappe.call({
//             method:"nafed_erp.procure_to_pay.api.rfq_api.get_item_by_barcode",
//             args:{barcode: barcode}
//         });

//         if (res.message && res.message.item_code) {

//             let item_code = res.message.item_code;
//             let mrp = flt(res.message.price_list_rate);

//             console.log("✅ Barcode matched:", item_code, mrp);

//             // ✅ Let POS add item normally
//             await this.add_to_cart({
//                 item_code: item_code
//             });

//             // 🔥 FIX LAST ROW ONLY (safe)
//             setTimeout(() => {

//                 let rows = this.frm.doc.items || [];
//                 let last = rows[rows.length - 1];

//                 if (!last) return;

//                 // ✅ ONLY override rate (do not break structure)
//                 frappe.model.set_value(last.doctype, last.name, "rate", mrp);
//                 frappe.model.set_value(last.doctype, last.name, "price_list_rate", mrp);
//                 frappe.model.set_value(last.doctype, last.name, "barcode", barcode);

//                 this.frm.refresh_field("items");
//                 this.frm.script_manager.trigger("calculate_taxes_and_totals");

//             }, 200);

//             return;
//         }

//         // fallback → default POS behavior
//         return original.call(this, barcode);
//     };

// });


// frappe.after_ajax(() => {

//     if (!erpnext?.PointOfSale) return;

//     const POS = erpnext.PointOfSale;
//     const original = POS.prototype.scan_barcode;

//     POS.prototype.scan_barcode = async function(barcode) {

//         let res = await frappe.call({
//             method:"nafed_erp.procure_to_pay.api.rfq_api.get_item_by_barcode",
//             args:{barcode: barcode}
//         });

//         if (res.message) {

//             await original.call(this, res.message.item_code);

//             let rows = this.frm.doc.items || [];
//             let last = rows[rows.length - 1];

//             if (last) {
//                 frappe.model.set_value(last.doctype, last.name, "rate", res.message.price_list_rate);
//             }

//             return;
//         }

//         return original.call(this, barcode);
//     };
// });




// frappe.ready(function () {

//     setTimeout(() => {

//         if (!erpnext.PointOfSale) return;

//         const original = erpnext.PointOfSale.prototype.on_scan;

//         erpnext.PointOfSale.prototype.on_scan = async function (barcode) {

//             console.log("Custom barcode:", barcode);

//             // your custom logic here

//             return original.call(this, barcode);
//         };

//     }, 2000);

// });


// Deepssek
// console.log("🔥 FINAL – Item Code Mapper + Barcode Handler");

// (function() {
//     let buffer = "";
//     let timer = null;
//     let processing = false;
//     const MIN_LEN = 4;
//     const DELAY_MS = 800;

//     // Mapping from backend item_name to actual item_code
//     const ITEM_CODE_MAP = {
//         "Oil Seed": "OS",
//         // Add more if needed, e.g., "Azospirillum Biofertilizer": "AB"
//     };

//     // Fallback rates + item codes per barcode
//     const BARCODE_DATA = {
//         "123450": { rate: 100, item_code: "OS" },
//         "1234500": { rate: 200, item_code: "OS" },
//         "12345000": { rate: 300, item_code: "OS" }
//     };

//     async function processBarcode(barcode) {
//         if (processing) return;
//         processing = true;
//         console.log(`📦 Processing barcode: ${barcode}`);

//         if (!window.cur_pos || !cur_pos.frm) {
//             frappe.msgprint("POS not ready");
//             processing = false;
//             return;
//         }

//         let rate = null;
//         let itemCode = null;

//         // 1. Try backend
//         try {
//             let res = await frappe.call({
//                 method: "nafed_erp.procure_to_pay.api.rfq_api.get_item_by_barcode",
//                 args: { barcode }
//             });
//             if (res.message && res.message.item_code) {
//                 let backendItem = res.message.item_code;   // e.g., "Oil Seed"
//                 // Map to actual item code if needed
//                 itemCode = ITEM_CODE_MAP[backendItem] || backendItem;
//                 rate = res.message.rate || res.message.price_list_rate;
//             }
//         } catch(e) {
//             console.warn("Backend error", e);
//         }

//         // 2. Fallback to local map if backend fails or returns invalid
//         if (!rate && BARCODE_DATA[barcode]) {
//             rate = BARCODE_DATA[barcode].rate;
//             itemCode = BARCODE_DATA[barcode].item_code;
//         }

//         if (!rate || !itemCode) {
//             frappe.msgprint(`Barcode ${barcode} not recognised`);
//             processing = false;
//             return;
//         }

//         console.log(`✅ Using item_code: ${itemCode}, rate: ${rate}`);

//         const frm = cur_pos.frm;
//         if (!frm.doc.items) frm.doc.items = [];

//         // Check for existing row with same barcode
//         let existing = frm.doc.items.find(row => row.custom_barcode_src === barcode);
//         if (existing) {
//             existing.qty += 1;
//             existing.amount = existing.qty * rate;
//             frm.refresh_field("items");
//             await frm.script_manager.trigger("calculate_taxes_and_totals");
//             console.log(`✅ Increased qty for ${barcode} → ${existing.qty}`);
//             processing = false;
//             return;
//         }

//         // Add new row
//         let newRow = frappe.model.add_child(frm.doc, "Sales Invoice Item", "items");
//         newRow.item_code = itemCode;          // This must be the actual item code (e.g., "OS")
//         newRow.qty = 1;
//         newRow.rate = rate;
//         newRow.price_list_rate = rate;
//         newRow.amount = rate;
//         newRow.custom_barcode_src = barcode;
//         newRow.discount_percentage = 0;
//         newRow.discount_amount = 0;
//         if (newRow.hasOwnProperty("barcode")) newRow.barcode = barcode;

//         frm.refresh_field("items");
//         await frm.script_manager.trigger("calculate_taxes_and_totals");
//         console.log(`✅ Added new row for ${barcode} with item ${itemCode} rate ${rate}`);
//         processing = false;
//     }

//     function finalizeBuffer() {
//         if (timer) clearTimeout(timer);
//         if (buffer.length >= MIN_LEN) {
//             processBarcode(buffer);
//         } else if (buffer.length > 0) {
//             console.log(`Ignoring short buffer: "${buffer}"`);
//         }
//         buffer = "";
//         timer = null;
//     }

//     // Keyboard capture
//     document.addEventListener("keypress", function(e) {
//         if (!window.cur_pos || !cur_pos.frm) return;
//         const char = String.fromCharCode(e.which);
//         if (/[0-9]/.test(char)) {
//             e.preventDefault();
//             e.stopPropagation();
//             buffer += char;
//             if (timer) clearTimeout(timer);
//             timer = setTimeout(finalizeBuffer, DELAY_MS);
//         }
//     }, true);

//     document.addEventListener("keydown", function(e) {
//         if (!window.cur_pos || !cur_pos.frm) return;
//         if (e.key === "Enter" && buffer.length >= MIN_LEN) {
//             e.preventDefault();
//             e.stopPropagation();
//             finalizeBuffer();
//         }
//     }, true);

//     // Periodic rate fixer (in case POS overrides)
//     setInterval(() => {
//         if (!window.cur_pos || !cur_pos.frm || !cur_pos.frm.doc.items) return;
//         let changed = false;
//         for (let row of cur_pos.frm.doc.items) {
//             if (row.custom_barcode_src && BARCODE_DATA[row.custom_barcode_src]) {
//                 const expected = BARCODE_DATA[row.custom_barcode_src];
//                 if (row.rate !== expected.rate || row.discount_percentage !== 0) {
//                     row.rate = expected.rate;
//                     row.price_list_rate = expected.rate;
//                     row.amount = row.qty * expected.rate;
//                     row.discount_percentage = 0;
//                     row.discount_amount = 0;
//                     changed = true;
//                     console.log(`🔧 Fixed rate for ${row.custom_barcode_src} to ${expected.rate}`);
//                 }
//                 if (row.item_code !== expected.item_code) {
//                     row.item_code = expected.item_code;
//                     changed = true;
//                 }
//             }
//         }
//         if (changed) {
//             cur_pos.frm.refresh_field("items");
//             cur_pos.frm.script_manager.trigger("calculate_taxes_and_totals");
//         }
//     }, 1000);

//     console.log(`🔥 Active: barcode capture with item code mapping (e.g., "Oil Seed" → "OS")`);
// })();

// console.log("🔥 NAFED POS Barcode Handler v4");

// (function () {
//     let buffer = "";
//     let timer = null;
//     let processing = false;
//     const MIN_LEN = 4;
//     const DELAY_MS = 800;

//     async function processBarcode(barcode) {
//         if (processing) return;
//         processing = true;
//         console.log(`📦 Barcode scanned: ${barcode}`);

//         if (!window.cur_pos?.frm) {
//             frappe.msgprint("POS not ready");
//             processing = false;
//             return;
//         }

//         // --- Fetch item from backend ---
//         let itemCode = null;
//         let rate = null;
//         try {
//             const res = await frappe.call({
//                 method: "nafed_erp.procure_to_pay.api.rfq_api.get_item_by_barcode",
//                 args: { barcode }
//             });
//             if (res.message?.item_code) {
//                 itemCode = res.message.item_code;
//                 rate = res.message.rate;
//             }
//         } catch (e) {
//             console.warn("Backend lookup failed:", e);
//         }

//         if (!itemCode || !rate) {
//             frappe.msgprint(`⚠️ Barcode "${barcode}" not found or has no price.`);
//             processing = false;
//             return;
//         }

//         console.log(`✅ item_code="${itemCode}", rate=₹${rate}`);

//         const frm = cur_pos.frm;
//         if (!frm.doc.items) frm.doc.items = [];

//         // --- Check existing row by barcode ---
//         const existing = frm.doc.items.find(r => r.custom_barcode_src === barcode);
//         if (existing) {
//             existing.qty += 1;
//             existing.rate = rate;
//             existing.price_list_rate = rate;
//             existing.amount = existing.qty * rate;
//             existing.discount_percentage = 0;
//             existing.discount_amount = 0;
//             frm.refresh_field("items");
//             frm.script_manager.trigger("calculate_taxes_and_totals");
//             console.log(`♻️ qty → ${existing.qty} for ${barcode}`);
//             processing = false;
//             return;
//         }

//         // --- Fetch full item details from ERPNext (same way POS does internally) ---
//         let itemDetails = null;
//         try {
//             const det = await frappe.call({
//                 method: "erpnext.stock.get_item_details.get_item_details",
//                 args: {
//                     args: {
//                         item_code: itemCode,
//                         customer: frm.doc.customer || "",
//                         doctype: "Sales Invoice",
//                         name: frm.doc.name,
//                         company: frm.doc.company,
//                         price_list: frm.doc.selling_price_list,
//                         currency: frm.doc.currency,
//                         conversion_rate: frm.doc.conversion_rate || 1,
//                         qty: 1,
//                         stock_qty: 1,
//                         transaction_date: frm.doc.posting_date,
//                         is_pos: 1,
//                         pos_profile: frm.doc.pos_profile,
//                         uom: "",
//                         update_stock: frm.doc.update_stock,
//                     }
//                 }
//             });
//             if (det.message) itemDetails = det.message;
//         } catch (e) {
//             console.warn("get_item_details failed:", e);
//         }

//         // --- Add row using full item details ---
//         const newRow = frappe.model.add_child(frm.doc, "Sales Invoice Item", "items");

//         if (itemDetails) {
//             // Copy all fetched fields onto the row
//             Object.assign(newRow, itemDetails);
//         }

//         // Always override with barcode-specific values
//         newRow.item_code = itemCode;
//         newRow.qty = 1;
//         newRow.rate = rate;
//         newRow.price_list_rate = rate;
//         newRow.amount = rate;
//         newRow.discount_percentage = 0;
//         newRow.discount_amount = 0;
//         newRow.custom_barcode_src = barcode;

//         frm.refresh_field("items");
//         frm.script_manager.trigger("calculate_taxes_and_totals");
//         console.log(`➕ Added: "${itemCode}" @ ₹${rate}`);
//         processing = false;
//     }

//     function finalizeBuffer() {
//         if (timer) clearTimeout(timer);
//         const code = buffer;
//         buffer = "";
//         timer = null;
//         if (code.length >= MIN_LEN) processBarcode(code);
//         else console.log(`Ignoring short buffer: "${code}"`);
//     }

//     document.addEventListener("keypress", function (e) {
//         if (!window.cur_pos?.frm) return;
//         const ch = String.fromCharCode(e.which);
//         if (/[0-9]/.test(ch)) {
//             e.preventDefault();
//             e.stopPropagation();
//             buffer += ch;
//             if (timer) clearTimeout(timer);
//             timer = setTimeout(finalizeBuffer, DELAY_MS);
//         }
//     }, true);

//     document.addEventListener("keydown", function (e) {
//         if (!window.cur_pos?.frm) return;
//         if (e.key === "Enter" && buffer.length >= MIN_LEN) {
//             e.preventDefault();
//             e.stopPropagation();
//             finalizeBuffer();
//         }
//     }, true);

//     console.log("✅ v4 active — using get_item_details for proper POS row population");
// })();


