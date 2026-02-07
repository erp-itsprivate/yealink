# Copyright (c) 2026, ItsPrivate and contributors
# For license information, please see license.txt

import frappe,ast
from frappe.model.document import Document


class PBXAPIEvents(Document):
	def after_inser(self):
		json_data=ast.literal_eval(self.msg)
		if json_data.get('info') != '':
			self.db_set('path',json_data.get('info'),False,False,True)
