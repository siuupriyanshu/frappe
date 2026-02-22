from __future__ import annotations

from datetime import datetime
import frappe
from frappe import _
from frappe.utils import validate_email_address


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


def _get_newsletter_doctype_name() -> str | None:
	for candidate in ("newsletter signup", "Newsletter Signup"):
		if frappe.db.exists("DocType", candidate):
			return candidate
	return None


@frappe.whitelist(allow_guest=True)
def submit_newsletter(email: str) -> dict:
	email = (email or "").strip()
	if not email:
		frappe.throw(_("Email is required."))

	if not validate_email_address(email, throw=False):
		frappe.throw(_("Please enter a valid email address."))

	doctype_name = _get_newsletter_doctype_name()
	if not doctype_name:
		frappe.throw(_("Newsletter doctype not found."))

	if frappe.db.exists(doctype_name, {"email": email}):
		return {"message": _("You are already subscribed.")}

	doc = frappe.get_doc({"doctype": doctype_name, "email": email})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"message": _("Subscribed successfully.")}


def _set_newsletter_context(context: dict) -> None:
	context.newsletter_success = getattr(context, "newsletter_success", None)
	context.newsletter_error = getattr(context, "newsletter_error", None)
	context.newsletter_email = getattr(context, "newsletter_email", "")

	if not (frappe.request and frappe.request.method == "POST"):
		return

	if not frappe.form_dict.get("newsletter_signup"):
		return

	email = (frappe.form_dict.get("email") or "").strip()
	context.newsletter_email = email

	try:
		result = submit_newsletter(email)
		context.newsletter_success = result.get("message")
		context.newsletter_email = ""
	except Exception as error:
		context.newsletter_error = str(error)


def set_common_context(context: dict, page_key: str, page_title: str) -> dict:
	context.no_cache = 1
	context.routes = ROUTES
	context.current_page = page_key
	context.page_title = page_title
	context.current_year = datetime.now().year
	_set_appointment_context(context)
	_set_newsletter_context(context)
	return context
