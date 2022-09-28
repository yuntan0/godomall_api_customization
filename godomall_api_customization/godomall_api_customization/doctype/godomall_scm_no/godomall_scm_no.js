// Copyright (c) 2022, John Park and contributors
// For license information, please see license.txt

frappe.ui.form.on('Godomall SCM No', {
	refresh: function(frm) {
	    frm.add_custom_button(__('Create Supplier info'),function(){
            //frappe.msgprint(frm.doc.date);
            let goods_no = frm.selected_doc.name;
            


            frappe.call({
				method: "godomall_api_customization.api.get_common_scm_code", //dotted path to server method
				

				callback: function(r) {

					console.log(r)
					//cur_frm.exchange_rate = r.message.exchange_rate;
					if(r.message=='200') {
						// code snippet
						//frappe.msgprint();
						frappe.msgprint({
							title: __('Supplier updated'),
							message: __('Supplier updated')+r.message,
							indicator: 'orange'
						});
						//frm.selected_doc.exchange_rate = r.message.exchange_rate;
						// cur_frm.set_value('rate',r.message.rate);
						// cur_frm.set_value('date',r.message.date);
						// cur_frm.set_value('usd_rate',r.message.usd_rate);
						// cur_frm.set_value('scale',r.message.scale);

						return;
						//cur_frm.set_value('exchange_rate',r.message.exchange_rate);
						//cur_frm.exchange_rate = r.message.exchange_rate;

						}
				}
			})
			
        }, __("Get Supplier Info")    );

	



     }
});
