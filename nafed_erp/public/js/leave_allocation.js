// frappe.ui.form.on('Leave Allocation', {
//     refresh(frm) {
//         if (frm.doc.docstatus === 1) {
//             setTimeout(() => {
//                 $('li a:contains("Expire Allocation")').closest('li').remove();
//             }, 500);
//         }
//     }
// });


// ----------------------------------------------------------------------------------------

// frappe.ui.form.on('Leave Allocation', {
//     refresh(frm) {
//         if (frm.doc.docstatus === 1) {
//             setTimeout(() => {
//                 $('li a:contains("Expire Allocation")').closest('li').remove();
//             }, 500);
//         }
//     }
// });


// ----------------------------------------------------------------------------------------

frappe.ui.form.on('Leave Allocation', {
    refresh: function(frm) {
        // This hides the entire "Actions" button group
        setTimeout(() => {
            $('.btn-group[data-label="Actions"]').hide();
        }, 10);
        
        // If you only want to remove the 'Expire Allocation' item inside Actions:
        // frm.page.remove_custom_button('Expire Allocation', 'Actions');
    }
});

frappe.ui.form.on('Leave Allocation', {
    refresh: function(frm) {

        const remove_actions = () => {
            frm.page.wrapper
                .find('div.inner-group-button[data-label="Actions"]')
                .remove();
        };

        remove_actions();

        setTimeout(remove_actions, 100);
    }
});