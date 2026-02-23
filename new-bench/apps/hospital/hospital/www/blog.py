import frappe
from hospital.www.page_context import set_common_context

def get_context(context: dict) -> dict:
    context = set_common_context(context, "blog", "Blog - Medinova")

    page = int(frappe.form_dict.get("page", 1))
    limit = 6                     # items per page
    start = (page - 1) * limit      # offset

    total_blogs = frappe.db.count("blogs", {"is_published": 1})

    context["blogs"] = frappe.get_all(
        "blogs",
        fields=["name", "title", "description", "author", "views", "comments"],
        filters={"is_published": 1},
        order_by="creation desc",
        start=start,
        page_length=limit,
        ignore_permissions=True,
    )

    context["page"] = page
    context["limit"] = limit
    context["total"] = total_blogs
    context["pages"] = (total_blogs + limit - 1) // limit  

    return context