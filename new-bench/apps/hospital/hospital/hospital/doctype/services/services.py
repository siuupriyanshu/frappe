

# import frappe
from frappe.model.document import Document


class services(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		emergency_care: DF.Data | None
		is_published: DF.Check
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		if not self.title and self.emergency_care:
			self.title = self.emergency_care
