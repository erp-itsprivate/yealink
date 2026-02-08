# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)
class PBXUser(Document):
	def on_update(self):	
		try:	
			if frappe.db.count("PBX User Extension", filters={"parent" :self.name,"disabled":1,"is_default":1}) > 0 :
					frappe.throw("You Can't deactive default Extension")
			if frappe.db.count("PBX User Extension", filters={"parent" :self.name,"is_default":1}) > 1 :
					frappe.throw("You Can't make multiple default Extension")
		except Exception as e :
				logger_exception.error(f" file => pbx_user.py method =>  on_update  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbx_user.py method =>  on_update  self  {self} {frappe.get_traceback()} ", title="Yealink") 

	

