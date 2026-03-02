# Copyright (c) 2026, priyanshu mandal and contributors
# For license information, please see license.txt

import frappe 
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime, getdate, nowdate



class Appointment(Document):
	def validate(self):
        self.validate_future_date()
        self.validate_doctor_availability()
        self.validate_slot_conflict()
        self.fetch_doctor_details()
        self.set_appointment_datetime()

    def validate_future_date(self):
        if getdate(self.appointment_date) < getdate(nowdate()):
            frappe.throw('Appointment date cannot be in the past')

    def fetch_doctor_details(self):
        doc = frappe.get_doc('Doctor', self.doctor)
        self.doctor_name = doc.full_name
        self.specialization = doc.specialization
        self.duration = doc.slot_duration
        self.consultation_fee = doc.consultation_fee

    def set_appointment_datetime(self):
        if self.appointment_date and self.appointment_time:
            self.appointment_datetime = f'{self.appointment_date} {self.appointment_time}'

    def validate_doctor_availability(self):
        doctor = frappe.get_doc('Doctor', self.doctor)
        if not doctor.is_active:
            frappe.throw(f'Dr. {doctor.full_name} is not currently accepting appointments')
        day = getdate(self.appointment_date).strftime('%A')
        available = [d.day for d in doctor.available_days]
        if day not in available:
            frappe.throw(f'Dr. {doctor.full_name} is not available on {day}s')

    def validate_slot_conflict(self):
        conflicts = frappe.db.count('Appointment', {
            'doctor': self.doctor,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'status': ['not in', ['Cancelled']],
            'name': ['!=', self.name]
        })
        if conflicts:
            frappe.throw('This time slot is already booked for the selected doctor')

    def after_insert(self):
        self.send_confirmation_email()

    def send_confirmation_email(self):
        frappe.sendmail(
            recipients=[self.patient_email],
            subject=f'Appointment Confirmed - {self.name}',
            template='appointment_confirmation',
            args=self.as_dict(),
            now=True
        )
        self.db_set('confirmation_sent', 1)

    def on_submit(self):
        self.db_set('status', 'Confirmed')

    def on_cancel(self):
        self.db_set('status', 'Cancelled')

