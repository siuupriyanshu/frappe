from hospital.www.page_context import set_common_context


def get_context(context: dict) -> dict:
	return set_common_context(context, "price", "Pricing - Medinova")
