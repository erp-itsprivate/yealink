# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from yealink.utils import integrate,retry_on_token_expiry,process_code,get_user_extension,get_contact
from frappe.utils import get_datetime
from functools import wraps
import hashlib
import json
import pymysql

logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)

class PBXSettings(Document):
	def on_update(self):
		try:
			type_filters=[]
			for webhook_filter in self.webhook_events:
				type_filters.append({"type":webhook_filter.event_type_filter,"filter_code":webhook_filter.event_filter,"action_code":webhook_filter.event_action})
			self.db_set('webhook_event_filter',str(type_filters),False,False,True)	
		except Exception as e :
				logger_exception.error(f" file => pbxsettings.py method =>  on_update  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbxsettings.py method =>  on_update  self  {self} {frappe.get_traceback()} ", title="Yealink") 

		
	@retry_on_token_expiry	
	def get_extension_id(self):
		try:
			get_extension_url=self.url+self.get_extension_api
			query_params = {
						"access_token":self.pbx_token,		
				}
			res=integrate(url=get_extension_url,token=None,req_data=None,query_params=query_params,method=self.get_extension_method)
			
			
			if res.json().get('errcode') == 0 :			
					for data in  res.json().get('data'):
						print(data.get('number'))
						if frappe.db.exists("PBX User Extension", {"disabled":0,"pbx_ext":data.get('number')}):
							user_ext=frappe.get_doc("PBX User Extension", {"disabled":0,"pbx_ext":data.get('number')})
							user_ext.db_set('pbx_id',data.get('id'),False,False,True)
			
						
			return res
		except Exception as e :
				logger_exception.error(f" file => pbxsettings.py method =>  get_extension_id  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbxsettings.py method =>  get_extension_id  self  {self} {frappe.get_traceback()} ", title="Yealink") 

	
	
	@retry_on_token_expiry
	def get_ext_stat(self,extension_number):
		try:
			get_ext_stat_url=self.url+self.get_extension_stat_api
			
			pbx_ext=frappe.get_all("PBX User Extension",fields=['name','pbx_id'], filters=[["disabled","=",0],["pbx_ext","=",extension_number],['pbx_id', '!=',None]])[0]
			query_params = {
							"access_token":self.pbx_token,	
							"id": pbx_ext.pbx_id,

					}
			
				
			res=integrate(url=get_ext_stat_url,token=None,req_data=None,query_params=query_params,method=self.get_extension_stat_method)
			
			if res.json().get('errcode') == 0  :
					status=res.json().get('data').get('presence_status')
					print(res.json().get('data').get('presence_status'))
					frappe.db.set_value("PBX User Extension", pbx_ext.name, "status", status, update_modified=False)
					frappe.db.commit()
			return res	
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_ext_stat  self  {self} extension_number {extension_number} {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_ext_stat  self  {self} extension_number {extension_number} {frappe.get_traceback()} ", title="Yealink") 

		
	def get_contact_for_cdr(self):
		try:
			for cdr in frappe.get_all('PBX CDRs',filters=[['related_doctype_id','=',None],['pbx','=',self.name],['num_tries_get_contact','<=',self.num_tries_get_contact]],fields=['name']):
				cdr_doc=frappe.get_doc("PBX CDRs",cdr.name)
				updates={"num_tries_get_contact":cdr_doc.num_tries_get_contact+1}
				if cdr_doc.call_type =='Inbound':
					contact=get_contact(str(cdr_doc.call_from_number))
			
				if contact is not None :
					updates.update({"related_doctype_id":contact})
				else:
					contact=get_contact(str(cdr_doc.call_to_number))
					if contact is not None :
						updates.update({"related_doctype_id":contact})
			
				print(updates)
				frappe.db.set_value(cdr_doc.doctype, cdr_doc.name, updates)
			frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_contact_for_cdr  self  {self}   {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_contact_for_cdr  self  {self}  {frappe.get_traceback()} ", title="Yealink") 

	@frappe.whitelist()
	def get_phonebooks_to_sync(self):
		try:
			for phonebook_sync in self.pbx_contact_sync:
				if phonebook_sync.disable == 0 :
					object_from_code={}
					global_and_local_variable={}
					exec(phonebook_sync.contacts_selector,global_and_local_variable, object_from_code)
					tmp_mapping_list=[]
					for mapping in self.mapping_phones:
								tmp_mapping_list.append({
										"num_type": mapping.mapping_pbx_phone,
										"number": mapping.mapping_id
									})
					mapping  = {int(item['number']): item['num_type'] for item in tmp_mapping_list}

					if frappe.db.exists('PBX PhoneBook Sync', self.name + '-'+phonebook_sync.address_book):				
						doc=frappe.get_doc('PBX PhoneBook Sync', self.name + '-'+phonebook_sync.address_book)
						if ('data'  in object_from_code):           
							data=object_from_code['data']
							
							for element in data :
								data_str = json.dumps(element, sort_keys=True)
								hash_value = hashlib.sha256(data_str.encode()).hexdigest()	
								element.update({'hash':hash_value}) 
									
								if len (frappe.get_all("PBX Contacts Synced", fields=["*"], filters = {"parent":doc.name,"hash":hash_value})) == 0 :
								
									element.update({'status':'NEW'})  
									contact=doc.append("synced_contacts", {})
									contact.hash=hash_value
									
									contact.doctype_synced=element.doctype_synced
									contact.doctype_id=element.doctype_id
									contact.first_name=element.first_name				
									contact.last_name=element.last_name
									contact.email=element.email
									contact.gender=element.gender
									contact.company	=element.company		 
									contact.parent=doc 	
									contact.status='NEW'
									contact.synced=0
									phones=element.all_phones
									num_list = [n.strip() for n in phones.split(",")]
									
									for i, n in enumerate(num_list, start=1):
										num_type = mapping.get(i)
										contact.set(num_type,n)
									contact.save(ignore_permissions=True)
								
							
							for sync_contact in doc.synced_contacts:
								match = next((rec for rec in data if rec["hash"] == sync_contact.hash), None)
								if match :									
									if sync_contact.status=='DELETED':
										sync_contact.status='NEW'
										sync_contact.synced=0
								else:								 
									sync_contact.status='DELETED'
									sync_contact.synced=0
									sync_contact.save(ignore_permissions=True)

						doc.save(ignore_permissions=True)	
						frappe.db.commit()
					else:
						
						doc = frappe.get_doc({
								'doctype': 'PBX PhoneBook Sync',
								'phonebook': phonebook_sync.address_book,
								'pbx':self.name,
								'sync_name': self.name + '-'+phonebook_sync.address_book			
							})
						
						if ('data'  in object_from_code):           
							data=object_from_code['data']
							
							for element in data :
								data_str = json.dumps(element, sort_keys=True)
								hash_value = hashlib.sha256(data_str.encode()).hexdigest()
								contact=doc.append("synced_contacts", {})
								contact.hash=hash_value
								
								contact.doctype_synced=element.doctype_synced
								contact.doctype_id=element.doctype_id
								contact.first_name=element.first_name				
								contact.last_name=element.last_name
								contact.email=element.email
								contact.gender=element.gender
								contact.company	=element.company		 
								contact.parent=doc 	
								contact.status='NEW'
								contact.synced=0
								phones=element.all_phones
								num_list = [n.strip() for n in phones.split(",")]
								
								for i, n in enumerate(num_list, start=1):
									num_type = mapping.get(i)
									contact.set(num_type,n)
								contact.save(ignore_permissions=True)	
							doc.insert(ignore_permissions=True)
							frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_phonebooks_to_sync  self  {self}   {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_phonebooks_to_sync  self  {self}  {frappe.get_traceback()} ", title="Yealink") 

	@retry_on_token_expiry						
	def create_contact(self,contact,phonebook_id):
		try:
			create_contact_url=self.url+self.create_contact_api
			query_params = {
						"access_token":self.pbx_token,		
				}
			number_list = []
			if contact.mobile_number is not None:
				number_list.append({
					"num_type": "mobile_number",
					"number": contact.mobile_number
				})
			if contact.mobile_number2 is not None:
				number_list.append({
					"num_type": "mobile_number2",
					"number": contact.mobile_number2
				})
			if contact.business_number is not None:
				number_list.append({
					"num_type": "business_number",
					"number": contact.business_number
				})
			if contact.business_number2 is not None:
				number_list.append({
					"num_type": "business_number2",
					"number": contact.business_number2
				})
			params ={
					
					"first_name": contact.first_name,
					"last_name": contact.last_name,
					"company":contact.company or "N/A" ,
					"email": contact.email or "N/A",
					"phonebook_id_list": [
						int(phonebook_id)
					],
					"number_list":  number_list
					}
			
			
			res=integrate(url=create_contact_url,token=None,req_data=params,query_params=query_params,method=self.create_contact_method)
			print(res.json())
			if res.status_code==200:
				if res.json().get('errcode') == 0 :
					contact_synced=frappe.get_doc('PBX Contacts Synced',contact.name)
					contact_synced.pbx_id=res.json().get('id') 
					contact_synced.synced=1
					contact_synced.save()
			frappe.db.commit()

			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  create_contact  self  {self}  contact {contact} phonebook_id {phonebook_id}  {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  create_contact  self  {self}  contact {contact} phonebook_id {phonebook_id} {frappe.get_traceback()} ", title="Yealink") 

	
	@frappe.whitelist() 						
	def get_cdrs_by_date(self):
		try:
			if self.last_cdr_date is None:
				self.last_cdr_date=frappe.utils.get_datetime()
				self.get_all_cdrs()
				
				
			else:
				diff= frappe.utils.get_datetime() - get_datetime(self.last_cdr_date) 
				
				if int(diff.total_seconds()/60) >= self.diff_time_to_sync:
					self.get_cdrs(page=None)
			print('conmit')
			frappe.db.commit()
			return "SUCCESS"
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_cdrs_by_date  self  {self}    {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_cdrs_by_date  self  {self}   {frappe.get_traceback()} ", title="Yealink") 


	@retry_on_token_expiry						
	def get_all_cdrs(self):
		try:
			get_cdrs_url=self.url+self.get_cdrs_api
			query_params = {
						"access_token":self.pbx_token,	
						"page_size":	1,
						
				}
			res=integrate(url=get_cdrs_url,token=None,req_data=None,query_params=query_params,method=self.get_cdrs_method)
			print(res.json())
			if res.status_code==200:
				if res.json().get('errcode') == 0 :
					self.total_cdrs=res.json().get('total_number')
					self.save()
					if (frappe.db.count("PBX CDRs", filters={"pbx" :self.name}) != self.total_cdrs ):
						print(self.total_cdrs)
						missing_cdr=self.total_cdrs-frappe.db.count("PBX CDRs", filters={"pbx" :self.name})
						count_of_call_cdr=int(missing_cdr/self.cdr_page_size)
						if count_of_call_cdr != 1 :
							count_of_call_cdr=count_of_call_cdr+1
						print(count_of_call_cdr)
						for i in range(count_of_call_cdr):
							print('in loop ---------------------------------------------------' + str(i))
							self.get_cdrs(i+1)
			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_all_cdrs  self  {self}    {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_all_cdrs  self  {self}   {frappe.get_traceback()} ", title="Yealink") 



	@retry_on_token_expiry						
	def get_cdrs(self,page):
		try:
			if page is not None:
				get_cdrs_url=self.url+self.get_cdrs_api
				query_params = {
							"access_token":self.pbx_token,	
							"page_size":	self.cdr_page_size,
							"sort_by": "time",
							"order_by":"desc",
							"page":page
					}
				
				
				res=integrate(url=get_cdrs_url,token=None,req_data=None,query_params=query_params,method=self.get_cdrs_method)
			else:
				get_cdrs_url=self.url+self.get_cdrs_api_by_datetime
				start_time=get_datetime(self.last_cdr_date).replace(hour=0, minute=0, second=0).timestamp()
				end_time=frappe.utils.get_datetime().replace(hour=23, minute=59, second=59).timestamp()
				

				query_params = {
							"access_token":self.pbx_token,	
							"start_time":	str(int(start_time)),
							"end_time":  str(int(end_time))
							
					}			
				print(query_params)
				res=integrate(url=get_cdrs_url,token=None,req_data=None,query_params=query_params,method=self.get_cdrs_method)
				
			if res.status_code==200:
				if res.json().get('errcode') == 0 :			
					if  res.json().get('total_number') > 0 :
					
						self.db_set('total_cdrs',res.json().get('total_number'),False,False,True)
						
						self.db_set('last_cdr_date',frappe.utils.get_datetime(),False,False,True)
						
						print(self.last_cdr_date)	
						for data in  res.json().get('data'):
							if self.filter_cdr_code is not None and len(self.filter_cdr_code) > 0 :
								if process_code(self.filter_cdr_code,str(data))==True :
									print( str(data))
									doc = frappe.get_doc({
											'doctype': 'PBX CDRs',
											'pbx':self.name,
											'full_data': str(data),
													
										})
									try:
										doc.insert()
										#print(doc.name)
									except   pymysql.err.IntegrityError as e:
										
										frappe.db.rollback()
										##where call_type != 'Internal'
										print("Exception name:", type(e).__name__)
						frappe.db.commit()
						
			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_cdrs  self  {self}    {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_cdrs  self  {self}   {frappe.get_traceback()} ", title="Yealink") 


	@retry_on_token_expiry						
	def delete_contact(self,contact):
		try:
			if (contact.pbx_id != 0):
				delete_contact_url=self.url+self.delete_contact_api
				query_params = {
							"access_token":self.pbx_token,		
							"id":contact.pbx_id
					}
		
			
			res=integrate(url=delete_contact_url,token=None,req_data=None,query_params=query_params,method=self.delete_contact_method)
			print(res.json())
			if res.status_code==200:
				if res.json().get('errcode') == 0 :
					contact_synced=frappe.get_doc('PBX Contacts Synced',contact.name)
					contact_synced.pbx_id=0 
					contact_synced.synced=1
					contact_synced.save()
			frappe.db.commit()

			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  delete_contact  self  {self}  contact {contact}   {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  delete_contact  self  {self} contact {contact}   {frappe.get_traceback()} ", title="Yealink") 

		

	def get_token(self):
		try:
			print('get token')
			token_url=self.url+self.get_token_url
			params ={
					
					"password": self.password,
					"username": self.username
					}
			res=integrate(url=token_url,token=None,req_data=params,method=self.get_token_method)
			print(res.json())
			if res.status_code==200:
				data=res.json()
				self.pbx_token=data.get('access_token')
				self.pbx_refresh_token=data.get('refresh_token')
				self.save()
				frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_token  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_token  self  {self}    {frappe.get_traceback()} ", title="Yealink") 

	

	
	def delete_phonebooks(self):
		try:
			for phonebook in self.pbx_phonebooks:
				phonebook.delete()
			
			frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  delete_phonebooks  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  delete_phonebooks  self  {self}    {frappe.get_traceback()} ", title="Yealink") 


	@frappe.whitelist()
	@retry_on_token_expiry
	def get_phonebooks(self):
		try:
			self.delete_phonebooks()
			get_phonebooks_url=self.url+self.get_phonebook_api
			query_params = {
						"access_token":self.pbx_token,		
				}
			
			res=integrate(url=get_phonebooks_url,token=None,req_data=None,query_params=query_params,method=self.get_phonebook_method)
			print(res.json())
			if res.json().get('errcode') == 0 and res.json().get('total_number') > 1 :
				for phonebook in res.json().get('data'):
					if (len(frappe.get_all("PBX PhoneBooks", fields=["*"], filters = {"parent":self.name,"id":phonebook.get('id'),"phonebook_name":phonebook.get('name')}))==0):
						self.insert_phonebook(phonebook.get('id'),phonebook.get('name'),phonebook.get('total'))

			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  get_phonebooks  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  get_phonebooks  self  {self}    {frappe.get_traceback()} ", title="Yealink") 

	
	def insert_phonebook(self,id,phonebook_name,total_contacts):
		try:
			print('insert pbx_phonebooks')
			new_row = self.append("pbx_phonebooks", {
					"id":str(id),
				"phonebook_name": str(phonebook_name),
				"total_contacts":int(total_contacts)
				})
			self.save()
			frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  insert_phonebook  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  insert_phonebook  self  {self}    {frappe.get_traceback()} ", title="Yealink") 

	
	
	 
	@frappe.whitelist()
	@retry_on_token_expiry
	def create_phonebooks(self,phonebook_name):
		try:
			create_phonebooks_url=self.url+self.create_phonebook_api
			query_params = {
						"access_token":self.pbx_token,		
				}
			params={
			
				"name": str(phonebook_name),
			
			}
			res=integrate(url=create_phonebooks_url,token=None,req_data=params,query_params=query_params,method=self.create_phonebook_method)
			print(res.json())
			return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  create_phonebooks  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  create_phonebooks  self  {self}    {frappe.get_traceback()} ", title="Yealink") 


	

	def insert_event(self,event_type,event_id):
		try:
			print('insert event')
			new_row = self.append("pbx_events", {
					"event_date_time":frappe.utils.get_datetime(),
				"event_type": str(event_type),
				"event_id":str(event_id)
				})
			self.save()
			frappe.db.commit()
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  insert_event  self  {self}  event_type {event_type}  event_id {event_id}    {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  insert_event  self  {self}  event_type {event_type} event_id {event_id} {frappe.get_traceback()} ", title="Yealink") 



	def refresh_token(self):
			try:
				print('refrsh token')
				params={
					"refresh_token": self.pbx_refresh_token

				}
				refresh_url=self.url+self.refresh_token_url
				res=integrate(url=refresh_url,token=None,req_data=params,method=self.refresh_token_method)
				print(res.json())
				if res.status_code==200:
						if res.json().get('errcode') == 0 :
							data=res.json()
							self.pbx_token=data.get('access_token')
							self.pbx_refresh_token=data.get('refresh_token')
							self.save()
							frappe.db.commit()
						if res.json().get('errcode')==10004:
							self.get_token()
					
				return res.json()
			except Exception as e :
				logger_exception.error(f" file => pbxsettings.py method =>  refresh_token  self  {self}      {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbxsettings.py method =>  refresh_token  self  {self} {frappe.get_traceback()} ", title="Yealink") 


	
	
	@retry_on_token_expiry
	def make_call(self,from_number,to_number):
		try:
			if get_user_extension(frappe.session.user) != 'None':
				call_url=self.url+self.call_api
				params={
				
					"caller": get_user_extension(frappe.session.user),
					"callee": str(to_number),
				
					"auto_answer": "no"
				}
				query_params = {
							"access_token":self.pbx_token,		
					}
				res=integrate(url=call_url,token=None,req_data=params,query_params=query_params,method=self.call_api_method)
				self.insert_event("CALL",res.json().get('call_id'))
				return res
		except Exception as e :
			logger_exception.error(f" file => pbxsettings.py method =>  make_call  self  {self}      {frappe.get_traceback()} ")
			frappe.log_error(message=f" file => pbxsettings.py method =>  make_call  self  {self} {frappe.get_traceback()} ", title="Yealink") 

