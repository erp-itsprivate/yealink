# Copyright (c) 2025, ItsPrivate and contributors
# For license information, please see license.txt

import frappe
import ast,json
from frappe.model.document import Document


class PBXCDRs(Document):
	def after_insert(self):		 
		print(self.name)
		print('------------------------------------------')
		#try:
		data= ast.literal_eval(str(self.full_data))
		#except Exception as e :
		#	data=json.loads(str(self.full_data))
		# print(data.get('id'))	 
		# print(data.get('uid')  )
		# print(data.get('call_from') )
		# print(data.get('call_to') )
		# print(data.get('time') )
		# print(data.get('timestamp') )
		# print(data.get('duration') )
		# print(data.get('talk_duration') )
		# print(data.get('ring_duration') )
		# print(data.get('src_addr') )
		# print(data.get('disposition') )
		# print(data.get('call_type') )
		# print(data.get('reason') )
		# print(data.get('call_from_number') )
		# print(data.get('call_to_number') )
		# print(data.get('call_from_name') )
		# print(data.get('call_to_name') )
		# print(data.get('call_note') )
		# print(data.get('call_note_id'))
		# print(data.get('did') )
		# print(data.get('did_name') )
		# print(data.get('call_id') )
		# print(data.get('enb_call_note') )
		# print('====================================================')
		# self.cdr_id=data.get('id') or "NA"
		# self.uid=data.get('uid')  or "NA"
		# self.call_from=data.get('call_from') or "NA"
		# self.call_to=data.get('call_to') or "NA"
		# self.cdr_time=data.get('time') or "NA"
		# self.timestamp=data.get('timestamp') or "NA" 
		# self.duration=data.get('duration') or 0
		# self.talk_duration=data.get('talk_duration') or 0 
		# self.ring_duration =data.get('ring_duration') or 0 
		# self.src_addr=data.get('src_addr') or "NA"
		# self.disposition=data.get('disposition') or "NA"
		# self.call_type=data.get('call_type') or "NA"
		# self.reason=data.get('reason') or "NA"
		# self.call_from_number=data.get('call_from_number') or "NA"
		# self.call_to_number=data.get('call_to_number') or "NA"
		# self.call_from_name=data.get('call_from_name') or "NA"
		# self.call_to_name=data.get('call_to_name') or "NA"
		# self.call_note=data.get('call_note') or "NA"
		# self.call_note_id=data.get('call_note_id') or "NA"
		# self.did=data.get('did') or "NA"
		# self.did_name=data.get('did_name') or "NA"
		# self.call_id=data.get('call_id') or "NA"
		# self.enb_call_note=data.get('enb_call_note') or "NA"
		updates= {
			"cdr_id" : str(data.get('id')) or "NA",
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
		"call_from_number":str(data.get('call_from_number')) or "NA",
		"call_to_number":str(data.get('call_to_number') )or "NA",
		"call_from_name":str(data.get('call_from_name')) or "NA",
		"call_to_name":str(data.get('call_to_name')) or "NA",
		"call_note":str(data.get('call_note')) or "NA",
		"call_note_id":str(data.get('call_note_id')) or "NA",
		"did":str(data.get('did')) or "NA",
		"did_name":str(data.get('did_name')) or "NA",
		"call_id":str(data.get('call_id')) or "NA",
		"enb_call_note":str(data.get('enb_call_note')) or "NA"
		}
 
		
		frappe.db.set_value(self.doctype, self.name, updates)
		#print(updates)
		#print(data.get('call_note'))
		#self.call_note=str(data.get('call_note')) or "NA",
		#print(ast.literal_eval(str(data.get('call_note'))))
		#self.save()
	 
