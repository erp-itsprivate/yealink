// Copyright (c) 2025, ItsPrivate and contributors
// For license information, please see license.txt

// frappe.ui.form.on("PBX Settings", {
// 	refresh(frm) {

// 	},
// });


// Copyright (c) 2025, ABC BIS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("PBX Settings", {
    load_buttons: function (frm) {
        frm.add_custom_button(__('Add PhoneBook'), function() {
            let d = new frappe.ui.Dialog({
                title: 'Enter PhoneBook Name',
                fields: [
                    {
                        label: 'PhoneBook',
                        fieldname: 'phonebook',
                        fieldtype: 'Data'
                    } 
                ],
                
                primary_action_label: 'Submit',
                primary_action(values) {
                    console.log(values);
                    frappe.call({             
                        doc: frm.doc,
                        method: "create_phonebooks",
                        args: {
                            phonebook_name: values.phonebook,
                        },
                        callback: function (r) {
                          console.log(r);
                          
                            frappe.msgprint(__(r.message.errmsg));
                           
                        },
                   
                    });
                    d.hide();
                }
            });
            
            d.show();
           
        },__('Tools'));
        frm.add_custom_button(__('Get PhoneBooks'), function() {
            frappe.call({             
                doc: frm.doc,
                method: "get_phonebooks",
                freeze: true,
                freeze_message: "Getting  Data...",
                 
                callback: function (r) {
                    frappe.msgprint(__(r.message.errmsg));
                  //frappe.msgprint("Data :"+ r.message);
                  frm.reload_doc();
                },
           
            });
        },__('Tools'));
        frm.add_custom_button(__('Sync Contact'), function() {
            frappe.call({             
                doc: frm.doc,
                method: "get_phonebooks_to_sync",
           
              freeze: true,
              freeze_message: "Sync Contact ...",
                callback: function (r) {
                    frappe.msgprint(  r.message);
                 
                },
           
            });
        },__('Tools'));
        frm.add_custom_button(__('Get CDRs'), function() {
            frappe.call({             
                doc: frm.doc,
                method: "get_cdrs_by_date",
           
              freeze: true,
              freeze_message: "Getting Data ...",
                callback: function (r) {
                    frappe.msgprint(  r.message);
                    frm.reload_doc();
                },
           
            });
        },__('Tools'));
    },
    refresh(frm){
        frm.trigger('load_buttons');
    
    },
    before_load(frm){
        frm.trigger('load_buttons');
    },
 
 });
