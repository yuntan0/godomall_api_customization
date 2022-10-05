# Copyright (c) 2022, John Park and contributors
# For license information, please see license.txt

import frappe
import godomall_api_customization.api

from frappe.model.document import Document

class GodoMallBatchJob(Document):
	def before_save(self):
		# if self.status == 'Success':
		# 	order_list = frappe.db.get_list('Godomall Order', filters=[ 
		# 		['order_date', 'between', [self.order_from_date, self.order_to_date]]
		# 		,['order_status','Not in',['s1','r3']]
		# 	] , pluck='name')
		# 	result =""
		# 	for order in order_list:
		# 		print(order)
		# 		result += godomall_api_customization.api.get_godomall_order(order_no=order)
		# 	self.result = result
		start_date1 = self.order_from_date
		end_date1 = self.order_to_date
		date_type1 =  'order'
		order_status1 =self.order_status

		# godomall_api_customization.api.api.get_godomall_order(start_date=start_date1,end_date=end_date1,date_type=date_type1,order_status=order_status1)
		# godomall_api_customization.api.get_godomall_goods(page_no=str(idx),search_date_type="modDt")
		# godomall_api_customization.api.api.get_godomall_order(order_no=order)
	def after_insert(self):
		start_date1 = self.order_from_date
		end_date1 = self.order_to_date
		date_type1 =  'order'
		order_status1 =self.order_status

		godomall_api_customization.api.get_godomall_order(start_date=start_date1,end_date=end_date1,date_type=date_type1,order_status=order_status1)
		frappe.db.sql("""
                    update frappedb.`tabGodomall Order` 
					set batch_job_no = %s
					where order_date between %s and %s and order_status =%s
					and batch_job_no is null;
                    """,( self.name,start_date1,end_date1,order_status1) , as_dict=1)

		order_list = frappe.db.get_list('Godomall Order'
			,filters= [
				['batch_job_no','=', self.name ]
				]
				, pluck='name')
		
		json_order_details={}
		json_order_details['order_no'] = order_list.order_no

		

		# batch_order = 
		

