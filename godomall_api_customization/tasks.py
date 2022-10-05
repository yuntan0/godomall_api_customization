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
    today = datetime.today()

    end_date = today.strftime('%Y-%m-%d')  
    godomall_api_customization.api.get_godomall_order(start_date=end_date,end_date=end_date,date_type='order')
    batch_list = frappe.db.get_list('GodoMall Batch Job',filters=[ 
			['status','=', 'Ready']	
            ,['background_yn','=','Y']
	] , pluck='name')
    
    for batch in batch_list:
        batch_doc = frappe.get_doc('GodoMall Batch Job',batch)
        if batch_doc.order_status:

            start_date1 = batch_doc.order_from_date
            end_date1 = batch_doc.order_to_date
            date_type1 =  'order'
            order_status1 =batch_doc.order_status

            godomall_api_customization.api.get_godomall_order(start_date=start_date1,end_date=end_date1,date_type=date_type1,order_status=order_status1)
            frappe.db.sql("""
                        update frappedb.`tabGodomall Order` 
                        set batch_job_no = %s
                        where order_date between %s and %s and order_status =%s
                        and batch_job_no is null;
                        """,( batch_doc.name,start_date1,end_date1,order_status1) , as_dict=1)
        else:
            order_list = frappe.db.get_list('Godomall Order', filters=[ 
                ['order_date', 'between', [batch_doc.order_from_date, batch_doc.order_to_date]]
                ,['order_status','Not in',['s1','r3']]
                ,['background_yn','=','Y']
            ] , pluck='name')
            result =""
            for order in order_list:
                print(order)
                result += godomall_api_customization.api.get_godomall_order(order_no=order) +"\n"

                frappe.db.commit()
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