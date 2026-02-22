import frappe
from frappe import _
from frappe.utils import validate_email_address

from hospital.www.page_context import set_common_context


def _get_contact_doctype_name() -> str | None:
	for candidate in ("contacts", "Contacts"):
		if frappe.db.exists("DocType", candidate):
			return candidate
	return None


def get_context(context: dict) -> dict:
	context = set_common_context(context, "contact", "Contact - Medinova")
	context.contact_success = None
	context.contact_error = None
	context.form_values = {}

	if frappe.request and frappe.request.method == "POST":
		context.form_values = {
			"name1": (frappe.form_dict.get("name1") or "").strip(),
			"email": (frappe.form_dict.get("email") or "").strip(),
			"subject": (frappe.form_dict.get("subject") or "").strip(),
			"message": (frappe.form_dict.get("message") or "").strip(),
		}

		try:
			send_contact_message(**context.form_values)
			context.contact_success = _("Message sent successfully.")
			context.form_values = {}
		except Exception as error:
			context.contact_error = str(error)

	return context


@frappe.whitelist(allow_guest=True)
def send_contact_message(name1: str, email: str, subject: str, message: str) -> dict:
	if not all([name1, email, subject, message]):
		frappe.throw(_("All contact fields are required."))

	if not validate_email_address(email, throw=False):
		frappe.throw(_("Please enter a valid email address."))

	doctype_name = _get_contact_doctype_name()
	if not doctype_name:
		frappe.throw(_("Contacts doctype not found."))

	doc = frappe.get_doc(
		{
			"doctype": doctype_name,
			"name1": name1,
			"email": email,
			"subject": subject,
			"message": message,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {"message": _("Message sent successfully.")}
