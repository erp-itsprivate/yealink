import frappe
from frappe.utils import get_url_to_form

def execute(filters=None):
    filters = frappe._dict(filters or {})
    #filters.meeting= frappe.get_doc('Meeting',{'closed':False}).meet_name
    columns = get_columns(filters)
    data = get_data(filters)
    #data=[]
    #columns =[]
    #data.append({"Shareholdernn":"ahmad","b_party":"ll"})
   #tr_date <= %(trx_date)s
    return columns, data

def get_conditions(filters):
    conditions = {}
    #current_day=frappe.utils.nowdate()
    #conditions="where cast(ts.creation as date) >= cast('"+current_day+"' as Date) and cast(ts.creation as date) <= cast('"+current_day+"' as Date)"
    #conditions="where 1=1 "
    conditions.update({'company':filters.get("company")})
    # if filters.get("status") is not None:
    #     if filters.get("status") != "All":
    #     #conditions["status"] = filters.status
    #     #return conditions
    #         conditions += "and  srv_status  =  %(status)s "
    # if filters.get("from_service_creation"):
    #     conditions += "and  cast(ts.creation as date)  >=  cast(%(from_service_creation)s as date) "
    
    # if filters.get("to_service_creation"):
    #     conditions += "and  cast(ts.creation as date)  <=  cast(%(to_service_creation)s as date) "
    return conditions
	

def get_columns(filters):
    columns = [
           {
            "label": "Company",
            "fieldtype": "link",
            "fieldname": "company",
            "options": "company",
            "width": 90,
        },
          {
            "label": "Call Type",
            "fieldtype": "data",
            "fieldname": "call_type",
            
            "width": 100,
        },
        {
            "label": "Call ID",
            "fieldtype": "data",
            "fieldname": "call_id",
         
            "width": 150,
        },
         {
            "label": "Call From Number",
            "fieldtype": "data",
            
            "fieldname": "call_from_number",
         
            "width":150,
        }, 
        {
            "label": "Call From Name",
            "fieldtype": "data",
            
            "fieldname": "call_from_name",
         
            "width":150,
        }, 
           {
            "label": "Doctype",
            "fieldtype": "data",
            "fieldname": "doc_type",
           
            "width": 150,
        },
   		{
            "label": "Lead",
            "fieldtype": "link",
            "fieldname": "lead",
            "options": "lead	",
            "width": 180,
        },



           {
            "label": "Datetime",
            "fieldtype": "Datetime",
           
            "fieldname": "datetime",
         
            "width":150,
        }, 
		 {
            "label": "Date",
            "fieldtype": "Date",
           
            "fieldname": "date",
         
            "width":130,
        },
		 {
            "label": "Department",
            "fieldtype": "data",
           
            "fieldname": "department",
         
            "width":150,
        },  
		 {
            "label": "Call Duration",
            "fieldtype": "Int",
           
            "fieldname": "call_duration",
         
            "width":120,
        }, 
		 {
            "label": "Talk Duration",
            "fieldtype": "Int",
           
            "fieldname": "talk_duration",
         
            "width":130,
        }, 
		 {
            "label": "Call To Number",
            "fieldtype": "data",
           
            "fieldname": "call_to_number",
         
            "width":180,
        },
		{
            "label": "Call To Name",
            "fieldtype": "data",
           
            "fieldname": "call_to_name",
         
            "width":180,
        },  
		{
            "label": "Disposition",
            "fieldtype": "data",
           
            "fieldname": "disposition",
         
            "width":140,
        },
        {
            "label": "Count",
            "fieldtype": "Int",
           
            "fieldname": "cnt",
         
            "width":50,
        },
        
         
    ]

    return columns

 

def get_data(filters):
		data = []
		conditions = get_conditions(filters)
		company=conditions.get('company')
		if company is not None and company != "" :
			
			values = {  'company':company}
		
			result=frappe.db.sql("""
						select
				cdrs.company as company,
				cdrs.call_type as call_type,
				cdrs.call_id as call_id,
				cdrs.call_from_number as call_from_number ,
				cdrs.call_from_name as call_from_name,
				cdrs.related_doctype as doc_type,
				cdrs.related_doctype_id as lead ,
				min(cdrs.cdr_time) as datetime  ,
				DATE(min(cdrs.cdr_time)) as date,
				GROUP_CONCAT(distinct department ORDER BY cdrs.cdr_time SEPARATOR '|') AS department,
				sum(cdrs.duration) as call_duration,
				sum(cdrs.talk_duration) as talk_duration,
				SUBSTRING_INDEX(GROUP_CONCAT(cdrs.call_to_number ORDER BY cdrs.cdr_time SEPARATOR '|'), '|', -1) as call_to_number,
				SUBSTRING_INDEX(GROUP_CONCAT(cdrs.call_to_name ORDER BY cdrs.cdr_time SEPARATOR '|'), '|', -1) as call_to_name,
				if(cdrs.call_type='Inbound' and length(SUBSTRING_INDEX(GROUP_CONCAT(cdrs.call_to_number ORDER BY cdrs.cdr_time SEPARATOR '|'), '|', -1))<>3, 'NO ANSWER',SUBSTRING_INDEX(GROUP_CONCAT(cdrs.disposition ORDER BY cdrs.cdr_time SEPARATOR '|'), '|', -1)) as disposition,
				1 as cnt
			from
				(
				select
					ivr.department as department,
					cdr.call_id, 
					cdr.call_to_number,
					cdr.call_to_name,
					cdr.call_from_number,
					cdr.call_from_name,
					cdr.call_type,
					cdr.company,
					STR_TO_DATE(cdr.cdr_time,'%%d/%%m/%%Y %%H:%%i:%%s') as cdr_time,
					cdr.disposition,
					cdr.duration,
					cdr.talk_duration,
					cdr.related_doctype,
					cdr.related_doctype_id
				from 
					`tabPBX CDRs` cdr left outer join 
					`tabPBX IVR` ivr
						on 
							cdr.company = ivr.company and
							cdr.call_to_number = ivr.path 
				where
					cdr.company = %(company)s
				) as cdrs
			group by
				cdrs.company,
				cdrs.call_type,
				cdrs.call_id,
				cdrs.call_from_number,
				cdrs.call_from_name,
				cdrs.related_doctype,
				cdrs.related_doctype_id
			 
			""",values=values, as_dict=1)



			for d in result:
				
				#row = {"shareholder": d['name'] ,"shareholdername":d['full_name'],"nationality":d["nationality"] ,"type":d["type"] ,
				#"tranasction": d["transaction_type"],"volume":d["volume"],"price":d["price"],"date":d["tr_date"]
				
				
				#}
				

 

				row = { "company":d.company,"call_type":d.call_type,"call_id":d.call_id ,"call_from_number":d.call_from_number,"call_from_name":d.call_from_name 
           			,"doc_type":d.doc_type,
					"lead":d.lead,"datetime":d.datetime,"date":d.date,"department":d.department,"call_duration":d.call_duration,"talk_duration":d.talk_duration,"call_to_number":d.call_to_number,"call_to_name":d.call_to_name,
					"disposition":d.disposition,"cnt":d.cnt
				}
				 
				data.append(row)

		return data
