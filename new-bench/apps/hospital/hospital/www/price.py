import frappe

from hospital.www.page_context import set_common_context


def get_context(context: dict) -> dict:
	context = set_common_context(context, "price", "Pricing - Medinova")
	context["medical_programs"] = frappe.get_all(
		"medical program",
		fields=["title", "price", "description"],
		filters={"is_published": 1},
		order_by="creation desc",
	)
	return context
