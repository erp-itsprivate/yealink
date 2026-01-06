
import requests,ast,json
from functools import wraps
import frappe 
import re
import frappe
import hmac
import hashlib
import base64
from types import SimpleNamespace


@frappe.whitelist( allow_guest=True,methods=["POST"])
def incoming_call():
	try:
		# 1. Get the Secret Key (Store this in site_config or a Settings Doctype)
		# For now, we assume it is a string
		find_secret=False
		file_name = "my_file.txt"
		for secret in frappe.get_all('PBX Secret Settings', filters={"enabled":True},fields=['pbx','webhook_secret']):
			secret_key=secret.get('webhook_secret')
			# 2. Get the Signature from the Header
			# Yeastar sends it in 'X-Signature' (headers are case-insensitive in retrieval usually)
		
			received_signature = frappe.request.headers.get('X-Signature')
				
			
			if not received_signature:
				frappe.throw("Missing X-Signature header", exc=frappe.AuthenticationError)
			# 4. Compute the HMAC-SHA256 Signature
			# hmac.new(key, message, digest_method)
			payload_bytes = frappe.request.get_data()					
			computed_hash = hmac.new(
				key=secret_key.encode('utf-8'), # Key must be bytes	
				msg=payload_bytes, 	
				digestmod=hashlib.sha256
			).digest()

			# 5. Base64 Encode the result
			computed_signature = base64.b64encode(computed_hash).decode('utf-8')

			# 6. Compare (Securely)
			# hmac.compare_digest is better than '==' because it prevents timing attacks
			if hmac.compare_digest(computed_signature, received_signature):
				
				find_secret=True
				pbx=frappe.get_doc('PBX Settings',secret.get('pbx'))
				event_filter= ast.literal_eval(pbx.webhook_event_filter)
				raw_data = frappe.request.get_data(as_text=True)
				json_data = frappe.request.get_json(silent=True) 
				with open(file_name, 'a') as file:
					file.write("--- NEW REQUEST ---\n")
					file.write(f"Raw Data: {raw_data}\n")					 
					file.write("---------------------------------------------------------------------------------------------")
					
				form_data = frappe.form_dict				 
				associated = [v for v in event_filter if v.get('type') == str(json_data.get('type'))]
				if len(associated) ==1 :
					# Log success (Optional)
					# frappe.log_error("Signature Verified", "Yeastar Webhook")
					ggg=execute_code(associated[0].get('filter_code'),str(json_data))
					
						
						#file.write(str(len(associated))+"\n")
						#file.write(str(associated[0].get('filter_code'))+"\n")
						#file.write(str(json_data)+"\n")
						 
					if ggg['result']==True:
							abv=execute_code(associated[0].get('action_code'),str(json_data))
							
						# Log JSON if it exists
					
						# Log Raw Data (useful for debugging)
						
						
						# Log Form Data
					

						
					# Return success to Yeastar
					frappe.response['message'] = "Hello from Frappe!"
			

		if find_secret==False:
				# --- FAILURE: TAMPERED OR FAKE ---
				frappe.log_error(
					f"Expected: {computed_signature}\nReceived: {received_signature} IP {frappe.request.remote_addr}", 
					"Yeastar Signature Mismatch"
				)
				# Return 401 Unauthorized or 400 Bad Request
				frappe.response.status_code = 401
				return {"status": "failed", "message": "Invalid Signature"}
	except Exception as e :
				 
				frappe.log_error(message=f"  file => scale_transaction.py method =>  on_update   {frappe.get_traceback()} ", title="Yealink") 

	

def get_lead_from_number(phone_number):
    if frappe.db.exists('Contact Phone',{'phone':phone_number}):
        contact=frappe.get_doc('Contact Phone',{'phone':phone_number}).parent
        data=frappe.get_all('Dynamic Link', filters=[["parenttype",'=','Contact'],['parentfield','=','links'],['parent','=',contact],['link_doctype','=','Lead']],fields=['link_name'],limit=1,pluck='link_name')
        if len(data)==1 :
            return data[0]
        

