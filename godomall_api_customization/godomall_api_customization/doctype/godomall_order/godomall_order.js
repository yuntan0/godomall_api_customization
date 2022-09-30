// Copyright (c) 2022, John Park and contributors
// For license information, please see license.txt

frappe.ui.form.on('Godomall Order', {
	refresh: function(frm) {
	    frm.add_custom_button(__('Updae current order'),function(){
            //frappe.msgprint(frm.doc.date);
            let order_no = frm.selected_doc.name;
            



            frappe.call({
				method: "godomall_api_customization.api.get_godomall_order?order_no="+order_no, //dotted path to server method
				kwargs: {
					'order_no':order_no
				},

				callback: function(r) {

					console.log(r)
					//cur_frm.exchange_rate = r.message.exchange_rate;
					if(r.message) {
						// code snippet
						//frappe.msgprint();
						frappe.msgprint({
							title: __('Current Order updated'),
							message: __('Current Order updated')+r.message,
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
			}})
			
        }, __("Get Godomall order")    );

	    frm.add_custom_button(__('Create today order'),function(){
            //frappe.msgprint(frm.doc.date);
            var today = new Date();
			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=order&start_date="+today+"&end_date="+today, //dotted path to server method
					

					callback: function(r) {

						console.log(r)
						if(r.message) {
						// code snippet
						frappe.msgprint({
							title: __('Today Order Created'),
							message: __('Godomall Today Order Created'),
							indicator: 'orange'

						});
						frm.refresh();
					}



					}
				})
			
        }, __("Get Godomall order")    );

		frm.add_custom_button(__('Update modified order'),function(){
            //frappe.msgprint(frm.doc.date);
            var today = new Date();
			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=modify&start_date="+today+"&end_date="+today, //dotted path to server method
					kwargs: {
						'date_type':'modify',
						'start_date':today,
						'end_date':today
					},

					callback: function(r) {

						console.log(r)
						if(r.message) {
						// code snippet
						frappe.msgprint({
							title: __('Today Order Updated'),
							message: __('Godomall Today Modified Order Updated'),
							indicator: 'orange'

						});
					}



					}
				})
			
        }, __("Get Godomall order")    );

		frm.add_custom_button(__('Create D-1 order'),function(){
            var today = new Date();
		    var dday = new Date();
		    dday.setDate(dday.getDate() - 1);
		    
			var ddd = String(dday.getDate()).padStart(2, '0');
			var dmm = String(dday.getMonth() + 1).padStart(2, '0'); //January is 0!
			var dyyyy = dday.getFullYear();

			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;
			dday =  dyyyy+'-'+dmm+'-'+ddd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=order&start_date="+dday+"&end_date="+dday, //dotted path to server method
					kwargs: {
						'date_type':'order',
						'start_date':dday,
						'end_date':today
					},

					callback: function(r) {

						console.log(r)
						if(r.message) {
						// code snippet
						frappe.msgprint({
							title: __('D-1 Order Created'),
							message: __('Godomall D-1 Order Created'),
							indicator: 'orange'

						});
					}



					}
				})
			
        }, __("Get Godomall order")    );

		frm.add_custom_button(__('Update D-1 modified order'),function(){
            var today = new Date();
		    var dday = new Date();
		    dday.setDate(dday.getDate() - 1);
		    
			var ddd = String(dday.getDate()).padStart(2, '0');
			var dmm = String(dday.getMonth() + 1).padStart(2, '0'); //January is 0!
			var dyyyy = dday.getFullYear();

			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;
			dday =  dyyyy+'-'+dmm+'-'+ddd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=modify&start_date="+dday+"&end_date="+dday, //dotted path to server method
					kwargs: {
						'date_type':'modify',
						'start_date':dday,
						'end_date':today
					},

					callback: function(r) {

						console.log(r)
						// code snippet
						if(r.message) {
						frappe.msgprint({
							title: __('D-1 Order Created'),
							message: __('Godomall D-1 Modified Order Updated'),
							indicator: 'orange'

						});
					}



					}
				})
			
        }, __("Get Godomall order")    );

		frm.add_custom_button(__('Create D-2 order'),function(){
            var today = new Date();
		    var dday = new Date();
		    dday.setDate(dday.getDate() - 2);
		    
			var ddd = String(dday.getDate()).padStart(2, '0');
			var dmm = String(dday.getMonth() + 1).padStart(2, '0'); //January is 0!
			var dyyyy = dday.getFullYear();

			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;
			dday =  dyyyy+'-'+dmm+'-'+ddd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=order&start_date="+dday+"&end_date="+dday, //dotted path to server method
					kwargs: {
						'date_type':'order',
						'start_date':dday,
						'end_date':today
					},

					callback: function(r) {

						console.log(r)
						// code snippet
						if(r.message) {
						frappe.msgprint({
							title: __('D-2 Order Created'),
							message: __('Godomall @-2 Order Created'),
							indicator: 'orange'

						});
					}



					}
				})
			
        }, __("Get Godomall order")    );

		frm.add_custom_button(__('Update D-2 modified order'),function(){
            //frappe.msgprint(frm.doc.date);
            var today = new Date();
		    var dday = new Date();
		    dday.setDate(dday.getDate() - 2);
		    
			var ddd = String(dday.getDate()).padStart(2, '0');
			var dmm = String(dday.getMonth() + 1).padStart(2, '0'); //January is 0!
			var dyyyy = dday.getFullYear();

			var dd = String(today.getDate()).padStart(2, '0');
			var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
			var yyyy = today.getFullYear();

			today = yyyy+'-'+mm+'-'+dd;
			dday =  dyyyy+'-'+dmm+'-'+ddd;


				frappe.call({
					method: "godomall_api_customization.api.get_godomall_order?date_type=modify&start_date="+dday+"&end_date="+dday, //dotted path to server method
					callback: function(r) {

						console.log(r)
						// code snippet
						if(r.message) {
						frappe.msgprint({
							title: __('D-2 Order Created'),
							message: __('Godomall D-2 Modified Order Updated'),
							indicator: 'orange'

						});
					}



					}
				})
			
        }, __("Get Godomall order")    );



     }
});
