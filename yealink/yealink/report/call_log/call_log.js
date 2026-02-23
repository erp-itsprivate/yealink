// Copyright (c) 2026, ItsPrivate and contributors
// For license information, please see license.txt

frappe.query_reports["Call Log"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
			"default":frappe.defaults.get_default("company")
            
        },
	],
	"onload": function(report) {
        
        report.refresh();
        
       }
};

 
	
 