@frappe.whitelist( allow_guest=True,methods=["POST"])
def incoming_call2():
	file_name = "my_file.txt"
	raw_data = frappe.request.get_data(as_text=True)
	info = {
        "method": frappe.request.method,
        "path": frappe.request.path,
        "headers": dict(frappe.request.headers),
        "query_string": frappe.request.query_string,
        "data": frappe.request.data,          # raw body
        "form_dict": frappe.local.form_dict,  # parsed params
        "cookies": frappe.request.cookies,
        "remote_addr": frappe.request.remote_addr,
		"secret" : frappe.request.headers.get("Authorization")
    }
    # 2. Try to get JSON safely
    # silent=True returns None instead of crashing if data isn't JSON
	json_data = frappe.request.get_json(silent=True) 

    # 3. Get Form Data (if sent as x-www-form-urlencoded)
	form_data = frappe.form_dict
	with open(file_name, 'a') as file:
		file.write("--- NEW REQUEST ---\n")
        
        # Log JSON if it exists
		if json_data:
			json_dd=json.dumps(json_data)
			file.write(f"JSON Data: {json_dd}  \n")
		else:
			file.write("No JSON Data found.\n")

        # Log Raw Data (useful for debugging)
		file.write(f"Raw Data: {raw_data}\n")
        
        # Log Form Data
		file.write(f"Form Dict: {str(form_data)}\n")

		file.write(f"all Info: {str(info)}\n")
	#with open(file_name, 'a') as file:
		#file.write(str(frappe.local.request)+"\n")
		#file.write(str(frappe.local.request.data)+"\n")
		#file.write(str(frappe.local.request.get_json())+"\n")
	
	frappe.response['message'] = "Hello from Frappe!"

def execute_code(code,parameter):
        data= ast.literal_eval(str(parameter))
		# Convert dict to object
        doc_obj = SimpleNamespace(**data)
        _locals = {
			"params": doc_obj
		}
        object_from_code = {}
        
        exec(code, _locals, object_from_code)
        return object_from_code
         

def process_code(code,data_to_validate):
	tokens = re.findall(r"_VS_[A-Za-z0-9_]+_VS_", code)
	cleaned = [t.replace("_VS_", "") for t in tokens]
	data= ast.literal_eval(str(data_to_validate))

	replacement={}
	for i in range(len(tokens)) :
		replacement.update({tokens[i]:data.get(cleaned[i])})
	for key, value in replacement.items():
		if isinstance(value, str):
			replace_with = repr(value)
		else:
			replace_with = str(value)
		code = code.replace(key, replace_with)
	object_from_code={}
	global_and_local_variable={}
	exec(code,global_and_local_variable, object_from_code) 
	if ('result'  in object_from_code):    
		return object_from_code['result']

def get_extension_user(extension_number):
	if frappe.db.exists('PBX User Extension',{'pbx_ext' : extension_number}):
		return frappe.get_doc('PBX User Extension',{'pbx_ext' : extension_number}).parent
	else:
		return False
	
def get_user_extension(user):
	if len(frappe.get_all('PBX User Extension',fields=['pbx_ext'],filters={'parent':user,'is_default':1})) ==1 :
		return frappe.get_all('PBX User Extension',fields=['pbx_ext'],filters={'parent':user,'is_default':1},pluck='pbx_ext')[0]
	


def get_extension_email(extension_number):
	if frappe.db.exists('PBX User Extension',{'pbx_ext' : extension_number}):
		return frappe.get_doc('User',frappe.get_doc('PBX User Extension',{'pbx_ext' : extension_number}).parent).email
	else:
		return False

def get_contact(phone_number):
	if frappe.db.exists('Contact Phone', {'phone' : phone_number}):
		return frappe.get_doc('Contact Phone',{'phone' : phone_number}).parent
	elif frappe.db.exists('Contact Phone', {'phone' : '9639'+phone_number}):
		return frappe.get_doc('Contact Phone',{'phone' :'9639'+ phone_number}).parent
	else:
		return None
	
def retry_on_token_expiry(func):
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			# 1. Attempt to run the function
			res = func(self, *args, **kwargs)
			
			# 2. Check if the response indicates an expired token
			if res and res.status_code == 200:
				try:
					# Check the specific error code
					if res.json().get('errcode') == 10004:
						print("Token expired. Refreshing token and retrying...")
						
						# 3. Refresh the token (updates self.pbx_token)
						self.refresh_token()
						if self.pbx_refresh_token is None or self.pbx_refresh_token == "":
							self.get_token()
						# 4. Call the ORIGINAL function again
						# Because self.pbx_token is updated, the function will pick up the new token
						res = func(self, *args, **kwargs)
				except Exception as e:
					print(f"Error parsing JSON during retry check: {e}")

			# 5. Return the final result
			return res
		return wrapper

def integrate(url,token=None,req_data=None,query_params=None,method="GET"):
            headers=None
            url = url
            if token != None:

                headers = {                        
                    "Authorization": token  # Use 'Bearer' for OAuth tokens
                }
            
            data={}
            if req_data != None:
                for key,value in req_data.items():                           
                    data.update({key:value})
          
            if method=="GET":
                response = requests.get(url=url.rstrip(), json=data, headers=headers,params=query_params)
            if method=="POST":
                response = requests.post(url=url.rstrip(), json=data, headers=headers,params=query_params)


            return response