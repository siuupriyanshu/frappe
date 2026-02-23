import frappe

from hospital.www.page_context import set_common_context


def _get_blog(blog_name: str | None):
	filters = {"is_published": 1}
	if blog_name:
		filters["name"] = blog_name

	blog = frappe.db.get_value(
		"blogs",
		filters,
		["name", "title", "description", "author", "views", "comments"],
		as_dict=True,
	)

	if blog or not blog_name:
		return blog

	return frappe.db.get_value(
		"blogs",
		{"title": blog_name, "is_published": 1},
		["name", "title", "description", "author", "views", "comments"],
		as_dict=True,
	)


def _add_comment(blog_name: str | None, context: dict) -> None:
	if not (frappe.request and frappe.request.method == "POST"):
		return

	if not frappe.form_dict.get("add_comment"):
		return

	commenter_name = (frappe.form_dict.get("commenter_name") or "").strip()
	comment_text = (frappe.form_dict.get("comment_text") or "").strip()
	blog_reference = (frappe.form_dict.get("blog_name") or blog_name or "").strip()

	if not blog_reference or not commenter_name or not comment_text:
		context.comment_error = "Name and comment are required."
		return

	frappe.get_doc(
		{
			"doctype": "comments",
			"blogs": blog_reference,
			"commenter_name": commenter_name,
			"comment_text": comment_text,
		}
	).insert(ignore_permissions=True)

	frappe.db.commit()
	context.comment_success = "Your comment was added successfully."


def get_context(context: dict) -> dict:
	context = set_common_context(context, "detail", "Blog Detail - Medinova")
	context.comment_success = None
	context.comment_error = None

	blog_name = (frappe.form_dict.get("blog") or frappe.form_dict.get("name") or "").strip() or None
	_add_comment(blog_name, context)

	blog = _get_blog(blog_name)
	if not blog:
		blog = frappe.db.get_value(
			"blogs",
			{"is_published": 1},
			["name", "title", "description", "author", "views", "comments"],
			as_dict=True,
			order_by="creation desc",
		)

	context.blog = blog

	context.blog_comments = []
	if blog:
		context.blog_comments = frappe.get_all(
			"comments",
			fields=["name", "commenter_name", "comment_text", "creation"],
			filters={"blogs": blog.name},
			order_by="creation asc",
			ignore_permissions=True,
		)

		if not context.blog_comments:
			context.blog_comments = frappe.get_all(
				"comments",
				fields=["name", "commenter_name", "comment_text", "creation"],
				filters={"blogs": blog.title},
				order_by="creation asc",
				ignore_permissions=True,
			)

		context.comment_count = len(context.blog_comments)
	else:
		context.comment_count = 0

	context.categories = frappe.get_all(
		"Categories",
		fields=["name", "category_name"],
		order_by="creation desc",
		ignore_permissions=True,
	)

	context.recent_posts = frappe.get_all(
		"blogs",
		fields=["name", "title"],
		filters={"is_published": 1},
		order_by="creation desc",
		page_length=5,
		ignore_permissions=True,
	)

	if blog:
		context.recent_posts = [post for post in context.recent_posts if post.name != blog.name]

	return context
