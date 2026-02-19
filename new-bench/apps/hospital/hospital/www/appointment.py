import frappe
from frappe import _
from frappe.utils import getdate, get_time
from hospital.www.page_context import set_common_context


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


def get_context(context: dict) -> dict:
	set_common_context(context, "appointment", "Appointment - Medinova")
	context.appointment_success = None
	context.appointment_error = None
	context.form_values = {}

	doctype_name = _get_appointment_doctype_name()

	if doctype_name:
		context.departments = _get_select_options(doctype_name, "department")
		context.doctors = _get_select_options(doctype_name, "doctor")
	else:
		context.departments = []
		context.doctors = []

	if frappe.request and frappe.request.method == "POST":
		context.form_values = {
			"department": (frappe.form_dict.get("department") or "").strip(),
			"doctor": (frappe.form_dict.get("doctor") or "").strip(),
			"name1": (frappe.form_dict.get("name1") or "").strip(),
			"email": (frappe.form_dict.get("email") or "").strip(),
			"appointment_date": (frappe.form_dict.get("appointment_date") or "").strip(),
			"appointment_time": (frappe.form_dict.get("appointment_time") or "").strip(),
		}

		try:
			book_appointment(**context.form_values)
			context.appointment_success = _("Appointment submitted successfully.")
			context.form_values = {}
		except Exception as error:
			context.appointment_error = str(error)

	return context


@frappe.whitelist(allow_guest=True)
def book_appointment(
	department: str,
	doctor: str,
	name1: str,
	email: str,
	appointment_date: str,
	appointment_time: str,
) -> dict:
	if not all([department, doctor, name1, email, appointment_date, appointment_time]):
		frappe.throw(_("All appointment fields are required."))

	try:
		parsed_date = getdate(appointment_date)
	except Exception:
		frappe.throw(_("Invalid appointment date."))

	try:
		parsed_time = get_time(appointment_time)
	except Exception:
		frappe.throw(_("Invalid appointment time."))

	doctype_name = _get_appointment_doctype_name()

	if not doctype_name:
		frappe.throw(_("Appointment doctype not found."))

	doc = frappe.get_doc(
		{
			"doctype": doctype_name,
			"department": department,
			"doctor": doctor,
			"name1": name1,
			"email": email,
			"appointment_date": parsed_date,
			"appointment_time": parsed_time,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {"message": _("Appointment submitted successfully.")}
