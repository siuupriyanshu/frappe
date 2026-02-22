import frappe

from hospital.www.page_context import set_common_context


def get_context(context: dict) -> dict:
	context = set_common_context(context, "blog", "Blog - Medinova")
	context["blogs"] = frappe.get_all(
		"blogs",
		fields=["title", "description", "author", "views", "comments"],
		filters={"is_published": 1},
		order_by="creation desc",
	)
	return context
