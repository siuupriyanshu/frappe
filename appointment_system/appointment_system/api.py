import frappe
from frappe import _
from frappe.utils import nowdate, getdate

@frappe.whitelist(allow_guest=True)
def book_appointment(patient_name, patient_email, doctor,
                     appointment_date, appointment_time, reason,
                     patient_phone=None, notes=None):
    
    # Basic validation
    if getdate(appointment_date) < getdate(nowdate()):
        frappe.throw(_('Appointment date must be in the future'))

    # Check doctor exists and is active
    doc_data = frappe.db.get_value('Doctor', doctor,
        ['full_name', 'is_active'], as_dict=True)
    if not doc_data:
        frappe.throw(_('Doctor not found'))
    if not doc_data.is_active:
        frappe.throw(_('This doctor is not accepting appointments'))

    # Create the appointment
    appointment = frappe.get_doc({
        'doctype': 'Appointment',
        'patient_name': patient_name,
        'patient_email': patient_email,
        'patient_phone': patient_phone,
        'doctor': doctor,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,
        'reason': reason,
        'notes': notes,
        'status': 'Scheduled'
    })

    try:
        # ignore_permissions is correct for allow_guest=True
        appointment.insert(ignore_permissions=True)
        frappe.db.commit()
    except frappe.exceptions.OutgoingEmailError:
        # The appointment is saved, but the email failed. 
        # We log it and continue so the user sees a success message.
        frappe.log_error("Email failed to send for appointment " + appointment.name)
        return {
            'status': 'success_partial',
            'appointment_id': appointment.name,
            'message': _('Appointment booked, but confirmation email could not be sent. Please contact support.')
        }

    return {
        'status': 'success',
        'appointment_id': appointment.name,
        'message': f'Appointment booked successfully with {doc_data.full_name}'
    }