from __future__ import annotations

from datetime import datetime
import frappe


ROUTES = {
	"home": "/hospital",
	"about": "/about",
	"service": "/service",
	"price": "/price",
	"blog": "/blog",
	"detail": "/detail",
	"team": "/team",
	"testimonial": "/testimonial",
	"appointment": "/appointment",
	"search": "/search",
	"contact": "/contact",
}


def _get_appointment_doctype_name() -> str | None:
	for candidate in ("appointment", "Appointment"):
		if frappe.db.exists("DocType", candidate):
			return candidate
	return None


def _get_select_options(doctype_name: str, fieldname: str) -> list[str]:
	meta = frappe.get_meta(doctype_name)
	field = meta.get_field(fieldname)
	if not field or not field.options:
		return []

	return [option.strip() for option in field.options.split("\n") if option.strip()]


def _set_appointment_context(context: dict) -> None:
	context.form_values = getattr(context, "form_values", {}) or {}
	context.appointment_success = getattr(context, "appointment_success", None)
	context.appointment_error = getattr(context, "appointment_error", None)

	doctype_name = _get_appointment_doctype_name()
	if doctype_name:
		context.departments = _get_select_options(doctype_name, "department")
		context.doctors = _get_select_options(doctype_name, "doctor")
	else:
		context.departments = []
		context.doctors = []


def set_common_context(context: dict, page_key: str, page_title: str) -> dict:
	context.no_cache = 1
	context.routes = ROUTES
	context.current_page = page_key
	context.page_title = page_title
	context.current_year = datetime.now().year
	_set_appointment_context(context)
	return context
