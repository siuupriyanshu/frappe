frappe.ui.form.on('Appointment', {

    // Triggered when the form first loads
    setup: function(frm) {
        frm.set_query('doctor', function() {
            return { filters: { is_active: 1 } };
        });
    },

    // Auto-populate fields when doctor is selected
    doctor: function(frm) {
        if (frm.doc.doctor) {
            frappe.call({
                method: 'frappe.client.get',
                args: { doctype: 'Doctor', name: frm.doc.doctor },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('doctor_name', r.message.full_name);
                        frm.set_value('consultation_fee', r.message.consultation_fee);
                        frm.set_value('duration', r.message.slot_duration);
                    }
                }
            });
        }
    },

    // Auto-set combined datetime when date changes
    appointment_date: function(frm) {
        set_appointment_datetime(frm);
        validate_appointment_date(frm);
    },

    // Auto-set combined datetime when time changes
    appointment_time: function(frm) {
        set_appointment_datetime(frm);
    },

    // Validate before form save
    validate: function(frm) {
        validate_appointment_date(frm);
    }
});

function set_appointment_datetime(frm) {
    if (frm.doc.appointment_date && frm.doc.appointment_time) {
        let dt = frm.doc.appointment_date + ' ' + frm.doc.appointment_time;
        frm.set_value('appointment_datetime', dt);
    }
}

function validate_appointment_date(frm) {
    if (frm.doc.appointment_date) {
        let today = frappe.datetime.get_today();
        if (frm.doc.appointment_date < today) {
            frappe.msgprint({
                title: 'Invalid Date',
                message: 'Appointment date cannot be in the past.',
                indicator: 'red'
            });
            frm.set_value('appointment_date', '');
        }
    }
}

