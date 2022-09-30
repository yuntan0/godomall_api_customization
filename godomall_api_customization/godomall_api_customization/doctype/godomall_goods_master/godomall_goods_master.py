# Copyright (c) 2022, John Park and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate
from frappe.model.document import Document

class GodomallGoodsmaster(Document):
	pass
	# def validate(self):
	# 	if not self.release_bundle_yn:
	# 		frappe.throw(_("Please edit Bundle YN"))
