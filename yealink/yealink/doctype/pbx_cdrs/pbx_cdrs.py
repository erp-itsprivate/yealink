# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
import ast,json
from frappe.model.document import Document
from yealink.utils import get_contact,get_extension_user,get_extension_email,normalize_syria_number
from frappe.desk.form.assign_to import add 
from frappe.utils import escape_html
logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)
class PBXCDRs(Document):
	def create_task_for_notanswered(self):
		try:
			self.reload()
			
			pbx=frappe.get_doc('PBX Settings',self.pbx)
			assigned_to_list=[v.usr for v in pbx.not_answered_users]
				
			assigned_to=get_extension_user(self.call_to_number)
			
			
			description = f"Call From #({str(self.call_from_number)}) " 
				
			task = frappe.get_doc({
			"doctype": "Task",
			"subject": f"Call From {str(self.call_from_number)} " ,
			"description": description,
		
			"status": "Open"
			})
			print(assigned_to_list)
			print(self.call_from_number)
		# Insert into DB
			task.insert(ignore_permissions=True)
			if assigned_to != 0:
				assigned_to_list.append(assigned_to)
		# Assign to a user if provided
		
			add({
				"assign_to": assigned_to_list, 
				"doctype": "Task",
				"name": task.name,
				"description": description,
				"priority": task.priority
			})
			frappe.db.sql(""" 
			update `tabPBX CDRs` set task_created =1  where call_id =%s 
			""", (self.call_id))		
			frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbx_cdrs.py method =>  create_task_for_notanswered  self  {self} {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbx_cdrs.py method =>  create_task_for_notanswered  self  {self} {frappe.get_traceback()} ", title="Yealink") 

	


	
		

	def after_insert(self):	
		try:
			data= ast.literal_eval(str(self.full_data))
		except Exception as e :
			data=json.loads(str(self.full_data))	 
		try:
			updates= {
				"cdr_id" : str(data.get('id')) if  str(data.get('id')) != 'None' else str(data.get('new_id'))    or "NA",
			"uid": str(data.get('uid'))  or "NA",
			"call_from": str(data.get('call_from')) or "NA",
			"call_to": str(data.get('call_to')) or "NA",
			"cdr_time": str(data.get('time')) or "NA",
			"timestamp":str(data.get('timestamp')) or "NA" ,
			"duration":  data.get('duration') or 0,
			"talk_duration": data.get('talk_duration') or 0, 
			"ring_duration":data.get('ring_duration') or 0 ,
			"src_addr":str(data.get('src_addr')) or "NA",
			"disposition":str(data.get('disposition')) or "NA",
			"call_type":str(data.get('call_type')) or "NA",
			"reason":str(data.get('reason') ) or "NA",
			"call_from_number":normalize_syria_number(str(data.get('call_from_number'))) or "NA",
			"call_to_number":normalize_syria_number(str(data.get('call_to_number') ))or "NA",
			"call_from_name":str(data.get('call_from_name')) or "NA",
			"call_to_name":str(data.get('call_to_name')) or "NA",
			"call_note":str(data.get('call_note')) or "NA",
			"call_note_id":str(data.get('call_note_id')) or "NA",
			"did":str(data.get('did')) or "NA",
			"did_name":str(data.get('did_name')) or "NA",
			"call_id":str(data.get('call_id')) or "NA",
			"enb_call_note":str(data.get('enb_call_note')) or "NA",
			"src_trunk":str(data.get('src_trunk')) or "NA",
			"dst_trunk" : str(data.get('dst_trunk')) or "NA", 
			"company":  frappe.get_doc("PBX Company Trunk", {"trunk": str(data.get("src_trunk"))}).company if frappe.db.exists("PBX Company Trunk", {"trunk": str(data.get("src_trunk"))}) else ( frappe.get_doc("PBX Company Trunk", {"trunk": str(data.get("dst_trunk"))}).company if frappe.db.exists("PBX Company Trunk", {"trunk": str(data.get("dst_trunk"))}) else None)

			}
			if str(data.get('call_type')) =='Inbound':
				contact=get_contact(normalize_syria_number(str(data.get('call_from_number'))))
			
				if contact is not None :
					updates.update({"related_doctype_id":contact.name,"related_doctype":contact.doctype})
			else:
				contact=get_contact(normalize_syria_number(str(data.get('call_to_number'))))
				if contact is not None :
					updates.update({"related_doctype_id":contact.name,"related_doctype":contact.doctype})
			print(updates)
			
			frappe.db.set_value(self.doctype, self.name, updates)
		except Exception as e :
			logger_exception.error(f" file => pbx_cdrs.py method =>  after_insert  self  {self} {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbx_cdrs.py method =>  after_insert  self  {self} {frappe.get_traceback()} ", title="Yealink") 

	

		#self.create_task_for_notanswered()
	


def get_phone_cdrs(incoming,outgoing,number):
	try:
		cdrs=[]
		if incoming==True:
			if (frappe.db.count("PBX CDRs", filters={"call_type" :'Inbound','call_from_number':number}) > 0):
				cdrs.append(frappe.get_all('PBX CDRs', filters=[["call_type",'=','Inbound'],['call_from_number','=',number]],fields=['call_from','call_from_name','call_from_number','call_to','call_to_name','call_to_number','call_type','cdr_time','disposition','reason','talk_duration']))
		if outgoing==True:
			if (frappe.db.count("PBX CDRs", filters={"call_type" :'Outbound','call_to_number':number}) > 0):
				cdrs.append(frappe.get_all('PBX CDRs', filters=[["call_type",'=','Outbound'],['call_to_number','=',number]],fields=['call_from','call_from_name','call_from_number','call_to','call_to_name','call_to_number','call_type','cdr_time','disposition','reason','talk_duration']))
		if len(cdrs) >0 : 
			return cdrs
	except Exception as e :
			logger_exception.error(f" file => pbx_cdrs.py method =>  get_phone_cdrs  incoming  {incoming} outgoing  {outgoing} number {number} {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbx_cdrs.py method =>  get_phone_cdrs  incoming  {incoming}  outgoing {outgoing}  number {number} {frappe.get_traceback()} ", title="Yealink") 



def get_phone_cdrs_by_cdrid(number,limit):	
	try:
		from datetime import datetime
		all_cdrs= frappe.get_all('PBX CDRs',or_filters=[[ "call_to_number", "=", number],[ "call_from_number", "=", number]],fields=['call_id'],order_by='cdr_id desc',distinct=True,limit=limit,pluck='call_id')
		cdrs=frappe.get_all('PBX CDRs',filters=[['call_id','in',all_cdrs]],order_by='cdr_id',fields=['call_type','related_doctype_id','company','call_from_name','talk_duration','disposition','call_to_name','call_id','cdr_id','cdr_time'])
		docs = [ {**d, "creation": datetime.strptime(d["cdr_time"], "%d/%m/%Y %H:%M:%S") } for d in cdrs ]
		return docs
	except Exception as e :
			logger_exception.error(f" file => pbx_cdrs.py method =>  get_phone_cdrs_by_cdrid  number  {number} limit  {limit}   {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbx_cdrs.py method =>  get_phone_cdrs_by_cdrid  number  {number}  limit {limit}   {frappe.get_traceback()} ", title="Yealink") 



