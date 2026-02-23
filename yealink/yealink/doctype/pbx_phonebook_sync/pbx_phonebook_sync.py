# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

logger_exception = frappe.logger("Yealink.error", allow_site=True, file_count=50)
logger_exception.setLevel(20)
class PBXPhoneBookSync(Document):
 


	def on_update(self):
		#self.sync()
		pass

	def sync_background(self):
		frappe.enqueue(
                self.sync, # python function or a module path as string
            queue="long", # one of short, default, long
             timeout=None, # pass timeout manually
            is_async=True, # if this is True, method is run in worker
             now=False, # if this is True, method is run directly (not in a worker)
             job_id="job_phonebook_sync "+str(self.name), # specify a job name
             job_name="job_phonebook_sync "+str(self.name),
             enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request
             at_front=False, # put the job at the front of the queue
            )
	def sync(self):
		try:
			print("sync")
			pbx_setting=frappe.get_doc('PBX Settings',self.pbx)
			pbx_setting.get_phonebooks()
			if len(frappe.get_all("PBX PhoneBooks", fields=["*"], filters = {"parent":pbx_setting.name,"phonebook_name":self.phonebook})) ==1 : 	
				phonebook_id=frappe.get_all("PBX PhoneBooks", fields=["*"], filters = {"parent":pbx_setting.name,"phonebook_name":self.phonebook})[0]["id"]
				
				contacts=frappe.get_all("PBX Contacts Synced", fields=["*"], filters = {"parent":self.name,"synced":0,"status":"NEW"})
				 
				for contact in contacts:
				
					pbx_setting.create_contact(contact,phonebook_id)
				
				del_contacts=frappe.get_all("PBX Contacts Synced", fields=["*"], filters = {"parent":self.name,"synced":0,"status":"DELETED"})
				for contact in del_contacts:
					
					pbx_setting.delete_contact(contact)
				print("new is " + str(len(contacts)))
				print("deleted is " + str(len(del_contacts)))
				print("contacts is " + str(self.total_contacts))
				new_contacts=self.total_contacts + len(contacts)-len(del_contacts)
				frappe.db.set_value("PBX PhoneBook Sync", self.name, "last_sync", frappe.utils.now_datetime())
				print("contacts is " + str(new_contacts))
				
				self.db_set('total_contacts',new_contacts,False,False,True)         
				
			pbx_setting.get_phonebooks()
		except Exception as e :
				logger_exception.error(f" file => pbx_phonebook_sync.py method =>  sync  self  {self} {frappe.get_traceback()} ")
				frappe.log_error(message=f" file => pbx_phonebook_sync.py method =>  sync  sync  {self} {frappe.get_traceback()} ", title="Yealink") 
