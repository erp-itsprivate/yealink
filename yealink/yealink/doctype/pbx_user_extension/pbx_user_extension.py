# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PBXUserExtension(Document):
	pass


def get_status(extension_number):
	if len(frappe.get_all("PBX User Extension", filters=[["disabled","=",0],["pbx_ext","=",extension_number],['pbx_id', '!=',None]])) ==1:
		pbx_user_extension=frappe.get_all("PBX User Extension", filters=[["disabled","=",0],["pbx_ext","=",extension_number],['pbx_id', '!=',None]])[0].name	
		pbx_user_extension_doc=frappe.get_doc("PBX User Extension",pbx_user_extension)
		pbx=frappe.get_doc('PBX Settings',frappe.get_doc("PBX User",pbx_user_extension_doc.parent).pbx)
		pbx.get_ext_stat(extension_number)
		pbx_user_extension_doc.reload()
		return pbx_user_extension_doc.status