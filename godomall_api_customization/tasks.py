from __future__ import unicode_literals

import locale
import frappe
import random
import string
import requests
import godomall_api_customization.api
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def all():
	pass
	# print("Scheduler started")
	# letters = string.ascii_letters
	# note = " ".join(random.choice(letters) for i in range(20))
	# new_note = frappe.get_doc( {"doctype":"Note",
	# 						"title":note
	# 						}
	# )
	# new_note.insert()
	# frappe.db.commit()

def daily():
    today = datetime.today()
    yesterday = datetime.today() - timedelta(1)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    godomall_api_customization.api.get_godomall_goods_batch_registered(days=10)
    godomall_api_customization.api.get_godomall_goods_batch_modified(days=10)
    godomall_api_customization.api.get_godomall_order(start_date=start_date,end_date=end_date,date_type='order')

def hourly():
    batch_list = frappe.db.get_list('GodoMall Batch Job',filters=[ 
			['status','=', 'Ready']	
	] , pluck='name')
    
    for batch in batch_list:
        batch_doc = frappe.get_doc('GodoMall Batch Job',batch)
        order_list = frappe.db.get_list('Godomall Order', filters=[ 
			['order_date', 'between', [batch_doc.order_from_date, batch_doc.order_to_date]]
			,['order_status','Not in',['s1','r3']]
		] , pluck='name')
        result =""
        for order in order_list:
            print(order)
            result += godomall_api_customization.api.get_godomall_order(order_no=order) +"/n"
        batch_doc.status = 'Success'
        batch_doc.result = result
        batch_doc.save()

def weekly():
	godomall_api_customization.api.get_common_scm_code()

def monthly():
	pass

def cron():
    today = datetime.today()
    yesterday = datetime.today() - timedelta(1)
    tendays = datetime.today() - timedelta(10)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    tendays_ago= tendays.strftime('%Y-%m-%d')
    # godomall_api_customization.api.get_godomall_goods_batch_registered(days=2)
    # godomall_api_customization.api.get_godomall_goods_batch_modified(days=2)
    godomall_api_customization.api.get_godomall_order(start_date=start_date,end_date=end_date,date_type='order')
    order_list = frappe.db.get_list('Godomall Order', filters=[ 
			['order_date', 'between', [tendays_ago, end_date]]
			,['order_status','Not in',['s1','r3']]
		] , pluck='name')
    for order in order_list:
        # print(order)
        godomall_api_customization.api.get_godomall_order(order_no=order) 