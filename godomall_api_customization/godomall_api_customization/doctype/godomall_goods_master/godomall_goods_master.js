// Copyright (c) 2022, John Park and contributors
// For license information, please see license.txt

frappe.ui.form.on('Godomall Goods master', {
	refresh: function(frm) {
	    frm.add_custom_button(__('Updae current Goods'),function(){
            //frappe.msgprint(frm.doc.date);
            let goods_no = frm.selected_doc.name;
            


            frappe.call({
				method: "godomall_api_customization.api.get_godomall_goods?goods_no="+goods_no, //dotted path to server method
				kwargs: {
					'goods_no':goods_no
				},

				callback: function(r) {

					console.log(r)
					//cur_frm.exchange_rate = r.message.exchange_rate;
					if(r.message=='200') {
						// code snippet
						//frappe.msgprint();
						frappe.msgprint({
							title: __('Current Goods updated'),
							message: __('Current Goods updated')+r.message,
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
			
        }, __("Get Godomall order")    );

	    frm.add_custom_button(__('Create today order'),function(){
            //frappe.msgprint(frm.doc.date);
            var today = new Date();
			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_goods_batch_registered?days=30", //dotted path to server method
					

					callback: function(r) {

						console.log(r)
						if(r.message=='200') {
						// code snippet
						frappe.msgprint({
							title: __('From 30days to today Goods Created'),
							message: __('Godomall From 30days to today Goods Created'),
							indicator: 'orange'

						});
						frm.refresh();
					}



					}
				})
			
        }, __("Get Godomall order")    );




     }
});
