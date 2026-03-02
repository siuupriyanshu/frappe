# Copyright (c) 2026, priyanshu mandal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Doctor(Document):
    def validate(self):
        self.validate_times()
        self.validate_email()

    def validate_times(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                frappe.throw('Start Time must be before End Time')

    def validate_email(self):
        existing = frappe.db.exists('Doctor', {'email': self.email})
        if existing and existing != self.name:
            frappe.throw(f'Email {self.email} is already registered to another doctor')

    def after_insert(self):
        frappe.msgprint(f'Doctor {self.full_name} created successfully', alert=True)

