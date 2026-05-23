frappe.ui.form.on('Breeder Seed Plan Item', {
    // This triggers whenever any child table row is added, removed, or modified
    form_render: function(frm) {
        calculate_totals(frm);
    },
    target_physical: function(frm) {
        calculate_totals(frm);
    },
    target_financial: function(frm) {
        calculate_totals(frm);
    },
    achievement_physical: function(frm) {
        calculate_totals(frm);
    },
    achievement_financial: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_totals(frm) {
    let totals = {
        target_physical: 0,
        target_financial: 0,
        achievement_physical: 0,
        achievement_financial: 0
    };
    
    $.each(frm.doc.breeder_seed_plan_item || [], function(i, row) {
        totals.target_physical += row.target_physical || 0;
        totals.target_financial += row.target_financial || 0;
        totals.achievement_physical += row.achievement_physical || 0;
        totals.achievement_financial += row.achievement_financial || 0;
    });
    
    // Display totals somewhere on the form – you need a field to hold them
    frm.set_value('total_target_physical', totals.target_physical);
    frm.set_value('total_target_financial', totals.target_financial);
    frm.set_value('total_achievement_physical', totals.achievement_physical);
    frm.set_value('total_achievement_financial', totals.achievement_financial);
}