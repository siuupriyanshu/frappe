frappe.ui.form.on('Doctor', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('View Appointments', function() {
                frappe.set_route('List', 'Appointment', {
                    doctor: frm.doc.name
                });
            }, 'Go To');
        }
    },
    start_time: function(frm) { validate_times(frm); },
    end_time: function(frm) { validate_times(frm); }
});

function validate_times(frm) {
    if (frm.doc.start_time && frm.doc.end_time) {
        if (frm.doc.start_time >= frm.doc.end_time) {
            frappe.msgprint('Start time must be before end time.');
            frm.set_value('end_time', '');
        }
    }
}
