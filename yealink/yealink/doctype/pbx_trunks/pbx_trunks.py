# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)

class PBXTrunks(Document):
	def on_update(self):	
		try:	
			trunks=[]
			print(self.as_json())
			for trunk in self.company_trunks:
				trunks.append(trunk.trunk)
			has_duplicates = len(trunks) != len(set(trunks))
			if has_duplicates > 0 :
				frappe.throw('Duplicate Trunks')
		except Exception as e :
				logger_exception.error(f" file => pbxtrunks.py method =>  on_update  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbxtrunks.py method =>  on_update  self  {self} {frappe.get_traceback()} ", title="Yealink") 

	
