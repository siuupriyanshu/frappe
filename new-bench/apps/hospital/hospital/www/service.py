import frappe

from hospital.www.page_context import set_common_context


def get_context(context: dict) -> dict:
	context = set_common_context(context, "service", "Services - Medinova")
	context["services"] = frappe.get_all(
		"services",
		fields=["title", "description", "emergency_care"],
		filters={"is_published": 1},
		order_by="creation desc",
	)
	return context
