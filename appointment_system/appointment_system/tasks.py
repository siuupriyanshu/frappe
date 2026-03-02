import frappe
from frappe.utils import add_days, nowdate

def send_appointment_reminders():
    """Send reminder emails for tomorrow's appointments."""
    tomorrow = add_days(nowdate(), 1)
    appointments = frappe.get_all('Appointment', filters={
        'appointment_date': tomorrow,
        'status': 'Confirmed',
        'docstatus': 1
    }, fields=['name', 'patient_name', 'patient_email', 'doctor_name', 'appointment_time'])

    for appt in appointments:
        frappe.sendmail(
            recipients=[appt.patient_email],
            subject=f'Reminder: Appointment Tomorrow - {appt.name}',
            message=f'''
Dear {appt.patient_name},

This is a reminder that you have an appointment tomorrow with {appt.doctor_name}
at {appt.appointment_time}.

Please arrive 10 minutes early.

Regards,
Appointment System
            ''',
            now=False
        )
    frappe.logger().info(f'Sent {len(appointments)} appointment reminders for {tomorrow}')
