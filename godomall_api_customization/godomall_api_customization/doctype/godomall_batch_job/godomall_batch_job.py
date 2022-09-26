# Copyright (c) 2022, John Park and contributors
# For license information, please see license.txt

import frappe
import godomall_api_customization.api

from frappe.model.document import Document

class GodoMallBatchJob(Document):
	def before_save(self):
		if self.status == 'Success':
			order_list = frappe.db.get_list('Godomall Order', filters=[ 
				['order_date', 'between', [self.order_from_date, self.order_to_date]]
				,['order_status','Not in',['s1','r3']]
			] , pluck='name')
			result =""
			for order in order_list:
				print(order)
				result += godomall_api_customization.api.get_godomall_order(order_no=order)
			self.result = result

			# godomall_api_customization.api.get_godomall_goods(page_no=str(idx),search_date_type="modDt")

