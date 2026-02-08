# Copyright (c) 2026, ItsPrivate and contributors
# For license information, please see license.txt

import frappe,ast
from frappe.model.document import Document

logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)

class PBXAPIEvents(Document):
	def after_insert(self):
		try:
			json_data=ast.literal_eval(self.msg)
			if json_data.get('info') != '':
				self.db_set('path',json_data.get('info'),False,False,True)
		except Exception as e :
				logger_exception.error(f" file => pbxapievents.py method =>  after_insert  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbxapievents.py method =>  after_insert  self  {self} {frappe.get_traceback()} ", title="Yealink") 

