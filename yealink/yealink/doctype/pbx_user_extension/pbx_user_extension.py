# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)

class PBXUserExtension(Document):
	pass


def get_status(extension_number):
	try:
		if len(frappe.get_all("PBX User Extension", filters=[["disabled","=",0],["pbx_ext","=",extension_number],['pbx_id', '!=',None]])) ==1:
			pbx_user_extension=frappe.get_all("PBX User Extension", filters=[["disabled","=",0],["pbx_ext","=",extension_number],['pbx_id', '!=',None]])[0].name	
			pbx_user_extension_doc=frappe.get_doc("PBX User Extension",pbx_user_extension)
			pbx=frappe.get_doc('PBX Settings',frappe.get_doc("PBX User",pbx_user_extension_doc.parent).pbx)
			pbx.get_ext_stat(extension_number)
			pbx_user_extension_doc.reload()
			return pbx_user_extension_doc.status
	except Exception as e :
				logger_exception.error(f" file => pbx_user_extension.py method =>  get_status  extension_number  {extension_number} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbx_user_extension.py method =>  get_status  extension_number  {extension_number} {frappe.get_traceback()} ", title="Yealink") 

	