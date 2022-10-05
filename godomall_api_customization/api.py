from __future__ import unicode_literals
from ast import Pass
from urllib.request import urlopen
import frappe
import requests
import subprocess
import json
import os
from bs4 import BeautifulSoup
# from pyproj import Proj,transform
from datetime import datetime ,timedelta
import time
# bench execute godomall_api_customization.api.get_godomall_goods_batch
# bench execute godomall_api_customization.api.get_godomall_order  --kwargs "{'start_date':'2022-09-10','end_date':'2022-09-22','order_status':'r3','date_type':'modify'}"
#  bench execute godomall_api_customization.api.get_godomall_goods --kwargs "{'page_no':'1'}"
@frappe.whitelist()
def get_godomall_goods_batch_registered(**args):
    days = 0
    if args.get('days'):
        days = int(args.get('days'))
    else:
        days=600
    print('start')
    today = datetime.today()
    yesterday = datetime.today() - timedelta(days)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    idx =0
    max_page_cnt = 0
    while idx <= max_page_cnt:
        idx=idx+1
        max_page_cnt = get_godomall_goods(page_no=str(idx),search_date_type="regDt",start_date=start_date,end_date=end_date)
        print('start:'+str(idx)+"  Page:"+str(max_page_cnt))
    print('end')


@frappe.whitelist()
def get_godomall_goods_batch_modified(**args):
    days = 0
    if args.get('days'):
        days = int(args.get('days'))
    else:
        days=30
    print('start')
    today = datetime.today()
    yesterday = datetime.today() - timedelta(days)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    idx =0
    max_page_cnt = 0
    while idx <= max_page_cnt:
        idx=idx+1
        max_page_cnt = get_godomall_goods(page_no=str(idx),search_date_type="modDt",start_date=start_date,end_date=end_date)
        print('start:'+str(idx)+"  Page:"+str(max_page_cnt))
    print('end')
    
    
    # common_doc.common_doc.doctype.currency_exchange_rate.api.get_exchange_rate_all(exchange_date=today.strftime('%Y-%m-%d'))


@frappe.whitelist()
def get_godomall_goods(**kwargs):
    
    # if not search_date_type:
    #     search_date_type = "regDt"
    # else:
    #     search_date_type = "modDt"
    # today = datetime.today()
    # yesterday = datetime.today() - timedelta(30)
    # if not start_date:
    #     start_date = yesterday.strftime('%Y-%m-%d')
    # if not end_date:
    #     end_date = today.strftime('%Y-%m-%d')

    
    secrets_file = os.path.join(os.getcwd(), 'secrets.json')
    with open(secrets_file) as f:
        secrets = json.load(f)
    # print(secrets["godomall_partner_key"])
    # print(secrets["godomall_user_key"])
    # print(secrets["godomall_api_url"])
    url = []
    url.append(secrets["godomall_api_url"])
    url.append("/goods/Goods_Search.php")
    url.append("?partner_key=")
    url.append(secrets["godomall_partner_key"])
    url.append("&key=")
    url.append(secrets["godomall_user_key"])

    if kwargs.get('goods_no'):
        url.append('&goodsNo=')
        url.append(kwargs.get('goods_no'))
    if  kwargs.get('page_no'):
        url.append("&page=")
        url.append( kwargs.get('page_no'))
    
    if  kwargs.get('search_date_type'):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        search_date_type =  kwargs.get('search_date_type')
        url.append("&searchDateType=")
        url.append(search_date_type)
        url.append("&startDate=")
        url.append(start_date)
        url.append("&endDate=")
        url.append(end_date)
        url.append('&size=100')

    
    
    

    print("".join(url))

    # xmlObj = urlopen("".join(url))
    # bsObj = BeautifulSoup(xmlObj,"html.parser")
    # jsonObj = json.loads(str(bsObj))

    resp = requests.get("".join(url))
    if (resp.status_code == 200):
        # print(resp)
        xml_goods = resp.content
        soup = BeautifulSoup(xml_goods,"xml")
        max_page_cnt = 0

        try:
            code  = soup.find_all(name="code")
            max_page  = soup.find_all(name="max_page")
            print(code[0].text.strip())
            if code[0].text.strip() == "000":
                max_page_cnt = int(max_page[0].text.strip())
                # print(soup.find_all("return"))
                print(max_page_cnt)
                goods_list = soup.find_all("goods_data")
                for goods in goods_list:
                    curr_goods_no = goods.find("goodsNo").text.strip()
                    if frappe.db.exists('Godomall Goods master',goods.find("goodsNo").text.strip()):
                        goods_doc = frappe.get_doc('Godomall Goods master',goods.find("goodsNo").text.strip())
                        goods_doc.goods_nm_fl=goods.find('goodsNmFl').text.strip()
                        goods_doc.goods_nm=goods.find('goodsNm').text.strip()
                        if goods.find('goodsNmMain'):
                            goods_doc.goods_nm_main=goods.find('goodsNmMain').text.strip()
                        if goods.find('goodsNmList'):
                            goods_doc.goods_nm_list=goods.find('goodsNmList').text.strip()
                        if goods.find('goodsNmDetail'):
                            goods_doc.goods_nm_detail=goods.find('goodsNmDetail').text.strip()
                        if goods.find('goodsNmPartner'):
                            goods_doc.goods_nm_partner=goods.find('goodsNmPartner').text.strip()
                        if goods.find('purchaseGoodsNm'):
                            goods_doc.purchase_goods_nm=goods.find('purchaseGoodsNm').text.strip()
                        if goods.find('goodsDisplayFl'):
                            goods_doc.goods_display_fl=goods.find('goodsDisplayFl').text.strip()
                        if goods.find('goodsDisplayMobileFl'):
                            goods_doc.goods_display_mobile_fl=goods.find('goodsDisplayMobileFl').text.strip()
                        if goods.find('goodsSellFl'):
                            goods_doc.goods_sell_fl=goods.find('goodsSellFl').text.strip()
                        if goods.find('goodsSellMobileFl'):
                            goods_doc.goods_sell_mobile_fl=goods.find('goodsSellMobileFl').text.strip()
                        if goods.find('scmNo'):
                            goods_doc.scm_no=goods.find('scmNo').text.strip()
                        if goods.find('applyFl'):
                            goods_doc.apply_fl=goods.find('applyFl').text.strip()
                        if goods.find('applyType'):
                            goods_doc.apply_type=goods.find('applyType').text.strip()
                        if goods.find('applyMsg'):
                            goods_doc.apply_msg=goods.find('applyMsg').text.strip()
                        if goods.find('applyDt'):
                            goods_doc.apply_dt=goods.find('applyDt').text.strip()
                        if goods.find('commission'):
                            goods_doc.commission=goods.find('commission').text.strip()
                        if goods.find('goodsCd'):
                            goods_doc.goods_cd=goods.find('goodsCd').text.strip()
                        if goods.find('cateCd'):
                            goods_doc.cate_cd=goods.find('cateCd').text.strip()
                        if goods.find('allCateCd'):
                            goods_doc.all_cate_cd=goods.find('allCateCd').text.strip()
                        if goods.find('goodsSearchWord'):
                            goods_doc.goods_search_word=goods.find('goodsSearchWord').text.strip()
                        if goods.find('goodsOpenDt'):
                            goods_doc.goods_open_dt=goods.find('goodsOpenDt').text.strip()
                        if goods.find('goodsState'):
                            goods_doc.goods_state=goods.find('goodsState').text.strip()
                        if goods.find('goodsColor'):
                            goods_doc.goods_color=goods.find('goodsColor').text.strip()
                        if goods.find('brandCd'):
                            goods_doc.brand_cd=goods.find('brandCd').text.strip()
                        if goods.find('makerNm'):
                            goods_doc.maker_nm=goods.find('makerNm').text.strip()
                        if goods.find('originNm'):
                            goods_doc.origin_nm=goods.find('originNm').text.strip()
                        if goods.find('goodsModelNo'):
                            goods_doc.goods_model_no=goods.find('goodsModelNo').text.strip()
                        if goods.find('makeYmd'):
                            goods_doc.make_ymd=goods.find('makeYmd').text.strip()
                        if goods.find('launchYmd'):
                            goods_doc.launch_ymd=goods.find('launchYmd').text.strip()
                        if goods.find('effectiveStartYmd'):
                            goods_doc.effective_start_ymd=goods.find('effectiveStartYmd').text.strip()
                        if goods.find('effectiveEndYmd'):
                            goods_doc.effective_end_ymd=goods.find('effectiveEndYmd').text.strip()
                        if goods.find('goodsPermission'):
                            goods_doc.goods_permission=goods.find('goodsPermission').text.strip()
                        if goods.find('goodsPermissionGroup'):
                            goods_doc.goods_permission_group=goods.find('goodsPermissionGroup').text.strip()
                        if goods.find('onlyAdultFl'):
                            goods_doc.only_adult_fl=goods.find('onlyAdultFl').text.strip()
                        if goods.find('imageStorage'):
                            goods_doc.image_storage=goods.find('imageStorage').text.strip()
                        if goods.find('taxFreeFl'):
                            goods_doc.tax_free_fl=goods.find('taxFreeFl').text.strip()
                        if goods.find('taxPercent'):
                            goods_doc.tax_percent=goods.find('taxPercent').text.strip()
                        if goods.find('totalStock'):
                            goods_doc.goods_weight=goods.find('totalStock').text.strip()
                        if goods.find('totalStock'):
                            goods_doc.total_stock= goods.find('totalStock').text.strip()
                        if goods.find('stockFl'):
                            goods_doc.stock_fl=goods.find('stockFl').text.strip()
                        if goods.find('soldOutFl'):
                            goods_doc.sold_out_fl=goods.find('soldOutFl').text.strip()
                        if goods.find('salesUnit'):
                            goods_doc.sales_unit=goods.find('salesUnit').text.strip()
                        if goods.find('minOrderCnt'):
                            goods_doc.min_order_cnt=goods.find('minOrderCnt').text.strip()
                        if goods.find('maxOrderCnt'):
                            goods_doc.max_order_cnt=goods.find('maxOrderCnt').text.strip()
                        if goods.find('salesStartYmd'):
                            goods_doc.sales_start_ymd=goods.find('salesStartYmd').text.strip()
                        if goods.find('salesEndYmd'):
                            goods_doc.sales_end_ymd=goods.find('salesEndYmd').text.strip()
                        if goods.find('restockFl'):
                            goods_doc.restock_fl=goods.find('restockFl').text.strip()
                        if goods.find('mileageFl'):
                            goods_doc.mileage_fl=goods.find('mileageFl').text.strip()
                        if goods.find('mileageGoods'):
                            goods_doc.mileage_goods=goods.find('mileageGoods').text.strip()
                        if goods.find('mileageGoodsUnit'):
                            goods_doc.mileage_goods_unit=goods.find('mileageGoodsUnit').text.strip()
                        if goods.find('goodsDiscountFl'):
                            goods_doc.goods_discount_fl=goods.find('goodsDiscountFl').text.strip()
                        if goods.find('goodsDiscount'):
                            goods_doc.goods_discount=goods.find('goodsDiscount').text.strip()
                        if goods.find('goodsDiscountUnit'):
                            goods_doc.goods_discount_unit=goods.find('goodsDiscountUnit').text.strip()
                        if goods.find('payLimitFl'):
                            goods_doc.pay_limit_fl=goods.find('payLimitFl').text.strip()
                        if goods.find('payLimit'):
                            goods_doc.pay_limit=goods.find('payLimit').text.strip()
                        if goods.find('goodsPriceString'):
                            goods_doc.goods_price_string=goods.find('goodsPriceString').text.strip()
                        if goods.find('goodsPrice'):
                            goods_doc.goods_price=goods.find('goodsPrice').text.strip()
                        if goods.find('fixedPrice'):
                            goods_doc.fixed_price=goods.find('fixedPrice').text.strip()
                        if goods.find('costPrice'):
                            goods_doc.cost_price=goods.find('costPrice').text.strip()
                        if goods.find('optionFl'):
                            goods_doc.option_fl=goods.find('optionFl').text.strip()
                        if goods.find('optionDisplayFl'):
                            goods_doc.option_display_fl=goods.find('optionDisplayFl').text.strip()
                        if goods.find('optionName'):
                            goods_doc.option_name=goods.find('optionName').text.strip()
                        if goods.find('optionTextFl'):
                            goods_doc.option_text_fl=goods.find('optionTextFl').text.strip()
                        if goods.find('addGoodsFl'):
                            goods_doc.add_goods_fl=goods.find('addGoodsFl').text.strip()
                        if goods.find('shortDescription'):
                            goods_doc.short_description=goods.find('shortDescription').text.strip()
                        if goods.find('goodsDescription'):
                            goods_doc.goods_description=goods.find('goodsDescription').text.strip()
                        if goods.find('goodsDescriptionMobile'):
                            goods_doc.goods_description_mobile=goods.find('goodsDescriptionMobile').text.strip()
                        if goods.find('deliverySno'):    
                            goods_doc.delivery_sno=goods.find('deliverySno').text.strip()
                        if goods.find('relationFl'): 
                            goods_doc.relation_fl=goods.find('relationFl').text.strip()
                        if goods.find('relationSameFl'): 
                            goods_doc.relation_same_fl=goods.find('relationSameFl').text.strip()
                        if goods.find('relationGoodsNo'): 
                            goods_doc.relation_goods_no=goods.find('relationGoodsNo').text.strip()
                        if goods.find('goodsIconStartYmd'): 
                            goods_doc.goods_icon_start_ymd=goods.find('goodsIconStartYmd').text.strip()
                        if goods.find('goodsIconEndYmd'): 
                            goods_doc.goods_icon_end_ymd=goods.find('goodsIconEndYmd').text.strip()
                        if goods.find('goodsIconCdPeriod'): 
                            goods_doc.goods_icon_cd_period=goods.find('goodsIconCdPeriod').text.strip()
                        if goods.find('goodsIconCd'): 
                            goods_doc.goods_icon_cd=goods.find('goodsIconCd').text.strip()
                        if goods.find('imgDetailViewFl'): 
                            goods_doc.img_detail_view_fl=goods.find('imgDetailViewFl').text.strip()
                        if goods.find('externalVideoFl'): 
                            goods_doc.external_video_fl=goods.find('externalVideoFl').text.strip()
                        if goods.find('externalVideoUrl'): 
                            goods_doc.external_video_url=goods.find('externalVideoUrl').text.strip()
                        if goods.find('externalVideoWidth'): 
                            goods_doc.external_video_width=goods.find('externalVideoWidth').text.strip()
                        if goods.find('externalVideoHeight'): 
                            goods_doc.external_video_height=goods.find('externalVideoHeight').text.strip()
                        if goods.find('detailInfoDelivery'): 
                            goods_doc.detail_info_delivery=goods.find('detailInfoDelivery').text.strip()
                        if goods.find('detailInfoAS'): 
                            goods_doc.detail_info_as=goods.find('detailInfoAS').text.strip()
                        if goods.find('detailInfoRefund'): 
                            goods_doc.detail_info_refund=goods.find('detailInfoRefund').text.strip()
                        if goods.find('detailInfoExchange'): 
                            goods_doc.detail_info_exchange=goods.find('detailInfoExchange').text.strip()
                        if goods.find('memo'): 
                            goods_doc.memo=goods.find('memo').text.strip()
                        if goods.find('orderCnt'): 
                            goods_doc.order_cnt=goods.find('orderCnt').text.strip()
                        if goods.find('hitCnt'): 
                            goods_doc.hit_cnt=goods.find('hitCnt').text.strip()
                        if goods.find('reviewCnt'): 
                            goods_doc.review_cnt=goods.find('reviewCnt').text.strip()
                        if goods.find('excelFl'): 
                            goods_doc.excel_fl=goods.find('excelFl').text.strip()
                        if goods.find('regDt'): 
                            goods_doc.reg_dt=goods.find('regDt').text.strip()
                        if goods.find('modDt'): 
                            goods_doc.mod_dt=goods.find('modDt').text.strip()
                        if goods.find('seoTagFl'): 
                            goods_doc.seo_tag_fl=goods.find('seoTagFl').text.strip()

                        goods_options = goods.find_all('optionData')
                        json_options={}
                        for option in goods_options:
                            if frappe.db.exists('Godomall Goods Option',curr_goods_no + '-' +option.find('optionNo').text.strip()):
                                goods_doc.option_doc = frappe.get_doc('Godomall Goods Option',curr_goods_no + '-' +option.find('optionNo').text.strip())
                                if option.find('sno'):                  goods_doc.option_doc.sno = option.find('sno').text.strip()
                                if option.find('optionNo'):             goods_doc.option_doc.option_no = option.find('optionNo').text.strip()
                                if option.find('optionValue1'):         goods_doc.option_doc.option_value1= option.find('optionValue1').text.strip()
                                if option.find('optionValue2'):         goods_doc.option_doc.option_value2= option.find('optionValue2').text.strip()
                                if option.find('optionValue3'):         goods_doc.option_doc.option_value3= option.find('optionValue3').text.strip()
                                if option.find('optionValue4'):         goods_doc.option_doc.option_value4= option.find('optionValue4').text.strip()
                                if option.find('optionValue5'):         goods_doc.option_doc.option_value5= option.find('optionValue5').text.strip()
                                if option.find('optionPrice'):          goods_doc.option_doc.option_price= float(option.find('optionPrice').text.strip())
                                if option.find('optionCostPrice'):      goods_doc.option_doc.option_cost_price= float(option.find('optionCostPrice').text.strip())
                                if option.find('optionViewFl'):         goods_doc.option_doc.option_view_fl= option.find('optionViewFl').text.strip()
                                if option.find('optionSellFl'):         goods_doc.option_doc.option_sell_fl= option.find('optionSellFl').text.strip()
                                if option.find('optionSellCode'):       goods_doc.option_doc.option_sell_code= option.find('optionSellCode').text.strip()
                                if option.find('optionDeliveryFl'):     goods_doc.option_doc.option_delivery_fl= option.find('optionDeliveryFl').text.strip()
                                if option.find('optionDeliveryCode'):   goods_doc.option_doc.option_delivery_code= option.find('optionDeliveryCode').text.strip()
                                if option.find('optionCode'):           goods_doc.option_doc.option_code= option.find('optionCode').text.strip()
                                if option.find('stockCnt'):             goods_doc.option_doc.stock_cnt= int(option.find('stockCnt').text.strip())
                                if option.find('prevTotalStockChk'):    goods_doc.option_doc.prev_total_stock_chk= option.find('prevTotalStockChk').text.strip()
                                if option.find('sellStopFl'):           goods_doc.option_doc.sell_stop_fl= option.find('sellStopFl').text.strip()
                                if option.find('sellStopStock'):        goods_doc.option_doc.sell_stop_stock= option.find('sellStopStock').text.strip()
                                if option.find('confirmRequestStock'):  goods_doc.option_doc.confirm_request_stock= option.find('confirmRequestStock').text.strip()
                                if option.find('optionMemo'):           goods_doc.option_doc.option_memo= option.find('optionMemo').text.strip()
                                if option.find('deliverySmsSent'):      goods_doc.option_doc.delivery_sms_sent= option.find('deliverySmsSent').text.strip()
                                if option.find('optionImage'):          goods_doc.option_doc.option_image= option.find('optionImage').text.strip()
                                if option.find('regDt'):                goods_doc.option_doc.reg_dt= option.find('regDt').text.strip()
                                if option.find('modDt'):                goods_doc.option_doc.mod_dt= option.find('modDt').text.strip()
                            else:
                                json_options['goods_opt_no'] = curr_goods_no +'-'+ option.find('optionNo').text.strip()
                                if option.find('sno'):                  json_options['sno'] = option.find('sno').text.strip()
                                if option.find('optionNo'):             json_options['option_no'] = option.find('optionNo').text.strip()
                                if option.find('optionValue1'):         json_options['option_value1'] = option.find('optionValue1').text.strip()
                                if option.find('optionValue2'):         json_options['option_value2'] = option.find('optionValue2').text.strip()
                                if option.find('optionValue3'):         json_options['option_value3'] = option.find('optionValue3').text.strip()
                                if option.find('optionValue4'):         json_options['option_value4'] = option.find('optionValue4').text.strip()
                                if option.find('optionValue5'):         json_options['option_value5'] = option.find('optionValue5').text.strip()
                                if option.find('optionPrice'):          json_options['option_price'] = float(option.find('optionPrice').text.strip())
                                if option.find('optionCostPrice'):      json_options['option_cost_price'] = float(option.find('optionCostPrice').text.strip())
                                if option.find('optionViewFl'):         json_options['option_view_fl'] = option.find('optionViewFl').text.strip()
                                if option.find('optionSellFl'):         json_options['option_sell_fl'] = option.find('optionSellFl').text.strip()
                                if option.find('optionSellCode'):       json_options['option_sell_code'] = option.find('optionSellCode').text.strip()
                                if option.find('optionDeliveryFl'):     json_options['option_delivery_fl'] = option.find('optionDeliveryFl').text.strip()
                                if option.find('optionDeliveryCode'):   json_options['option_delivery_code'] = option.find('optionDeliveryCode').text.strip()
                                if option.find('optionCode'):           json_options['option_code'] = option.find('optionCode').text.strip()
                                if option.find('stockCnt'):             json_options['stock_cnt'] = int(option.find('stockCnt').text.strip())
                                if option.find('prevTotalStockChk'):    json_options['prev_total_stock_chk'] = option.find('prevTotalStockChk').text.strip()
                                if option.find('sellStopFl'):           json_options['sell_stop_fl'] = option.find('sellStopFl').text.strip()
                                if option.find('sellStopStock'):        json_options['sell_stop_stock'] = option.find('sellStopStock').text.strip()
                                if option.find('confirmRequestStock'):  json_options['confirm_request_stock'] = option.find('confirmRequestStock').text.strip()
                                if option.find('optionMemo'):           json_options['option_memo'] = option.find('optionMemo').text.strip()
                                if option.find('deliverySmsSent'):      json_options['delivery_sms_sent'] = option.find('deliverySmsSent').text.strip()
                                if option.find('optionImage'):          json_options['option_image'] = option.find('optionImage').text.strip()
                                if option.find('regDt'):                json_options['reg_dt'] = option.find('regDt').text.strip()
                                if option.find('modDt'):                json_options['mod_dt'] = option.find('modDt').text.strip()
                                goods_doc.append('goods_option',
                                    json_options
                                )

                        goods_doc.save(
                                        ignore_permissions=True, # ignore write permissions during insert
                                        ignore_version=True # do not create a version record
                                    )
                        frappe.db.commit()

                    else:

                        goods_doc = frappe.new_doc('Godomall Goods master')

                        goods_doc.goods_no=goods.find('goodsNo').text.strip()
                        goods_doc.goods_nm_fl=goods.find('goodsNmFl').text.strip()
                        goods_doc.goods_nm=goods.find('goodsNm').text.strip()
                        if goods.find('goodsNmMain'):
                            goods_doc.goods_nm_main=goods.find('goodsNmMain').text.strip()
                        goods_doc.goods_nm_list=goods.find('goodsNmList').text.strip()
                        goods_doc.goods_nm_detail=goods.find('goodsNmDetail').text.strip()
                        goods_doc.goods_nm_partner=goods.find('goodsNmPartner').text.strip()
                        goods_doc.purchase_goods_nm=goods.find('purchaseGoodsNm').text.strip()
                        goods_doc.goods_display_fl=goods.find('goodsDisplayFl').text.strip()
                        goods_doc.goods_display_mobile_fl=goods.find('goodsDisplayMobileFl').text.strip()
                        goods_doc.goods_sell_fl=goods.find('goodsSellFl').text.strip()
                        goods_doc.goods_sell_mobile_fl=goods.find('goodsSellMobileFl').text.strip()
                        goods_doc.scm_no=goods.find('scmNo').text.strip()
                        goods_doc.apply_fl=goods.find('applyFl').text.strip()
                        goods_doc.apply_type=goods.find('applyType').text.strip()
                        goods_doc.apply_msg=goods.find('applyMsg').text.strip()
                        goods_doc.apply_dt=goods.find('applyDt').text.strip()
                        goods_doc.commission=goods.find('commission').text.strip()
                        goods_doc.goods_cd=goods.find('goodsCd').text.strip()
                        if goods.find('cateCd'):
                            goods_doc.cate_cd=goods.find('cateCd').text.strip()
                        if goods.find('allCateCd'):
                            goods_doc.all_cate_cd=goods.find('allCateCd').text.strip()
                        if goods.find('goodsSearchWord'):
                            goods_doc.goods_search_word=goods.find('goodsSearchWord').text.strip()
                        if goods.find('goodsOpenDt'):
                            goods_doc.goods_open_dt=goods.find('goodsOpenDt').text.strip()
                        if goods.find('goodsState'):
                            goods_doc.goods_state=goods.find('goodsState').text.strip()
                        if goods.find('goodsColor'):
                            goods_doc.goods_color=goods.find('goodsColor').text.strip()
                        if goods.find('brandCd'):
                            goods_doc.brand_cd=goods.find('brandCd').text.strip()
                        if goods.find('makerNm'):
                            goods_doc.maker_nm=goods.find('makerNm').text.strip()
                        if goods.find('originNm'):
                            goods_doc.origin_nm=goods.find('originNm').text.strip()
                        if goods.find('goodsModelNo'):
                            goods_doc.goods_model_no=goods.find('goodsModelNo').text.strip()
                        if goods.find('makeYmd'):
                            goods_doc.make_ymd=goods.find('makeYmd').text.strip()
                        if goods.find('launchYmd'):
                            goods_doc.launch_ymd=goods.find('launchYmd').text.strip()
                        if goods.find('effectiveStartYmd'):
                            goods_doc.effective_start_ymd=goods.find('effectiveStartYmd').text.strip()
                        if goods.find('effectiveEndYmd'):
                            goods_doc.effective_end_ymd=goods.find('effectiveEndYmd').text.strip()
                        if goods.find('goodsPermission'):
                            goods_doc.goods_permission=goods.find('goodsPermission').text.strip()
                        if goods.find('goodsPermissionGroup'):
                            goods_doc.goods_permission_group=goods.find('goodsPermissionGroup').text.strip()
                        if goods.find('onlyAdultFl'):
                            goods_doc.only_adult_fl=goods.find('onlyAdultFl').text.strip()
                        if goods.find('imageStorage'):
                            goods_doc.image_storage=goods.find('imageStorage').text.strip()
                        if goods.find('taxFreeFl'):
                            goods_doc.tax_free_fl=goods.find('taxFreeFl').text.strip()
                        if goods.find('taxPercent'):
                            goods_doc.tax_percent=goods.find('taxPercent').text.strip()
                        if goods.find('totalStock'):
                            goods_doc.goods_weight=goods.find('totalStock').text.strip()
                        if goods.find('totalStock'):
                            goods_doc.total_stock= goods.find('totalStock').text.strip()
                        if goods.find('stockFl'):
                            goods_doc.stock_fl=goods.find('stockFl').text.strip()
                        if goods.find('soldOutFl'):
                            goods_doc.sold_out_fl=goods.find('soldOutFl').text.strip()
                        if goods.find('salesUnit'):
                            goods_doc.sales_unit=goods.find('salesUnit').text.strip()
                        if goods.find('minOrderCnt'):
                            goods_doc.min_order_cnt=goods.find('minOrderCnt').text.strip()
                        if goods.find('maxOrderCnt'):
                            goods_doc.max_order_cnt=goods.find('maxOrderCnt').text.strip()
                        if goods.find('salesStartYmd'):
                            goods_doc.sales_start_ymd=goods.find('salesStartYmd').text.strip()
                        if goods.find('salesEndYmd'):
                            goods_doc.sales_end_ymd=goods.find('salesEndYmd').text.strip()
                        if goods.find('restockFl'):
                            goods_doc.restock_fl=goods.find('restockFl').text.strip()
                        if goods.find('mileageFl'):
                            goods_doc.mileage_fl=goods.find('mileageFl').text.strip()
                        if goods.find('mileageGoods'):
                            goods_doc.mileage_goods=goods.find('mileageGoods').text.strip()
                        if goods.find('mileageGoodsUnit'):
                            goods_doc.mileage_goods_unit=goods.find('mileageGoodsUnit').text.strip()
                        if goods.find('goodsDiscountFl'):
                            goods_doc.goods_discount_fl=goods.find('goodsDiscountFl').text.strip()
                        if goods.find('goodsDiscount'):
                            goods_doc.goods_discount=goods.find('goodsDiscount').text.strip()
                        if goods.find('goodsDiscountUnit'):
                            goods_doc.goods_discount_unit=goods.find('goodsDiscountUnit').text.strip()
                        if goods.find('payLimitFl'):
                            goods_doc.pay_limit_fl=goods.find('payLimitFl').text.strip()
                        if goods.find('payLimit'):
                            goods_doc.pay_limit=goods.find('payLimit').text.strip()
                        if goods.find('goodsPriceString'):
                            goods_doc.goods_price_string=goods.find('goodsPriceString').text.strip()
                        if goods.find('goodsPrice'):
                            goods_doc.goods_price=goods.find('goodsPrice').text.strip()
                        if goods.find('fixedPrice'):
                            goods_doc.fixed_price=goods.find('fixedPrice').text.strip()
                        if goods.find('costPrice'):
                            goods_doc.cost_price=goods.find('costPrice').text.strip()
                        if goods.find('optionFl'):
                            goods_doc.option_fl=goods.find('optionFl').text.strip()
                        if goods.find('optionDisplayFl'):
                            goods_doc.option_display_fl=goods.find('optionDisplayFl').text.strip()
                        if goods.find('optionName'):
                            goods_doc.option_name=goods.find('optionName').text.strip()
                        if goods.find('optionTextFl'):
                            goods_doc.option_text_fl=goods.find('optionTextFl').text.strip()
                        if goods.find('addGoodsFl'):
                            goods_doc.add_goods_fl=goods.find('addGoodsFl').text.strip()
                        if goods.find('shortDescription'):
                            goods_doc.short_description=goods.find('shortDescription').text.strip()
                        if goods.find('goodsDescription'):
                            goods_doc.goods_description=goods.find('goodsDescription').text.strip()
                        if goods.find('goodsDescriptionMobile'):
                            goods_doc.goods_description_mobile=goods.find('goodsDescriptionMobile').text.strip()
                        if goods.find('deliverySno'):    
                            goods_doc.delivery_sno=goods.find('deliverySno').text.strip()
                        if goods.find('relationFl'): 
                            goods_doc.relation_fl=goods.find('relationFl').text.strip()
                        if goods.find('relationSameFl'): 
                            goods_doc.relation_same_fl=goods.find('relationSameFl').text.strip()
                        if goods.find('relationGoodsNo'): 
                            goods_doc.relation_goods_no=goods.find('relationGoodsNo').text.strip()
                        if goods.find('goodsIconStartYmd'): 
                            goods_doc.goods_icon_start_ymd=goods.find('goodsIconStartYmd').text.strip()
                        if goods.find('goodsIconEndYmd'): 
                            goods_doc.goods_icon_end_ymd=goods.find('goodsIconEndYmd').text.strip()
                        if goods.find('goodsIconCdPeriod'): 
                            goods_doc.goods_icon_cd_period=goods.find('goodsIconCdPeriod').text.strip()
                        if goods.find('goodsIconCd'): 
                            goods_doc.goods_icon_cd=goods.find('goodsIconCd').text.strip()
                        if goods.find('imgDetailViewFl'): 
                            goods_doc.img_detail_view_fl=goods.find('imgDetailViewFl').text.strip()
                        if goods.find('externalVideoFl'): 
                            goods_doc.external_video_fl=goods.find('externalVideoFl').text.strip()
                        if goods.find('externalVideoUrl'): 
                            goods_doc.external_video_url=goods.find('externalVideoUrl').text.strip()
                        if goods.find('externalVideoWidth'): 
                            goods_doc.external_video_width=goods.find('externalVideoWidth').text.strip()
                        if goods.find('externalVideoHeight'): 
                            goods_doc.external_video_height=goods.find('externalVideoHeight').text.strip()
                        if goods.find('detailInfoDelivery'): 
                            goods_doc.detail_info_delivery=goods.find('detailInfoDelivery').text.strip()
                        if goods.find('detailInfoAS'): 
                            goods_doc.detail_info_as=goods.find('detailInfoAS').text.strip()
                        if goods.find('detailInfoRefund'): 
                            goods_doc.detail_info_refund=goods.find('detailInfoRefund').text.strip()
                        if goods.find('detailInfoExchange'): 
                            goods_doc.detail_info_exchange=goods.find('detailInfoExchange').text.strip()
                        if goods.find('memo'): 
                            goods_doc.memo=goods.find('memo').text.strip()
                        if goods.find('orderCnt'): 
                            goods_doc.order_cnt=goods.find('orderCnt').text.strip()
                        if goods.find('hitCnt'): 
                            goods_doc.hit_cnt=goods.find('hitCnt').text.strip()
                        if goods.find('reviewCnt'): 
                            goods_doc.review_cnt=goods.find('reviewCnt').text.strip()
                        if goods.find('excelFl'): 
                            goods_doc.excel_fl=goods.find('excelFl').text.strip()
                        if goods.find('regDt'): 
                            goods_doc.reg_dt=goods.find('regDt').text.strip()
                        if goods.find('modDt'): 
                            goods_doc.mod_dt=goods.find('modDt').text.strip()
                        if goods.find('seoTagFl'): 
                            goods_doc.seo_tag_fl=goods.find('seoTagFl').text.strip()
                        
                        goods_options = goods.find_all('optionData')
                        json_options={}
                        for option in goods_options:
                            if frappe.db.exists('Godomall Goods Option',curr_goods_no + '-' +option.find('optionNo').text.strip()):
                                goods_doc.option_doc = frappe.get_doc('Godomall Goods Option',curr_goods_no + '-' +option.find('optionNo').text.strip())
                                if option.find('sno'):                  goods_doc.option_doc.sno = option.find('sno').text.strip()
                                if option.find('optionNo'):             goods_doc.option_doc.option_no = option.find('optionNo').text.strip()
                                if option.find('optionValue1'):         goods_doc.option_doc.option_value1= option.find('optionValue1').text.strip()
                                if option.find('optionValue2'):         goods_doc.option_doc.option_value2= option.find('optionValue2').text.strip()
                                if option.find('optionValue3'):         goods_doc.option_doc.option_value3= option.find('optionValue3').text.strip()
                                if option.find('optionValue4'):         goods_doc.option_doc.option_value4= option.find('optionValue4').text.strip()
                                if option.find('optionValue5'):         goods_doc.option_doc.option_value5= option.find('optionValue5').text.strip()
                                if option.find('optionPrice'):          goods_doc.option_doc.option_price= float(option.find('optionPrice').text.strip())
                                if option.find('optionCostPrice'):      goods_doc.option_doc.option_cost_price= float(option.find('optionCostPrice').text.strip())
                                if option.find('optionViewFl'):         goods_doc.option_doc.option_view_fl= option.find('optionViewFl').text.strip()
                                if option.find('optionSellFl'):         goods_doc.option_doc.option_sell_fl= option.find('optionSellFl').text.strip()
                                if option.find('optionSellCode'):       goods_doc.option_doc.option_sell_code= option.find('optionSellCode').text.strip()
                                if option.find('optionDeliveryFl'):     goods_doc.option_doc.option_delivery_fl= option.find('optionDeliveryFl').text.strip()
                                if option.find('optionDeliveryCode'):   goods_doc.option_doc.option_delivery_code= option.find('optionDeliveryCode').text.strip()
                                if option.find('optionCode'):           goods_doc.option_doc.option_code= option.find('optionCode').text.strip()
                                if option.find('stockCnt'):             goods_doc.option_doc.stock_cnt= int(option.find('stockCnt').text.strip())
                                if option.find('prevTotalStockChk'):    goods_doc.option_doc.prev_total_stock_chk= option.find('prevTotalStockChk').text.strip()
                                if option.find('sellStopFl'):           goods_doc.option_doc.sell_stop_fl= option.find('sellStopFl').text.strip()
                                if option.find('sellStopStock'):        goods_doc.option_doc.sell_stop_stock= option.find('sellStopStock').text.strip()
                                if option.find('confirmRequestStock'):  goods_doc.option_doc.confirm_request_stock= option.find('confirmRequestStock').text.strip()
                                if option.find('optionMemo'):           goods_doc.option_doc.option_memo= option.find('optionMemo').text.strip()
                                if option.find('deliverySmsSent'):      goods_doc.option_doc.delivery_sms_sent= option.find('deliverySmsSent').text.strip()
                                if option.find('optionImage'):          goods_doc.option_doc.option_image= option.find('optionImage').text.strip()
                                if option.find('regDt'):                goods_doc.option_doc.reg_dt= option.find('regDt').text.strip()
                                if option.find('modDt'):                goods_doc.option_doc.mod_dt= option.find('modDt').text.strip()
                            else:
                                json_options['goods_opt_no'] = curr_goods_no +'-'+ option.find('optionNo').text.strip()
                                if option.find('sno'):                  json_options['sno'] = option.find('sno').text.strip()
                                if option.find('optionNo'):             json_options['option_no'] = option.find('optionNo').text.strip()
                                if option.find('optionValue1'):         json_options['option_value1'] = option.find('optionValue1').text.strip()
                                if option.find('optionValue2'):         json_options['option_value2'] = option.find('optionValue2').text.strip()
                                if option.find('optionValue3'):         json_options['option_value3'] = option.find('optionValue3').text.strip()
                                if option.find('optionValue4'):         json_options['option_value4'] = option.find('optionValue4').text.strip()
                                if option.find('optionValue5'):         json_options['option_value5'] = option.find('optionValue5').text.strip()
                                if option.find('optionPrice'):          json_options['option_price'] = float(option.find('optionPrice').text.strip())
                                if option.find('optionCostPrice'):      json_options['option_cost_price'] = float(option.find('optionCostPrice').text.strip())
                                if option.find('optionViewFl'):         json_options['option_view_fl'] = option.find('optionViewFl').text.strip()
                                if option.find('optionSellFl'):         json_options['option_sell_fl'] = option.find('optionSellFl').text.strip()
                                if option.find('optionSellCode'):       json_options['option_sell_code'] = option.find('optionSellCode').text.strip()
                                if option.find('optionDeliveryFl'):     json_options['option_delivery_fl'] = option.find('optionDeliveryFl').text.strip()
                                if option.find('optionDeliveryCode'):   json_options['option_delivery_code'] = option.find('optionDeliveryCode').text.strip()
                                if option.find('optionCode'):           json_options['option_code'] = option.find('optionCode').text.strip()
                                if option.find('stockCnt'):             json_options['stock_cnt'] = int(option.find('stockCnt').text.strip())
                                if option.find('prevTotalStockChk'):    json_options['prev_total_stock_chk'] = option.find('prevTotalStockChk').text.strip()
                                if option.find('sellStopFl'):           json_options['sell_stop_fl'] = option.find('sellStopFl').text.strip()
                                if option.find('sellStopStock'):        json_options['sell_stop_stock'] = option.find('sellStopStock').text.strip()
                                if option.find('confirmRequestStock'):  json_options['confirm_request_stock'] = option.find('confirmRequestStock').text.strip()
                                if option.find('optionMemo'):           json_options['option_memo'] = option.find('optionMemo').text.strip()
                                if option.find('deliverySmsSent'):      json_options['delivery_sms_sent'] = option.find('deliverySmsSent').text.strip()
                                if option.find('optionImage'):          json_options['option_image'] = option.find('optionImage').text.strip()
                                if option.find('regDt'):                json_options['reg_dt'] = option.find('regDt').text.strip()
                                if option.find('modDt'):                json_options['mod_dt'] = option.find('modDt').text.strip()
                                goods_doc.append('goods_option',
                                    json_options
                                )

                        goods_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True,
                                        ignore_mandatory=True
                                        )
                        frappe.db.commit()

        except IndexError:
            print("Xml parsing Error")
        return max_page_cnt

@frappe.whitelist()
def get_godomall_order(**kwargs):
    order_no	 = kwargs.get('order_no')
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    date_type =  kwargs.get('date_type')
    order_status = kwargs.get('orderStatus')
    order_channel = kwargs.get('orderChannel')
    search_type = kwargs.get('searchType')
    batch_no = kwargs.get('batch_no')
    today = datetime.today()
    days_before = datetime.today() - timedelta(1)
    secrets_file = os.path.join(os.getcwd(), 'secrets.json')
    with open(secrets_file) as f:
        secrets = json.load(f)
    # print(secrets["godomall_partner_key"])
    # print(secrets["godomall_user_key"])
    # print(secrets["godomall_api_url"])
    url = []
    url.append(secrets["godomall_api_url"])
    url.append("/order/Order_Search.php")
    url.append("?partner_key=")
    url.append(secrets["godomall_partner_key"])
    url.append("&key=")
    url.append(secrets["godomall_user_key"])
    # if not date_type:
    #     date_type = "order"
    # else:
    #     date_type = "modify"
    # if not start_date:
    #     start_date = days_before.strftime('%Y-%m-%d')
    # if not end_date:
    #     end_date = today.strftime('%Y-%m-%d')
    if date_type:
        url.append("&dateType=")
        url.append(date_type)
    if start_date:
        url.append("&startDate=")
        url.append(start_date)
        url.append("&endDate=")
        url.append(end_date)
    
    if order_status:
        url.append('&orderStatus=')
        url.append(order_status)
    
    if order_no:
        url.append("&orderNo=")
        url.append(order_no)

    if order_channel:
        url.append('&orderChannel=')
        url.append(order_channel)

    if search_type:
        url.append('&searchType=')
        url.append(search_type)
    
    resp = requests.get("".join(url))
    print("".join(url))
    cur_order_no=""
    if (resp.status_code == 200):
        # print(resp)
        xml_orders = resp.content
        soup = BeautifulSoup(xml_orders,"xml")
        
        try:
            code  = soup.find_all(name="code")
            order_list = soup.find_all("order_data")
            for order in order_list:
                cur_order_no = order.find('orderNo').text.strip() 
                if frappe.db.exists('Godomall Order',order.find("orderNo").text.strip()) :
                    order_doc = frappe.get_doc('Godomall Order',order.find("orderNo").text.strip())
                    order_doc.order_date = "20"+ order.find('orderNo').text.strip()[0:6]
                    if order.find('memNo'):
                        order_doc.mem_no=order.find('memNo').text.strip()    #회원번호
                    if order.find('apiOrderGoodsNo'):
                        order_doc.api_order_goods_no=order.find('apiOrderGoodsNo').text.strip()    #외부채널품목고유번호
                    if order.find('orderStatus'):
                        order_doc.order_status=order.find('orderStatus').text.strip()    #주문상태 코드 코드표 참조
                    if order.find('orderIp'):
                        order_doc.order_ip=order.find('orderIp').text.strip()    #주문자IP
                    if order.find('orderChannelFl'):
                        order_doc.order_channel_fl=order.find('orderChannelFl').text.strip()    #주문채널
                    if order.find('orderTypeFl'):
                        order_doc.order_type_fl=order.find('orderTypeFl').text.strip()    #주문유형 코드표 참조
                    if order.find('orderEmail'):
                        order_doc.order_email=order.find('orderEmail').text.strip()    #이메일
                    if order.find('orderGoodsNm'):
                        order_doc.order_goods_nm=order.find('orderGoodsNm').text.strip()    #주문상품명
                    if order.find('orderGoodsCnt'):
                        order_doc.order_goods_cnt=order.find('orderGoodsCnt').text.strip()    #주문상품갯수
                    if order.find('settlePrice'):
                        order_doc.settle_price=order.find('settlePrice').text.strip()    #총 주문금액
                    if order.find('taxSupplyPrice'):
                        order_doc.tax_supply_price=order.find('taxSupplyPrice').text.strip()    #최초 총 과세금액
                    if order.find('taxVatPrice'):
                        order_doc.tax_vat_price=order.find('taxVatPrice').text.strip()    #최초 총 부가세 금액
                    if order.find('taxFreePrice'):
                        order_doc.tax_free_price=order.find('taxFreePrice').text.strip()    #최초 총 면세금액
                    if order.find('realTaxSupplyPrice'):
                        order_doc.real_tax_supply_price=order.find('realTaxSupplyPrice').text.strip()    #실제 총 과세금액(환불제외)
                    if order.find('realTaxVatPrice'):
                        order_doc.real_tax_vat_prcie=order.find('realTaxVatPrice').text.strip()    #실제 총 부가세(환불제외)
                    if order.find('realTaxFreePrice'):
                        order_doc.real_tax_free_price=order.find('realTaxFreePrice').text.strip()    #실제 총 면세금액(환불제외)
                    if order.find('useMileage'):
                        order_doc.use_mileage=order.find('useMileage').text.strip()    #주문시 사용한 마일리지
                    if order.find('useDeposit'):
                        order_doc.use_deposit=order.find('useDeposit').text.strip()    #주문시 사용한 예치금
                    if order.find('totalGoodsPrice'):
                        order_doc.total_goods_price=order.find('totalGoodsPrice').text.strip()    #총 상품 금액
                    if order.find('totalDeliveryCharge'):
                        order_doc.total_delivery_charge=order.find('totalDeliveryCharge').text.strip()    #총 배송비
                    if order.find('totalGoodsDcPrice'):
                        order_doc.total_goods_dc_price=order.find('totalGoodsDcPrice').text.strip()    #총 상품 할인 금액
                    if order.find('totalMemberDcPrice'):
                        order_doc.total_member_dc_price=order.find('totalMemberDcPrice').text.strip()    #총 회원 할인 금액
                    if order.find('totalMemberOverlapDcPrice'):
                        order_doc.total_member_overlap_price=order.find('totalMemberOverlapDcPrice').text.strip()    #총 그룹별 회원 중복할인 금액
                    if order.find('totalCouponGoodsDcPrice'):
                        order_doc.total_coupon_goods_dc_price=order.find('totalCouponGoodsDcPrice').text.strip()    #총 상품쿠폰 할인 금액
                    if order.find('totalCouponOrderDcPrice'):
                        order_doc.total_coupon_order_dc_price=order.find('totalCouponOrderDcPrice').text.strip()    #총 주문쿠폰 할인 금액
                    if order.find('totalCouponDeliveryDcPrice'):
                        order_doc.total_coupon_delivery_dc_price=order.find('totalCouponDeliveryDcPrice').text.strip()    #총 배송쿠폰 할인금액
                    if order.find('totalMileage'):
                        order_doc.total_mileage=order.find('totalMileage').text.strip()    #총 적립 마일리지
                    if order.find('totalGoodsMileage'):
                        order_doc.total_goods_mileage=order.find('totalGoodsMileage').text.strip()    #총 상품 상품적립 마일리지
                    if order.find('totalMemberMileage'):
                        order_doc.total_member_mileage=order.find('totalMemberMileage').text.strip()    #총 회원적립 마일리지
                    if order.find('totalCouponGoodsMileage'):
                        order_doc.total_coupon_goods_mileage=order.find('totalCouponGoodsMileage').text.strip()    #총 상품쿠폰 적립 마일리지
                    if order.find('totalCouponOrderMileage'):
                        order_doc.total_coupon_order_mileage=order.find('totalCouponOrderMileage').text.strip()    #총 주문쿠폰 적립 마일리지
                    if order.find('firstSaleFl'):
                        order_doc.first_sales_fl=order.find('firstSaleFl').text.strip()    #첫구매 여부 코드표 참조
                    if order.find('settleKind'):
                        order_doc.settle_kind=order.find('settleKind').text.strip()    #주문방법 코드표 참조
                    if order.find('multiShippingFl'):
                        order_doc.multi_shipping_fl=order.find('multiShippingFl').text.strip()    #복수배송지 사용여부 (y = 사용, n = 미사용)
                    if order.find('paymentDt'):
                        order_doc.payment_dt=order.find('paymentDt').text.strip()    #입금일자
                    if order.find('memId'):
                        order_doc.mem_id = order.find('memId').text.strip() 
                    if order.find('memGroupNm'):
                        order_doc.mem_group_nm = order.find('memGroupNm').text.strip() 
                    if order.find('orderGoodsStatusCnt'):
                        order_doc.order_goods_status_cnt = order.find('orderGoodsStatusCnt').text.strip() 
                    
                    order_delivery_list = order.find_all('orderDeliveryData')
                    for order_delivery in order_delivery_list:
                        if frappe.db.exists('Godomall Order Delivery Data',cur_order_no + '-' + order_delivery.find('sno').text.strip()):
                            order_doc.order_delivery_doc = frappe.get_doc('Godomall Order Delivery Data',cur_order_no + '-' + order_delivery.find('sno').text.strip())
                            if order_delivery.find('sno'):
                                order_doc.order_delivery_doc.order_sno = cur_order_no + '-' + order_delivery.find('sno').text.strip()
                                order_doc.order_delivery_doc.order_no = cur_order_no
                                order_doc.order_delivery_doc.sno =  order_delivery.find('sno').text.strip()
                            if order_delivery.find('scmNo'):
                                order_doc.order_delivery_doc.scm_no =  order_delivery.find('scmNo').text.strip()
                            if order_delivery.find('commission'):
                                order_doc.order_delivery_doc.commission =  float(order_delivery.find('commission').text.strip())
                            if order_delivery.find('scmAdjustNo'):
                                order_doc.order_delivery_doc.scm_adjust_no =  order_delivery.find('scmAdjustNo').text.strip()
                            if order_delivery.find('scmAdjustAfterNo'):
                                order_doc.order_delivery_doc.scm_adjust_after_no =  order_delivery.find('scmAdjustAfterNo').text.strip()
                            if order_delivery.find('deliveryCharge'):
                                order_doc.order_delivery_doc.delivery_charge =  float(order_delivery.find('deliveryCharge').text.strip())
                            if order_delivery.find('deliveryPolicyCharge'):
                                order_doc.order_delivery_doc.delivery_policy_charge =  float(order_delivery.find('deliveryPolicyCharge').text.strip())
                            if order_delivery.find('deliveryAreaCharge'):
                                order_doc.order_delivery_doc.delivery_area_charge =  float(order_delivery.find('deliveryAreaCharge').text.strip())
                            if order_delivery.find('divisionDeliveryUseDeposit'):
                                order_doc.order_delivery_doc.division_delivery_use_deposit =  float(order_delivery.find('divisionDeliveryUseDeposit').text.strip())
                            if order_delivery.find('divisionDeliveryUseMileage'):
                                order_doc.order_delivery_doc.division_delivery_use_mileage =  float(order_delivery.find('divisionDeliveryUseMileage').text.strip())
                            if order_delivery.find('divisionDeliveryCharge'):
                                order_doc.order_delivery_doc.division_delivery_charge =  float(order_delivery.find('divisionDeliveryCharge').text.strip())
                            if order_delivery.find('divisionMemberDeliveryDcPrice'):
                                order_doc.order_delivery_doc.division_member_melivery_dc_price =  float(order_delivery.find('divisionMemberDeliveryDcPrice').text.strip())
                            if order_delivery.find('deliveryInsuranceFee'):
                                order_doc.order_delivery_doc.delivery_insurance_fee =  float(order_delivery.find('deliveryInsuranceFee').text.strip())
                            if order_delivery.find('deliveryFixFl'):
                                order_doc.order_delivery_doc.delivery_fix_fl =  order_delivery.find('deliveryFixFl').text.strip()
                            if order_delivery.find('deliveryWeightInfo'):
                                order_doc.order_delivery_doc.delivery_weight_info =  order_delivery.find('deliveryWeightInfo').text.strip()
                            if order_delivery.find('overseasDeliveryPolicy'):
                                order_doc.order_delivery_doc.overseas_delivery_policy =  order_delivery.find('overseasDeliveryPolicy').text.strip()
                            if order_delivery.find('deliveryCollectFl'):
                                order_doc.order_delivery_doc.delivery_collect_fl =  order_delivery.find('deliveryCollectFl').text.strip()
                            if order_delivery.find('deliveryCollectPrice'):
                                order_doc.order_delivery_doc.delivery_collect_price =  float(order_delivery.find('deliveryCollectPrice').text.strip())
                            if order_delivery.find('deliveryWholeFreePrice'):
                                order_doc.order_delivery_doc.delivery_whole_free_price =  float(order_delivery.find('deliveryWholeFreePrice').text.strip())
                            if order_delivery.find('statisticsOrderFl'):
                                order_doc.order_delivery_doc.statistics_order_fl =  order_delivery.find('statisticsOrderFl').text.strip()
                        # order_doc.order_delivery_doc.save()
                        else:
                            json_delivery={"order_sno":""}
                            if order_delivery.find('sno'):
                                json_delivery["order_sno"] = cur_order_no + '-' + order_delivery.find('sno').text.strip()
                                json_delivery["order_no"] = cur_order_no
                                json_delivery["sno"] =  order_delivery.find('sno').text.strip()
                            if order_delivery.find('scmNo'):
                                json_delivery["scm_no"] =  order_delivery.find('scmNo').text.strip()
                            if order_delivery.find('commission'):
                                json_delivery["commission"] =  float(order_delivery.find('commission').text.strip())
                            if order_delivery.find('scmAdjustNo'):
                                json_delivery["scm_adjust_no"] =  order_delivery.find('scmAdjustNo').text.strip()
                            if order_delivery.find('scmAdjustAfterNo'):
                                json_delivery["scm_adjust_after_no"] =  order_delivery.find('scmAdjustAfterNo').text.strip()
                            if order_delivery.find('deliveryCharge'):
                                json_delivery["delivery_charge"] =  float(order_delivery.find('deliveryCharge').text.strip())
                            if order_delivery.find('deliveryPolicyCharge'):
                                json_delivery["delivery_policy_charge"] =  float(order_delivery.find('deliveryPolicyCharge').text.strip())
                            if order_delivery.find('deliveryAreaCharge'):
                                json_delivery["delivery_area_charge"] =  float(order_delivery.find('deliveryAreaCharge').text.strip())
                            if order_delivery.find('divisionDeliveryUseDeposit'):
                                json_delivery["division_delivery_use_deposit"] =  float(order_delivery.find('divisionDeliveryUseDeposit').text.strip())
                            if order_delivery.find('divisionDeliveryUseMileage'):
                                json_delivery["division_delivery_use_mileage"] =  float(order_delivery.find('divisionDeliveryUseMileage').text.strip())
                            if order_delivery.find('divisionDeliveryCharge'):
                                json_delivery["division_delivery_charge"] =  float(order_delivery.find('divisionDeliveryCharge').text.strip())
                            if order_delivery.find('divisionMemberDeliveryDcPrice'):
                                json_delivery["division_member_melivery_dc_price"] =  float(order_delivery.find('divisionMemberDeliveryDcPrice').text.strip())
                            if order_delivery.find('deliveryInsuranceFee'):
                                json_delivery["delivery_insurance_fee"] =  float(order_delivery.find('deliveryInsuranceFee').text.strip())
                            if order_delivery.find('deliveryFixFl'):
                                json_delivery["delivery_fix_fl"] =  order_delivery.find('deliveryFixFl').text.strip()
                            if order_delivery.find('deliveryWeightInfo'):
                                json_delivery["delivery_weight_info"] =  order_delivery.find('deliveryWeightInfo').text.strip()
                            if order_delivery.find('overseasDeliveryPolicy'):
                                json_delivery["overseas_delivery_policy"] =  order_delivery.find('overseasDeliveryPolicy').text.strip()
                            if order_delivery.find('deliveryCollectFl'):
                                json_delivery["delivery_collect_fl"] =  order_delivery.find('deliveryCollectFl').text.strip()
                            if order_delivery.find('deliveryCollectPrice'):
                                json_delivery["delivery_collect_price"] =  float(order_delivery.find('deliveryCollectPrice').text.strip())
                            if order_delivery.find('deliveryWholeFreePrice'):
                                json_delivery["delivery_whole_free_price"] =  float(order_delivery.find('deliveryWholeFreePrice').text.strip())
                            if order_delivery.find('statisticsOrderFl'):
                                json_delivery["statistics_order_fl"] =  order_delivery.find('statisticsOrderFl').text.strip()
                            # print(json.dumps(json_delivery))
                            order_doc.append('order_delivery_data',
                                json_delivery
                            )

                    order_info_data_list = order.find_all('orderInfoData')
                    order_seq = order.select('orderInfoData')
                    idx = 0
                    # print(order_seq[0]['idx'])
                    if frappe.db.exists('Customer',order.find('orderEmail').text.strip()):
                        cust_doc =frappe.get_doc('Customer',order.find('orderEmail').text.strip())
                        cust_doc.name = order.find('orderEmail').text.strip()
                        cust_doc.customer_name = order_info_data_list[0].find('orderName').text.strip()
                        if order.find('memGroupNm') and frappe.db.exists('Customer Group',order.find('memGroupNm').text.strip()):
                            
                            cust_doc.customer_group = order.find('memGroupNm').text.strip() 
                        else:
                            cust_doc.customer_group = '손님'
                        cust_doc.customer_type = 'Individual'
                        # print(cust_data.order_zonecode[0:2])
                        city_name =""
                        if order_info_data_list[0].find('orderZonecode').text.strip():
                            cust_doc.territory = get_territory_by_zipcode(zip_code=order_info_data_list[0].find('orderZonecode').text.strip())
                        cust_doc.so_required = 1
                        cust_doc.dn_required = 1
                        cust_doc.is_internal_customer = 0
                        cust_doc.default_currency = 'KRW'
                        cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                        cust_doc.save()
                    else:
                        cust_doc =frappe.new_doc('Customer')
                        cust_doc.name = order.find('orderEmail').text.strip()
                        cust_doc.customer_name = order_info_data_list[0].find('orderName').text.strip()
                        if order.find('memGroupNm'):
                            cust_doc.customer_group = order.find('memGroupNm').text.strip() 
                        else:
                            cust_doc.customer_group = '손님'
                        cust_doc.customer_type = 'Individual'
                        # print(cust_data.order_zonecode[0:2])
                        city_name =""
                        if order_info_data_list[0].find('orderZonecode').text.strip():
                            cust_doc.territory = get_territory_by_zipcode(zip_code=order_info_data_list[0].find('orderZonecode').text.strip())
                        cust_doc.so_required = 1
                        cust_doc.dn_required = 1
                        cust_doc.is_internal_customer = 0
                        cust_doc.default_currency = 'KRW'
                        cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                        cust_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True,
                            ignore_mandatory=True

                        )

                    for order_info_data in order_info_data_list:
                        if frappe.db.exists('Godomall Order Info Data',cur_order_no +'-'+ order_seq[idx]['idx']):
                            order_doc.order_info_doc = frappe.get_doc('Godomall Order Info Data',cur_order_no +'-'+ order_seq[idx]['idx'])
                            idx = idx+1
                            if order_info_data.find('orderName'):	order_doc.order_info_doc.order_name = order_info_data.find('orderName').text.strip()
                            if order_info_data.find('orderEmail'):	order_doc.order_info_doc.order_email= order_info_data.find('orderEmail').text.strip()
                            if order_info_data.find('orderCellPhone'):	order_doc.order_info_doc.order_cell_phone= order_info_data.find('orderCellPhone').text.strip()
                            if order_info_data.find('orderZipcode'):	order_doc.order_info_doc.order_zipcode= order_info_data.find('orderZipcode').text.strip()
                            if order_info_data.find('orderZonecode'):	order_doc.order_info_doc.order_zonecode= order_info_data.find('orderZonecode').text.strip()
                            if order_info_data.find('orderState'):	order_doc.order_info_doc.order_state= order_info_data.find('orderState').text.strip()
                            if order_info_data.find('orderCity'):	order_doc.order_info_doc.order_city= order_info_data.find('orderCity').text.strip()
                            if order_info_data.find('orderAddress'):	order_doc.order_info_doc.order_address= order_info_data.find('orderAddress').text.strip()
                            if order_info_data.find('orderAddressSub'):	order_doc.order_info_doc.order_address_sub= order_info_data.find('orderAddressSub').text.strip()
                            if order_info_data.find('receiverName'):	order_doc.order_info_doc.receiver_name= order_info_data.find('receiverName').text.strip()
                            if order_info_data.find('receiverCellPhone'):	order_doc.order_info_doc.receiver_cell_phone= order_info_data.find('receiverCellPhone').text.strip()
                            if order_info_data.find('receiverUseSafeNumberFl'):	order_doc.order_info_doc.receiver_use_safe_number_fl= order_info_data.find('receiverUseSafeNumberFl').text.strip()
                            if order_info_data.find('receiverSafeNumber'):	order_doc.order_info_doc.receiver_safe_number= order_info_data.find('receiverSafeNumber').text.strip()
                            if order_info_data.find('receiverSafeNumberDt'):	order_doc.order_info_doc.receiver_safe_number_dt= order_info_data.find('receiverSafeNumberDt').text.strip()
                            if order_info_data.find('receiverZipcode'):	order_doc.order_info_doc.receiver_zipcode= order_info_data.find('receiverZipcode').text.strip()
                            if order_info_data.find('receiverZonecode'):	order_doc.order_info_doc.receiver_zonecode= order_info_data.find('receiverZonecode').text.strip()
                            if order_info_data.find('receiverCountry'):	order_doc.order_info_doc.receiver_country= order_info_data.find('receiverCountry').text.strip()
                            if order_info_data.find('receiverState'):	order_doc.order_info_doc.receiver_state= order_info_data.find('receiverState').text.strip()
                            if order_info_data.find('receiverCity'):	order_doc.order_info_doc.receiver_city= order_info_data.find('receiverCity').text.strip()
                            if order_info_data.find('receiverAddress'):	order_doc.order_info_doc.receiver_address= order_info_data.find('receiverAddress').text.strip()
                            if order_info_data.find('receiverAddressSub'):	order_doc.order_info_doc.receiver_address_sub= order_info_data.find('receiverAddressSub').text.strip()
                            if order_info_data.find('deliveryVisit'):	order_doc.order_info_doc.delivery_visit= order_info_data.find('deliveryVisit').text.strip()
                            if order_info_data.find('orderinfoCd'):	order_doc.order_info_doc.orderinfo_cd= order_info_data.find('orderinfoCd').text.strip()
                            if order_info_data.find('gitMessage'):	order_doc.order_info_doc.gift_message= order_info_data.find('gitMessage').text.strip()
                        else:
                            json_order_info={"order_sub_no":""}
                            json_order_info["order_sub_no"] =  cur_order_no +'-'+ order_seq[idx]['idx']
                            idx = idx + 1
                            if order_info_data.find('orderName'):	json_order_info['order_name'] = order_info_data.find('orderName').text.strip()
                            if order_info_data.find('orderEmail'):	json_order_info['order_email'] = order_info_data.find('orderEmail').text.strip()
                            if order_info_data.find('orderCellPhone'):	json_order_info['order_cell_phone'] = order_info_data.find('orderCellPhone').text.strip()
                            if order_info_data.find('orderZipcode'):	json_order_info['order_zipcode'] = order_info_data.find('orderZipcode').text.strip()
                            if order_info_data.find('orderZonecode'):	json_order_info['order_zonecode'] = order_info_data.find('orderZonecode').text.strip()
                            if order_info_data.find('orderState'):	json_order_info['order_state'] = order_info_data.find('orderState').text.strip()
                            if order_info_data.find('orderCity'):	json_order_info['order_city'] = order_info_data.find('orderCity').text.strip()
                            if order_info_data.find('orderAddress'):	json_order_info['order_address'] = order_info_data.find('orderAddress').text.strip()
                            if order_info_data.find('orderAddressSub'):	json_order_info['order_address_sub'] = order_info_data.find('orderAddressSub').text.strip()
                            if order_info_data.find('receiverName'):	json_order_info['receiver_name'] = order_info_data.find('receiverName').text.strip()
                            if order_info_data.find('receiverCellPhone'):	json_order_info['receiver_cell_phone'] = order_info_data.find('receiverCellPhone').text.strip()
                            if order_info_data.find('receiverUseSafeNumberFl'):	json_order_info['receiver_use_safe_number_fl'] = order_info_data.find('receiverUseSafeNumberFl').text.strip()
                            if order_info_data.find('receiverSafeNumber'):	json_order_info['receiver_safe_number'] = order_info_data.find('receiverSafeNumber').text.strip()
                            if order_info_data.find('receiverSafeNumberDt'):	json_order_info['receiver_safe_number_dt'] = order_info_data.find('receiverSafeNumberDt').text.strip()
                            if order_info_data.find('receiverZipcode'):	json_order_info['receiver_zipcode'] = order_info_data.find('receiverZipcode').text.strip()
                            if order_info_data.find('receiverZonecode'):	json_order_info['receiver_zonecode'] = order_info_data.find('receiverZonecode').text.strip()
                            if order_info_data.find('receiverCountry'):	json_order_info['receiver_country'] = order_info_data.find('receiverCountry').text.strip()
                            if order_info_data.find('receiverState'):	json_order_info['receiver_state'] = order_info_data.find('receiverState').text.strip()
                            if order_info_data.find('receiverCity'):	json_order_info['receiver_city'] = order_info_data.find('receiverCity').text.strip()
                            if order_info_data.find('receiverAddress'):	json_order_info['receiver_address'] = order_info_data.find('receiverAddress').text.strip()
                            if order_info_data.find('receiverAddressSub'):	json_order_info['receiver_address_sub'] = order_info_data.find('receiverAddressSub').text.strip()
                            if order_info_data.find('deliveryVisit'):	json_order_info['delivery_visit'] = order_info_data.find('deliveryVisit').text.strip()
                            if order_info_data.find('orderinfoCd'):	json_order_info['orderinfo_cd'] = order_info_data.find('orderinfoCd').text.strip()
                            if order_info_data.find('gitMessage'):	json_order_info['gift_message'] = order_info_data.find('gitMessage').text.strip()
                            # print(json.dumps(json_order_info))
                            order_doc.append('order_info_data',
                                json_order_info
                            )

                        # order_info_data.save()
                    order_goods_data_list = order.find_all('orderGoodsData')
                    for order_goods_data in order_goods_data_list:
                        # print(order_goods_data.find('sno').text.strip() )
                        if frappe.db.exists('Godomall Order Goods Data',cur_order_no + '-' +order_goods_data.find('sno').text.strip()):
                            order_doc.order_goods_doc = frappe.get_doc('Godomall Order Goods Data',cur_order_no + '-' +order_goods_data.find('sno').text.strip())
                            if order_goods_data.find('sno'):	order_doc.order_goods_doc.sno= order_goods_data.find('sno').text.strip()
                            if order_goods_data.find('orderNo'):	order_doc.order_goods_doc.order_no= order_goods_data.find('orderNo').text.strip()
                            if order_goods_data.find('mailSno'):	order_doc.order_goods_doc.mall_sno= order_goods_data.find('mailSno').text.strip()
                            if order_goods_data.find('apiOrderGoodsNo'):	order_doc.order_goods_doc.api_order_goods_no= order_goods_data.find('apiOrderGoodsNo').text.strip()
                            if order_goods_data.find('orderCd'):	order_doc.order_goods_doc.order_cd= order_goods_data.find('orderCd').text.strip()
                            if order_goods_data.find('orderGroupCd'):	order_doc.order_goods_doc.order_group_cd= order_goods_data.find('orderGroupCd').text.strip()
                            if order_goods_data.find('eventCd'):	order_doc.order_goods_doc.event_sno= order_goods_data.find('eventCd').text.strip()
                            if order_goods_data.find('orderStatus'):	order_doc.order_goods_doc.order_status= order_goods_data.find('orderStatus').text.strip()
                            if order_goods_data.find('orderDeliverySno'):	order_doc.order_goods_doc.order_delivery_sno= order_goods_data.find('orderDeliverySno').text.strip()
                            if order_goods_data.find('invoiceCompanySno'):	order_doc.order_goods_doc.invoice_company_sno= order_goods_data.find('invoiceCompanySno').text.strip()
                            if order_goods_data.find('invoiceNo'):	order_doc.order_goods_doc.invoice_no= order_goods_data.find('invoiceNo').text.strip()
                            if order_goods_data.find('scmNo'):	order_doc.order_goods_doc.scm_no= order_goods_data.find('scmNo').text.strip()
                            if order_goods_data.find('purchaseNo'):	order_doc.order_goods_doc.purchase_no= order_goods_data.find('purchaseNo').text.strip()
                            if order_goods_data.find('commission'):	order_doc.order_goods_doc.commission= order_goods_data.find('commission').text.strip()
                            if order_goods_data.find('scmAdjustAfterNo'):	order_doc.order_goods_doc.scm_adjust_after_no= order_goods_data.find('scmAdjustAfterNo').text.strip()
                            if order_goods_data.find('goodsType'):	order_doc.order_goods_doc.goods_type= order_goods_data.find('goodsType').text.strip()
                            if order_goods_data.find('timeSaleFl'):	order_doc.order_goods_doc.time_sale_fl= order_goods_data.find('timeSaleFl').text.strip()
                            if order_goods_data.find('parentMustFl'):	order_doc.order_goods_doc.parent_must_fl= order_goods_data.find('parentMustFl').text.strip()
                            if order_goods_data.find('parentGoodsNo'):	order_doc.order_goods_doc.parent_goods_no= order_goods_data.find('parentGoodsNo').text.strip()
                            if order_goods_data.find('goodsNo'):	order_doc.order_goods_doc.goods_no= order_goods_data.find('goodsNo').text.strip()
                            if order_goods_data.find('listImageData'):	order_doc.order_goods_doc.list_image_data= order_goods_data.find('listImageData').text.strip()
                            if order_goods_data.find('goodsCd'):	order_doc.order_goods_doc.goods_cd= order_goods_data.find('goodsCd').text.strip()
                            if order_goods_data.find('goodsModelNo'):	order_doc.order_goods_doc.goods_model_no= order_goods_data.find('goodsModelNo').text.strip()
                            if order_goods_data.find('goodsNm'):	order_doc.order_goods_doc.goods_nm= order_goods_data.find('goodsNm').text.strip()
                            if order_goods_data.find('goodsNmStandard'):	order_doc.order_goods_doc.goods_nm_standard= order_goods_data.find('goodsNmStandard').text.strip()
                            if order_goods_data.find('goodsCnt'):	order_doc.order_goods_doc.goods_cnt= int(order_goods_data.find('goodsCnt').text.strip())
                            if order_goods_data.find('goodsPrice'):	order_doc.order_goods_doc.goods_price= float(order_goods_data.find('goodsPrice').text.strip())
                            if order_goods_data.find('divisionUseDeposit'):	order_doc.order_goods_doc.division_use_deposit= float(order_goods_data.find('divisionUseDeposit').text.strip())
                            if order_goods_data.find('divisionUseMileage'):	order_doc.order_goods_doc.division_use_mileage= float(order_goods_data.find('divisionUseMileage').text.strip())
                            if order_goods_data.find('divisionGoodsDeliveryUseDeposit'):	order_doc.order_goods_doc.division_goods_delivery_use_deposit= float(order_goods_data.find('divisionGoodsDeliveryUseDeposit').text.strip())
                            if order_goods_data.find('divisionGoodsDeliveryUseMileage'):	order_doc.order_goods_doc.division_goods_delivery_use_mileage= float(order_goods_data.find('divisionGoodsDeliveryUseMileage').text.strip())
                            if order_goods_data.find('divisionCouponOrderDcPrice'):	order_doc.order_goods_doc.division_coupon_order_dc_price= float(order_goods_data.find('divisionCouponOrderDcPrice').text.strip())
                            if order_goods_data.find('divisionCouponOrderMileage'):	order_doc.order_goods_doc.division_coupon_order_mileage= float(order_goods_data.find('divisionCouponOrderMileage').text.strip())
                            if order_goods_data.find('addGoodsPrice'):	order_doc.order_goods_doc.add_goods_price= float(order_goods_data.find('addGoodsPrice').text.strip())
                            if order_goods_data.find('optionPrice'):	order_doc.order_goods_doc.option_price= float(order_goods_data.find('optionPrice').text.strip())
                            if order_goods_data.find('optionCostPrice'):	order_doc.order_goods_doc.option_cost_price= float(order_goods_data.find('optionCostPrice').text.strip())
                            if order_goods_data.find('optionTextPrice'):	order_doc.order_goods_doc.option_text_price= float(order_goods_data.find('optionTextPrice').text.strip())
                            if order_goods_data.find('fixedPrice'):	order_doc.order_goods_doc.fixed_price= float(order_goods_data.find('fixedPrice').text.strip())
                            if order_goods_data.find('costPrice'):	order_doc.order_goods_doc.cost_price=float( order_goods_data.find('costPrice').text.strip())
                            if order_goods_data.find('goodsDcPrice'):	order_doc.order_goods_doc.goods_dc_price= float(order_goods_data.find('goodsDcPrice').text.strip())
                            if order_goods_data.find('memberDcPrice'):	order_doc.order_goods_doc.member_dc_price= float(order_goods_data.find('memberDcPrice').text.strip())
                            if order_goods_data.find('memberOverlapDcPrice'):	order_doc.order_goods_doc.member_overlap_dc_price= float(order_goods_data.find('memberOverlapDcPrice').text.strip())
                            if order_goods_data.find('couponGoodsDcPrice'):	order_doc.order_goods_doc.coupon_goods_dc_price= float(order_goods_data.find('couponGoodsDcPrice').text.strip())
                            if order_goods_data.find('timeSalePrice'):	order_doc.order_goods_doc.time_sale_price= float(order_goods_data.find('timeSalePrice').text.strip())
                            if order_goods_data.find('brandBankSalePrice'):	order_doc.order_goods_doc.brand_bank_sale_price= float(order_goods_data.find('brandBankSalePrice').text.strip())
                            if order_goods_data.find('myappDcPrice'):	order_doc.order_goods_doc.myapp_dc_price= float(order_goods_data.find('myappDcPrice').text.strip())
                            if order_goods_data.find('goodsDeliveryCollectPrice'):	order_doc.order_goods_doc.goods_delivery_collect_price= float(order_goods_data.find('goodsDeliveryCollectPrice').text.strip())
                            if order_goods_data.find('goodsMileage'):	order_doc.order_goods_doc.goods_mileage= float(order_goods_data.find('goodsMileage').text.strip())
                            if order_goods_data.find('memberMileage'):	order_doc.order_goods_doc.member_mileage= float(order_goods_data.find('memberMileage').text.strip())
                            if order_goods_data.find('couponGoodsMileage'):	order_doc.order_goods_doc.coupon_goods_mileage= float(order_goods_data.find('couponGoodsMileage').text.strip())
                            if order_goods_data.find('goodsDeliveryCollectPrice'):	order_doc.order_goods_doc.goods_delivery_collect_fl= order_goods_data.find('goodsDeliveryCollectPrice').text.strip()
                            if order_goods_data.find('minusDepositFl'):	order_doc.order_goods_doc.minus_deposit_fl= order_goods_data.find('minusDepositFl').text.strip()
                            if order_goods_data.find('minusRestoreDepositFl'):	order_doc.order_goods_doc.minus_restore_deposit_fl= order_goods_data.find('minusRestoreDepositFl').text.strip()
                            if order_goods_data.find('minusMileageFl'):	order_doc.order_goods_doc.minus_mileage_fl= order_goods_data.find('minusMileageFl').text.strip()
                            if order_goods_data.find('minusRestoreMileageFl'):	order_doc.order_goods_doc.minus_restore_mileage_fl= order_goods_data.find('minusRestoreMileageFl').text.strip()
                            if order_goods_data.find('plusMileageFl'):	order_doc.order_goods_doc.plus_mileage_fl= order_goods_data.find('plusMileageFl').text.strip()
                            if order_goods_data.find('plusRestoreMileageFl'):	order_doc.order_goods_doc.plus_restore_mileage_fl= order_goods_data.find('plusRestoreMileageFl').text.strip()
                            if order_goods_data.find('minusStockFl'):	order_doc.order_goods_doc.minus_stock_fl= order_goods_data.find('minusStockFl').text.strip()
                            if order_goods_data.find('minusRestoreStockFl'):	order_doc.order_goods_doc.minus_restore_stock_fl= order_goods_data.find('minusRestoreStockFl').text.strip()
                            if order_goods_data.find('optionSno'):	order_doc.order_goods_doc.option_sno= order_goods_data.find('optionSno').text.strip()
                            if order_goods_data.find('optionInfo'):	order_doc.order_goods_doc.option_info= order_goods_data.find('optionInfo').text.strip()
                            if order_goods_data.find('optionTextInfo'):	order_doc.order_goods_doc.option_text_info= order_goods_data.find('optionTextInfo').text.strip()
                            if order_goods_data.find('cateAllCd'):	order_doc.order_goods_doc.cate_all_cd= order_goods_data.find('cateAllCd').text.strip()
                            if order_goods_data.find('hscode'):	order_doc.order_goods_doc.hscode= order_goods_data.find('hscode').text.strip()
                            if order_goods_data.find('cancelDt'):	order_doc.order_goods_doc.cancel_dt= order_goods_data.find('cancelDt').text.strip()
                            if order_goods_data.find('paymentDt'):	order_doc.order_goods_doc.payment_dt= order_goods_data.find('paymentDt').text.strip()
                            if order_goods_data.find('invoiceDt'):	order_doc.order_goods_doc.invoice_dt= order_goods_data.find('invoiceDt').text.strip()
                            if order_goods_data.find('deliveryDt'):	order_doc.order_goods_doc.delivery_dt= order_goods_data.find('deliveryDt').text.strip()
                            if order_goods_data.find('deliveryCompleteDt'):	order_doc.order_goods_doc.delivery_complete_dt= order_goods_data.find('deliveryCompleteDt').text.strip()
                            if order_goods_data.find('finishDt'):	order_doc.order_goods_doc.finish_dt= order_goods_data.find('finishDt').text.strip()
                            if order_goods_data.find('mileageGiveDt'):	order_doc.order_goods_doc.mileage_give_dt= order_goods_data.find('mileageGiveDt').text.strip()
                            if order_goods_data.find('checkoutData'):	order_doc.order_goods_doc.checkout_data= order_goods_data.find('checkoutData').text.strip()
                            if order_goods_data.find('statisticsOrderFl'):	order_doc.order_goods_doc.statistics_order_fl= order_goods_data.find('statisticsOrderFl').text.strip()
                            if order_goods_data.find('statisticsGoodsFl'):	order_doc.order_goods_doc.statistics_goods_fl= order_goods_data.find('statisticsGoodsFl').text.strip()
                            if order_goods_data.find('deliveryMethodFl'):	order_doc.order_goods_doc.delivery_method_fl= order_goods_data.find('deliveryMethodFl').text.strip()
                            if order_goods_data.find('enuri'):	order_doc.order_goods_doc.enuri= order_goods_data.find('enuri').text.strip()
                            if order_goods_data.find('goodsDiscountInfo'):	order_doc.order_goods_doc.goods_discount_info= order_goods_data.find('goodsDiscountInfo').text.strip()
                            if order_goods_data.find('goodsMileageAddInfo'):	order_doc.order_goods_doc.goods_mileage_add_info= order_goods_data.find('goodsMileageAddInfo').text.strip()
                            if order_goods_data.find('inflow'):	order_doc.order_goods_doc.inflow= order_goods_data.find('inflow').text.strip()
                            if order_goods_data.find('linkMainTheme'):	order_doc.order_goods_doc.link_main_theme= order_goods_data.find('linkMainTheme').text.strip()
                            if order_goods_data.find('visitAddress'):	order_doc.order_goods_doc.visit_address= order_goods_data.find('visitAddress').text.strip()
                            if order_goods_data.find('dpxDeliveryType'):	order_doc.order_goods_doc.dpx_delivery_type= order_goods_data.find('dpxDeliveryType').text.strip()
                            if order_goods_data.find('dawnInfoType'):	order_doc.order_goods_doc.dawn_info_type= order_goods_data.find('dawnInfoType').text.strip()
                            if order_goods_data.find('dawnInfoMemo'):	order_doc.order_goods_doc.dawn_info_memo= order_goods_data.find('dawnInfoMemo').text.strip()
                            if order_goods_data.find('dawnInfoAlram'):	order_doc.order_goods_doc.dawn_info_alram= order_goods_data.find('dawnInfoAlram').text.strip()
                            if order_goods_data.find('requestBagFl'):	order_doc.order_goods_doc.request_bag_fl= order_goods_data.find('requestBagFl').text.strip()
                            if order_goods_data.find('goodsVolume'):	order_doc.order_goods_doc.goods_volume= order_goods_data.find('goodsVolume').text.strip()
                            if order_goods_data.find('couponMileageFl'):	order_doc.order_goods_doc.coupon_mileage_fl= order_goods_data.find('couponMileageFl').text.strip()
                            if order_goods_data.find('deliveryBundleFl'):	order_doc.order_goods_doc.delivery_bundle_fl= order_goods_data.find('deliveryBundleFl').text.strip()
                            if order_goods_data.find('deliveryDueDate'):	order_doc.order_goods_doc.delivery_due_date= order_goods_data.find('deliveryDueDate').text.strip()
                            if order_goods_data.find('easypayScmReceiptFl'):	order_doc.order_goods_doc.easypay_scm_receipt_fl= order_goods_data.find('easypayScmReceiptFl').text.strip()
                        else:
                            json_order_goods={"order_sno":""}
                            if order_goods_data.find('sno'):	
                                json_order_goods['order_sno'] = order_goods_data.find('orderNo').text.strip() + '-' +order_goods_data.find('sno').text.strip()
                                json_order_goods['sno'] = order_goods_data.find('sno').text.strip()
                            if order_goods_data.find('orderNo'):	json_order_goods['order_no'] = order_goods_data.find('orderNo').text.strip()
                            if order_goods_data.find('mailSno'):	json_order_goods['mall_sno'] = order_goods_data.find('mailSno').text.strip()
                            if order_goods_data.find('apiOrderGoodsNo'):	json_order_goods['api_order_goods_no'] = order_goods_data.find('apiOrderGoodsNo').text.strip()
                            if order_goods_data.find('orderCd'):	json_order_goods['order_cd'] = order_goods_data.find('orderCd').text.strip()
                            if order_goods_data.find('orderGroupCd'):	json_order_goods['order_group_cd'] = order_goods_data.find('orderGroupCd').text.strip()
                            if order_goods_data.find('eventCd'):	json_order_goods['event_sno'] = order_goods_data.find('eventCd').text.strip()
                            if order_goods_data.find('orderStatus'):	json_order_goods['order_status'] = order_goods_data.find('orderStatus').text.strip()
                            if order_goods_data.find('orderDeliverySno'):	json_order_goods['order_delivery_sno'] = order_goods_data.find('orderDeliverySno').text.strip()
                            if order_goods_data.find('invoiceCompanySno'):	json_order_goods['invoice_company_sno'] = order_goods_data.find('invoiceCompanySno').text.strip()
                            if order_goods_data.find('invoiceNo'):	json_order_goods['invoice_no'] = order_goods_data.find('invoiceNo').text.strip()
                            if order_goods_data.find('scmNo'):	json_order_goods['scm_no'] = order_goods_data.find('scmNo').text.strip()
                            if order_goods_data.find('purchaseNo'):	json_order_goods['purchase_no'] = order_goods_data.find('purchaseNo').text.strip()
                            if order_goods_data.find('commission'):	json_order_goods['commission'] = float(order_goods_data.find('commission').text.strip())
                            if order_goods_data.find('scmAdjustAfterNo'):	json_order_goods['scm_adjust_after_no'] = order_goods_data.find('scmAdjustAfterNo').text.strip()
                            if order_goods_data.find('goodsType'):	json_order_goods['goods_type'] = order_goods_data.find('goodsType').text.strip()
                            if order_goods_data.find('timeSaleFl'):	json_order_goods['time_sale_fl'] = order_goods_data.find('timeSaleFl').text.strip()
                            if order_goods_data.find('parentMustFl'):	json_order_goods['parent_must_fl'] = order_goods_data.find('parentMustFl').text.strip()
                            if order_goods_data.find('parentGoodsNo'):	json_order_goods['parent_goods_no'] = order_goods_data.find('parentGoodsNo').text.strip()
                            if order_goods_data.find('goodsNo'):	json_order_goods['goods_no'] = order_goods_data.find('goodsNo').text.strip()
                            if order_goods_data.find('listImageData'):	json_order_goods['list_image_data'] = order_goods_data.find('listImageData').text.strip()
                            if order_goods_data.find('goodsCd'):	json_order_goods['goods_cd'] = order_goods_data.find('goodsCd').text.strip()
                            if order_goods_data.find('goodsModelNo'):	json_order_goods['goods_model_no'] = order_goods_data.find('goodsModelNo').text.strip()
                            if order_goods_data.find('goodsNm'):	json_order_goods['goods_nm'] = order_goods_data.find('goodsNm').text.strip()
                            if order_goods_data.find('goodsNmStandard'):	json_order_goods['goods_nm_standard'] = order_goods_data.find('goodsNmStandard').text.strip()
                            if order_goods_data.find('goodsCnt'):	json_order_goods['goods_cnt'] = int(order_goods_data.find('goodsCnt').text.strip())
                            if order_goods_data.find('goodsPrice'):	json_order_goods['goods_price'] = float(order_goods_data.find('goodsPrice').text.strip())
                            if order_goods_data.find('divisionUseDeposit'):	json_order_goods['division_use_deposit'] = float(order_goods_data.find('divisionUseDeposit').text.strip())
                            if order_goods_data.find('divisionUseMileage'):	json_order_goods['division_use_mileage'] = float(order_goods_data.find('divisionUseMileage').text.strip())
                            if order_goods_data.find('divisionGoodsDeliveryUseDeposit'):	json_order_goods['division_goods_delivery_use_deposit'] = float(order_goods_data.find('divisionGoodsDeliveryUseDeposit').text.strip())
                            if order_goods_data.find('divisionGoodsDeliveryUseMileage'):	json_order_goods['division_goods_delivery_use_mileage'] = float(order_goods_data.find('divisionGoodsDeliveryUseMileage').text.strip())
                            if order_goods_data.find('divisionCouponOrderDcPrice'):	json_order_goods['division_coupon_order_dc_price'] = float(order_goods_data.find('divisionCouponOrderDcPrice').text.strip())
                            if order_goods_data.find('divisionCouponOrderMileage'):	json_order_goods['division_coupon_order_mileage'] = float(order_goods_data.find('divisionCouponOrderMileage').text.strip())
                            if order_goods_data.find('addGoodsPrice'):	json_order_goods['add_goods_price'] = float(order_goods_data.find('addGoodsPrice').text.strip())
                            if order_goods_data.find('optionPrice'):	json_order_goods['option_price'] = float(order_goods_data.find('optionPrice').text.strip())
                            if order_goods_data.find('optionCostPrice'):	json_order_goods['option_cost_price'] = float(order_goods_data.find('optionCostPrice').text.strip())
                            if order_goods_data.find('optionTextPrice'):	json_order_goods['option_text_price'] = float(order_goods_data.find('optionTextPrice').text.strip())
                            if order_goods_data.find('fixedPrice'):	json_order_goods['fixed_price'] = float(order_goods_data.find('fixedPrice').text.strip())
                            if order_goods_data.find('costPrice'):	json_order_goods['cost_price'] = float(order_goods_data.find('costPrice').text.strip())
                            if order_goods_data.find('goodsDcPrice'):	json_order_goods['goods_dc_price'] = float(order_goods_data.find('goodsDcPrice').text.strip())
                            if order_goods_data.find('memberDcPrice'):	json_order_goods['member_dc_price'] = float(order_goods_data.find('memberDcPrice').text.strip())
                            if order_goods_data.find('memberOverlapDcPrice'):	json_order_goods['member_overlap_dc_price'] = float(order_goods_data.find('memberOverlapDcPrice').text.strip())
                            if order_goods_data.find('couponGoodsDcPrice'):	json_order_goods['coupon_goods_dc_price'] = float(order_goods_data.find('couponGoodsDcPrice').text.strip())
                            if order_goods_data.find('timeSalePrice'):	json_order_goods['time_sale_price'] = float(order_goods_data.find('timeSalePrice').text.strip())
                            if order_goods_data.find('brandBankSalePrice'):	json_order_goods['brand_bank_sale_price'] = float(order_goods_data.find('brandBankSalePrice').text.strip())
                            if order_goods_data.find('myappDcPrice'):	json_order_goods['myapp_dc_price'] = float(order_goods_data.find('myappDcPrice').text.strip())
                            if order_goods_data.find('goodsDeliveryCollectPrice'):	json_order_goods['goods_delivery_collect_price'] = float(order_goods_data.find('goodsDeliveryCollectPrice').text.strip())
                            if order_goods_data.find('goodsMileage'):	json_order_goods['goods_mileage'] = float(order_goods_data.find('goodsMileage').text.strip())
                            if order_goods_data.find('memberMileage'):	json_order_goods['member_mileage'] = float(order_goods_data.find('memberMileage').text.strip())
                            if order_goods_data.find('couponGoodsMileage'):	json_order_goods['coupon_goods_mileage'] = float(order_goods_data.find('couponGoodsMileage').text.strip())
                            if order_goods_data.find('goods_delivery_collect_fl'):	json_order_goods['goods_delivery_collect_fl'] = order_goods_data.find('goods_delivery_collect_fl').text.strip()
                            if order_goods_data.find('minusDepositFl'):	json_order_goods['minus_deposit_fl'] = order_goods_data.find('minusDepositFl').text.strip()
                            if order_goods_data.find('minusRestoreDepositFl'):	json_order_goods['minus_restore_deposit_fl'] = order_goods_data.find('minusRestoreDepositFl').text.strip()
                            if order_goods_data.find('minusMileageFl'):	json_order_goods['minus_mileage_fl'] = order_goods_data.find('minusMileageFl').text.strip()
                            if order_goods_data.find('minusRestoreMileageFl'):	json_order_goods['minus_restore_mileage_fl'] = order_goods_data.find('minusRestoreMileageFl').text.strip()
                            if order_goods_data.find('plusMileageFl'):	json_order_goods['plus_mileage_fl'] = order_goods_data.find('plusMileageFl').text.strip()
                            if order_goods_data.find('plusRestoreMileageFl'):	json_order_goods['plus_restore_mileage_fl'] = order_goods_data.find('plusRestoreMileageFl').text.strip()
                            if order_goods_data.find('minusStockFl'):	json_order_goods['minus_stock_fl'] = order_goods_data.find('minusStockFl').text.strip()
                            if order_goods_data.find('minusRestoreStockFl'):	json_order_goods['minus_restore_stock_fl'] = order_goods_data.find('minusRestoreStockFl').text.strip()
                            if order_goods_data.find('optionSno'):	json_order_goods['option_sno'] = order_goods_data.find('optionSno').text.strip()
                            if order_goods_data.find('optionInfo'):	json_order_goods['option_info'] = order_goods_data.find('optionInfo').text.strip()
                            if order_goods_data.find('optionTextInfo'):	json_order_goods['option_text_info'] = order_goods_data.find('optionTextInfo').text.strip()
                            if order_goods_data.find('cateAllCd'):	json_order_goods['cate_all_cd'] = order_goods_data.find('cateAllCd').text.strip()
                            if order_goods_data.find('hscode'):	json_order_goods['hscode'] = order_goods_data.find('hscode').text.strip()
                            if order_goods_data.find('cancelDt'):	json_order_goods['cancel_dt'] = order_goods_data.find('cancelDt').text.strip()
                            if order_goods_data.find('paymentDt'):	json_order_goods['payment_dt'] = order_goods_data.find('paymentDt').text.strip()
                            if order_goods_data.find('invoiceDt'):	json_order_goods['invoice_dt'] = order_goods_data.find('invoiceDt').text.strip()
                            if order_goods_data.find('deliveryDt'):	json_order_goods['delivery_dt'] = order_goods_data.find('deliveryDt').text.strip()
                            if order_goods_data.find('deliveryCompleteDt'):	json_order_goods['delivery_complete_dt'] = order_goods_data.find('deliveryCompleteDt').text.strip()
                            if order_goods_data.find('finishDt'):	json_order_goods['finish_dt'] = order_goods_data.find('finishDt').text.strip()
                            if order_goods_data.find('mileageGiveDt'):	json_order_goods['mileage_give_dt'] = order_goods_data.find('mileageGiveDt').text.strip()
                            if order_goods_data.find('checkoutData'):	json_order_goods['checkout_data'] = order_goods_data.find('checkoutData').text.strip()
                            if order_goods_data.find('statisticsOrderFl'):	json_order_goods['statistics_order_fl'] = order_goods_data.find('statisticsOrderFl').text.strip()
                            if order_goods_data.find('statisticsGoodsFl'):	json_order_goods['statistics_goods_fl'] = order_goods_data.find('statisticsGoodsFl').text.strip()
                            if order_goods_data.find('deliveryMethodFl'):	json_order_goods['delivery_method_fl'] = order_goods_data.find('deliveryMethodFl').text.strip()
                            if order_goods_data.find('enuri'):	json_order_goods['enuri'] = order_goods_data.find('enuri').text.strip()
                            if order_goods_data.find('goodsDiscountInfo'):	json_order_goods['goods_discount_info'] = order_goods_data.find('goodsDiscountInfo').text.strip()
                            if order_goods_data.find('goodsMileageAddInfo'):	json_order_goods['goods_mileage_add_info'] = order_goods_data.find('goodsMileageAddInfo').text.strip()
                            if order_goods_data.find('inflow'):	json_order_goods['inflow'] = order_goods_data.find('inflow').text.strip()
                            if order_goods_data.find('linkMainTheme'):	json_order_goods['link_main_theme'] = order_goods_data.find('linkMainTheme').text.strip()
                            if order_goods_data.find('visitAddress'):	json_order_goods['visit_address'] = order_goods_data.find('visitAddress').text.strip()
                            if order_goods_data.find('dpxDeliveryType'):	json_order_goods['dpx_delivery_type'] = order_goods_data.find('dpxDeliveryType').text.strip()
                            if order_goods_data.find('dawnInfoType'):	json_order_goods['dawn_info_type'] = order_goods_data.find('dawnInfoType').text.strip()
                            if order_goods_data.find('dawnInfoMemo'):	json_order_goods['dawn_info_memo'] = order_goods_data.find('dawnInfoMemo').text.strip()
                            if order_goods_data.find('dawnInfoAlram'):	json_order_goods['dawn_info_alram'] = order_goods_data.find('dawnInfoAlram').text.strip()
                            if order_goods_data.find('requestBagFl'):	json_order_goods['request_bag_fl'] = order_goods_data.find('requestBagFl').text.strip()
                            if order_goods_data.find('goodsVolume'):	json_order_goods['goods_volume'] = order_goods_data.find('goodsVolume').text.strip()
                            if order_goods_data.find('couponMileageFl'):	json_order_goods['coupon_mileage_fl'] = order_goods_data.find('couponMileageFl').text.strip()
                            if order_goods_data.find('deliveryBundleFl'):	json_order_goods['delivery_bundle_fl'] = order_goods_data.find('deliveryBundleFl').text.strip()
                            if order_goods_data.find('deliveryDueDate'):	json_order_goods['delivery_due_date'] = order_goods_data.find('deliveryDueDate').text.strip()
                            if order_goods_data.find('easypayScmReceiptFl'):	json_order_goods['easypay_scm_receipt_fl'] = order_goods_data.find('easypayScmReceiptFl').text.strip()
                                
                                

                            order_doc.append('order_goods_data',
                                json_order_goods
                            )

                            
                            
                            # order_goods_data.save()
                            order_claim_data = order_goods_data.find_all('claimData')
                            order_claim_seq = order_goods_data.select('claimData')
                            # print(order_claim_data)
                            idx = 0
                            for order_claim in order_claim_data:
                                # print(order_claim)
                                if frappe.db.exists('Godomall Claim Data',cur_order_no + '-' +order_goods_data.find('sno').text.strip()):
                                    order_doc.order_claim_doc = frappe.get_doc('Godomall Claim Data',cur_order_no + '-' +order_goods_data.find('sno').text.strip())
                                    
                                    if order_claim.find('beforeStatus'):                order_doc.order_claim_doc.before_status = order_claim.find('beforeStatus').text.strip()
                                    if order_claim.find('handleMode'):                  order_doc.order_claim_doc.handle_mode = order_claim.find('handleMode').text.strip()
                                    if order_claim.find('handleCompleteFl'):            order_doc.order_claim_doc.handle_complete_fl = order_claim.find('handleCompleteFl').text.strip()
                                    if order_claim.find('handleReason'):                order_doc.order_claim_doc.handle_reason = order_claim.find('handleReason').text.strip()
                                    if order_claim.find('handleDetailReason'):          order_doc.order_claim_doc.handle_detail_reason = order_claim.find('handleDetailReason').text.strip()
                                    if order_claim.find('handleDetailReasonShowFl'):    order_doc.order_claim_doc.fandle_detail_reason_show_fl = order_claim.find('handleDetailReasonShowFl').text.strip()
                                    if order_claim.find('handleDt'):                    order_doc.order_claim_doc.handle_dt = order_claim.find('handleDt').text.strip()
                                    if order_claim.find('refundPrice'):                 order_doc.order_claim_doc.refund_price = float(order_claim.find('refundPrice').text.strip())
                                    if order_claim.find('refundUseDeposit'):            order_doc.order_claim_doc.refund_use_deposit = float(order_claim.find('refundUseDeposit').text.strip())
                                    if order_claim.find('refundUseMileage'):            order_doc.order_claim_doc.refund_use_mileage = float(order_claim.find('refundUseMileage').text.strip())
                                    if order_claim.find('refundDeliveryUseDeposit'):    order_doc.order_claim_doc.refund_delivery_use_deposit = float(order_claim.find('refundDeliveryUseDeposit').text.strip())
                                    if order_claim.find('refundDeliveryUseMileage'):    order_doc.order_claim_doc.refund_delivery_use_mileage = float(order_claim.find('refundDeliveryUseMileage').text.strip())
                                    if order_claim.find('refundDeliveryCharge'):        order_doc.order_claim_doc.refund_delivery_charge = float(order_claim.find('refundDeliveryCharge').text.strip())
                                    if order_claim.find('refundDeliveryInsuranceFee'):  order_doc.order_claim_doc.refund_delivery_insurance_fee = float(order_claim.find('refundDeliveryInsuranceFee').text.strip())
                                    if order_claim.find('refundDeliveryCoupon'):        order_doc.order_claim_doc.refund_delivery_coupon = float(order_claim.find('refundDeliveryCoupon').text.strip())
                                    if order_claim.find('refundCharge'):                order_doc.order_claim_doc.refund_charge = float(order_claim.find('refundCharge').text.strip())
                                    if order_claim.find('refundUseDepositCommission'):  order_doc.order_claim_doc.refund_use_deposit_commission = float(order_claim.find('refundUseDepositCommission').text.strip())
                                    if order_claim.find('refundUseMileageCommission'):  order_doc.order_claim_doc.refund_use_mileage_commission = float(order_claim.find('refundUseMileageCommission').text.strip())
                                    if order_claim.find('handleGroupCd'):               order_doc.order_claim_doc.handle_group_cd = order_claim.find('handleGroupCd').text.strip()
                                    if order_claim.find('regDt'):                       order_doc.order_claim_doc.reg_dt = order_claim.find('regDt').text.strip()
                                    idx = idx +1
                                else:
                                    json_order_claim={"order_sno":""}
                                    json_order_claim['order_sno'] =                cur_order_no +'-'+order_goods_data.find('sno').text.strip()
                                    if order_claim.find('beforeStatus'):                json_order_claim['before_status'] = order_claim.find('beforeStatus').text.strip()
                                    if order_claim.find('handleMode'):                  json_order_claim['handle_mode'] = order_claim.find('handleMode').text.strip()
                                    if order_claim.find('handleCompleteFl'):            json_order_claim['handle_complete_fl'] = order_claim.find('handleCompleteFl').text.strip()
                                    if order_claim.find('handleReason'):                json_order_claim['handle_reason'] = order_claim.find('handleReason').text.strip()
                                    if order_claim.find('handleDetailReason'):          json_order_claim['handle_detail_reason'] = order_claim.find('handleDetailReason').text.strip()
                                    if order_claim.find('handleDetailReasonShowFl'):    json_order_claim['fandle_detail_reason_show_fl'] = order_claim.find('handleDetailReasonShowFl').text.strip()
                                    if order_claim.find('handleDt'):                    json_order_claim['handle_dt'] = order_claim.find('handleDt').text.strip()
                                    if order_claim.find('refundPrice'):                 json_order_claim['refund_price'] = float(order_claim.find('refundPrice').text.strip())
                                    if order_claim.find('refundUseDeposit'):            json_order_claim['refund_use_deposit'] = float(order_claim.find('refundUseDeposit').text.strip())
                                    if order_claim.find('refundUseMileage'):            json_order_claim['refund_use_mileage'] = float(order_claim.find('refundUseMileage').text.strip())
                                    if order_claim.find('refundDeliveryUseDeposit'):    json_order_claim['refund_delivery_use_deposit'] = float(order_claim.find('refundDeliveryUseDeposit').text.strip())
                                    if order_claim.find('refundDeliveryUseMileage'):    json_order_claim['refund_delivery_use_mileage'] = float(order_claim.find('refundDeliveryUseMileage').text.strip())
                                    if order_claim.find('refundDeliveryCharge'):        json_order_claim['refund_delivery_charge'] = float(order_claim.find('refundDeliveryCharge').text.strip())
                                    if order_claim.find('refundDeliveryInsuranceFee'):  json_order_claim['refund_delivery_insurance_fee'] = float(order_claim.find('refundDeliveryInsuranceFee').text.strip())
                                    if order_claim.find('refundDeliveryCoupon'):        json_order_claim['refund_delivery_coupon'] = float(order_claim.find('refundDeliveryCoupon').text.strip())
                                    if order_claim.find('refundCharge'):                json_order_claim['refund_charge'] = float(order_claim.find('refundCharge').text.strip())
                                    if order_claim.find('refundUseDepositCommission'):  json_order_claim['refund_use_deposit_commission'] = float(order_claim.find('refundUseDepositCommission').text.strip())
                                    if order_claim.find('refundUseMileageCommission'):  json_order_claim['refund_use_mileage_commission'] = float(order_claim.find('refundUseMileageCommission').text.strip())
                                    if order_claim.find('handleGroupCd'):               json_order_claim['handle_group_cd'] = order_claim.find('handleGroupCd').text.strip()
                                    if order_claim.find('regDt'):                       json_order_claim['reg_dt'] = order_claim.find('regDt').text.strip()
                                    idx = idx +1
                                    order_doc.append('order_claim_data',
                                        json_order_claim
                                    )

                    order_doc.save(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_version=True # do not create a version record
                    )
                else:
                    print(cur_order_no)
                    order_doc = frappe.new_doc('Godomall Order')
                    order_doc.order_no=order.find('orderNo').text.strip()    #주문번호
                    order_doc.order_date = "20"+ order.find('orderNo').text.strip()[0:6]
                    if order.find('memNo'):
                        order_doc.mem_no=order.find('memNo').text.strip()    #회원번호
                    if order.find('apiOrderGoodsNo'):
                        order_doc.api_order_goods_no=order.find('apiOrderGoodsNo').text.strip()    #외부채널품목고유번호
                    if order.find('orderStatus'):
                        order_doc.order_status=order.find('orderStatus').text.strip()    #주문상태 코드 코드표 참조
                    if order.find('orderIp'):
                        order_doc.order_ip=order.find('orderIp').text.strip()    #주문자IP
                    if order.find('orderChannelFl'):
                        order_doc.order_channel_fl=order.find('orderChannelFl').text.strip()    #주문채널
                    if order.find('orderTypeFl'):
                        order_doc.order_type_fl=order.find('orderTypeFl').text.strip()    #주문유형 코드표 참조
                    if order.find('orderEmail'):
                        order_doc.order_email=order.find('orderEmail').text.strip()    #이메일
                    if order.find('orderGoodsNm'):
                        order_doc.order_goods_nm=order.find('orderGoodsNm').text.strip()    #주문상품명
                    if order.find('orderGoodsCnt'):
                        order_doc.order_goods_cnt=order.find('orderGoodsCnt').text.strip()    #주문상품갯수
                    if order.find('settlePrice'):
                        order_doc.settle_price=order.find('settlePrice').text.strip()    #총 주문금액
                    if order.find('taxSupplyPrice'):
                        order_doc.tax_supply_price=order.find('taxSupplyPrice').text.strip()    #최초 총 과세금액
                    if order.find('taxVatPrice'):
                        order_doc.tax_vat_price=order.find('taxVatPrice').text.strip()    #최초 총 부가세 금액
                    if order.find('taxFreePrice'):
                        order_doc.tax_free_price=order.find('taxFreePrice').text.strip()    #최초 총 면세금액
                    if order.find('realTaxSupplyPrice'):
                        order_doc.real_tax_supply_price=order.find('realTaxSupplyPrice').text.strip()    #실제 총 과세금액(환불제외)
                    if order.find('realTaxVatPrice'):
                        order_doc.real_tax_vat_prcie=order.find('realTaxVatPrice').text.strip()    #실제 총 부가세(환불제외)
                    if order.find('realTaxFreePrice'):
                        order_doc.real_tax_free_price=order.find('realTaxFreePrice').text.strip()    #실제 총 면세금액(환불제외)
                    if order.find('useMileage'):
                        order_doc.use_mileage=order.find('useMileage').text.strip()    #주문시 사용한 마일리지
                    if order.find('useDeposit'):
                        order_doc.use_deposit=order.find('useDeposit').text.strip()    #주문시 사용한 예치금
                    if order.find('totalGoodsPrice'):
                        order_doc.total_goods_price=order.find('totalGoodsPrice').text.strip()    #총 상품 금액
                    if order.find('totalDeliveryCharge'):
                        order_doc.total_delivery_charge=order.find('totalDeliveryCharge').text.strip()    #총 배송비
                    if order.find('totalGoodsDcPrice'):
                        order_doc.total_goods_dc_price=order.find('totalGoodsDcPrice').text.strip()    #총 상품 할인 금액
                    if order.find('totalMemberDcPrice'):
                        order_doc.total_member_dc_price=order.find('totalMemberDcPrice').text.strip()    #총 회원 할인 금액
                    if order.find('totalMemberOverlapDcPrice'):
                        order_doc.total_member_overlap_price=order.find('totalMemberOverlapDcPrice').text.strip()    #총 그룹별 회원 중복할인 금액
                    if order.find('totalCouponGoodsDcPrice'):
                        order_doc.total_coupon_goods_dc_price=order.find('totalCouponGoodsDcPrice').text.strip()    #총 상품쿠폰 할인 금액
                    if order.find('totalCouponOrderDcPrice'):
                        order_doc.total_coupon_order_dc_price=order.find('totalCouponOrderDcPrice').text.strip()    #총 주문쿠폰 할인 금액
                    if order.find('totalCouponDeliveryDcPrice'):
                        order_doc.total_coupon_delivery_dc_price=order.find('totalCouponDeliveryDcPrice').text.strip()    #총 배송쿠폰 할인금액
                    if order.find('totalMileage'):
                        order_doc.total_mileage=order.find('totalMileage').text.strip()    #총 적립 마일리지
                    if order.find('totalGoodsMileage'):
                        order_doc.total_goods_mileage=order.find('totalGoodsMileage').text.strip()    #총 상품 상품적립 마일리지
                    if order.find('totalMemberMileage'):
                        order_doc.total_member_mileage=order.find('totalMemberMileage').text.strip()    #총 회원적립 마일리지
                    if order.find('totalCouponGoodsMileage'):
                        order_doc.total_coupon_goods_mileage=order.find('totalCouponGoodsMileage').text.strip()    #총 상품쿠폰 적립 마일리지
                    if order.find('totalCouponOrderMileage'):
                        order_doc.total_coupon_order_mileage=order.find('totalCouponOrderMileage').text.strip()    #총 주문쿠폰 적립 마일리지
                    if order.find('firstSaleFl'):
                        order_doc.first_sales_fl=order.find('firstSaleFl').text.strip()    #첫구매 여부 코드표 참조
                    if order.find('settleKind'):
                        order_doc.settle_kind=order.find('settleKind').text.strip()    #주문방법 코드표 참조
                    if order.find('multiShippingFl'):
                        order_doc.multi_shipping_fl=order.find('multiShippingFl').text.strip()    #복수배송지 사용여부 (y = 사용, n = 미사용)
                    if order.find('paymentDt'):
                        order_doc.payment_dt=order.find('paymentDt').text.strip()    #입금일자
                    if order.find('memId'):
                        order_doc.mem_id = order.find('memId').text.strip() 
                    if order.find('memGroupNm'):
                        order_doc.mem_group_nm = order.find('memGroupNm').text.strip() 
                    if order.find('orderGoodsStatusCnt'):
                        order_doc.order_goods_status_cnt = order.find('orderGoodsStatusCnt').text.strip() 
                    
                    order_delivery_list = order.find_all('orderDeliveryData')
                    for order_delivery in order_delivery_list:
                        json_delivery={"order_sno":""}
                        if order_delivery.find('sno'):
                            json_delivery["order_sno"] = cur_order_no + '-' + order_delivery.find('sno').text.strip()
                            json_delivery["order_no"] = cur_order_no
                            json_delivery["sno"] =  order_delivery.find('sno').text.strip()
                        if order_delivery.find('scmNo'):
                            json_delivery["scm_no"] =  order_delivery.find('scmNo').text.strip()
                        if order_delivery.find('commission'):
                            json_delivery["commission"] =  float(order_delivery.find('commission').text.strip())
                        if order_delivery.find('scmAdjustNo'):
                            json_delivery["scm_adjust_no"] =  order_delivery.find('scmAdjustNo').text.strip()
                        if order_delivery.find('scmAdjustAfterNo'):
                            json_delivery["scm_adjust_after_no"] =  order_delivery.find('scmAdjustAfterNo').text.strip()
                        if order_delivery.find('deliveryCharge'):
                            json_delivery["delivery_charge"] =  float(order_delivery.find('deliveryCharge').text.strip())
                        if order_delivery.find('deliveryPolicyCharge'):
                            json_delivery["delivery_policy_charge"] =  float(order_delivery.find('deliveryPolicyCharge').text.strip())
                        if order_delivery.find('deliveryAreaCharge'):
                            json_delivery["delivery_area_charge"] =  float(order_delivery.find('deliveryAreaCharge').text.strip())
                        if order_delivery.find('divisionDeliveryUseDeposit'):
                            json_delivery["division_delivery_use_deposit"] =  float(order_delivery.find('divisionDeliveryUseDeposit').text.strip())
                        if order_delivery.find('divisionDeliveryUseMileage'):
                            json_delivery["division_delivery_use_mileage"] =  float(order_delivery.find('divisionDeliveryUseMileage').text.strip())
                        if order_delivery.find('divisionDeliveryCharge'):
                            json_delivery["division_delivery_charge"] =  float(order_delivery.find('divisionDeliveryCharge').text.strip())
                        if order_delivery.find('divisionMemberDeliveryDcPrice'):
                            json_delivery["division_member_melivery_dc_price"] =  float(order_delivery.find('divisionMemberDeliveryDcPrice').text.strip())
                        if order_delivery.find('deliveryInsuranceFee'):
                            json_delivery["delivery_insurance_fee"] =  float(order_delivery.find('deliveryInsuranceFee').text.strip())
                        if order_delivery.find('deliveryFixFl'):
                            json_delivery["delivery_fix_fl"] =  order_delivery.find('deliveryFixFl').text.strip()
                        if order_delivery.find('deliveryWeightInfo'):
                            json_delivery["delivery_weight_info"] =  order_delivery.find('deliveryWeightInfo').text.strip()
                        if order_delivery.find('overseasDeliveryPolicy'):
                            json_delivery["overseas_delivery_policy"] =  order_delivery.find('overseasDeliveryPolicy').text.strip()
                        if order_delivery.find('deliveryCollectFl'):
                            json_delivery["delivery_collect_fl"] =  order_delivery.find('deliveryCollectFl').text.strip()
                        if order_delivery.find('deliveryCollectPrice'):
                            json_delivery["delivery_collect_price"] =  float(order_delivery.find('deliveryCollectPrice').text.strip())
                        if order_delivery.find('deliveryWholeFreePrice'):
                            json_delivery["delivery_whole_free_price"] =  float(order_delivery.find('deliveryWholeFreePrice').text.strip())
                        if order_delivery.find('statisticsOrderFl'):
                            json_delivery["statistics_order_fl"] =  order_delivery.find('statisticsOrderFl').text.strip()
                        # print(json.dumps(json_delivery))
                        order_doc.append('order_delivery_data',
                            json_delivery
                        )
                        # print(order_delivery.find('sno').text.strip() )
                    
                    order_info_data_list = order.find_all('orderInfoData')
                    order_seq = order.select('orderInfoData')
                    idx = 0
                    # print(order_seq[0]['idx'])
                    if frappe.db.exists('Customer',order.find('orderEmail').text.strip()):
                        cust_doc =frappe.get_doc('Customer',order.find('orderEmail').text.strip())
                        cust_doc.name = order.find('orderEmail').text.strip()
                        cust_doc.customer_name = order_info_data_list[0].find('orderName').text.strip()
                        if order.find('memGroupNm') and frappe.db.exists('Customer Group',order.find('memGroupNm').text.strip()):
                            cust_doc.customer_group = order.find('memGroupNm').text.strip() 
                        else:
                            cust_doc.customer_group = '손님'
                        cust_doc.customer_type = 'Individual'
                        # print(cust_data.order_zonecode[0:2])
                        city_name =""
                        if order_info_data_list[0].find('orderZonecode').text.strip():
                            cust_doc.territory = get_territory_by_zipcode(zip_code=order_info_data_list[0].find('orderZonecode').text.strip())
                        cust_doc.so_required = 1
                        cust_doc.dn_required = 1
                        cust_doc.is_internal_customer = 0
                        cust_doc.default_currency = 'KRW'
                        cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                        cust_doc.save()
                    else:
                        cust_doc =frappe.new_doc('Customer')
                        cust_doc.name = order.find('orderEmail').text.strip()
                        cust_doc.customer_name = order_info_data_list[0].find('orderName').text.strip()
                        if order.find('memGroupNm') and frappe.db.exists('Customer Group',order.find('memGroupNm').text.strip()):
                            cust_doc.customer_group = order.find('memGroupNm').text.strip() 
                        else:
                            cust_doc.customer_group = '손님'
                        cust_doc.customer_type = 'Individual'
                        # print(cust_data.order_zonecode[0:2])
                        city_name =""
                        if order_info_data_list[0].find('orderZonecode').text.strip():
                            cust_doc.territory = get_territory_by_zipcode(zip_code=order_info_data_list[0].find('orderZonecode').text.strip())
                        cust_doc.so_required = 1
                        cust_doc.dn_required = 1
                        cust_doc.is_internal_customer = 0
                        cust_doc.default_currency = 'KRW'
                        cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                        cust_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True,
                            ignore_mandatory=True

                        )
                    for order_info_data in order_info_data_list:
                        
                        # print(order_seq[idx]['idx'])
                        
                        json_order_info={"order_sub_no":""}
                        json_order_info["order_sub_no"] =  cur_order_no +'-'+ order_seq[idx]['idx']
                        idx = idx + 1
                        if order_info_data.find('orderName'):	json_order_info['order_name'] = order_info_data.find('orderName').text.strip()
                        if order_info_data.find('orderEmail'):	json_order_info['order_email'] = order_info_data.find('orderEmail').text.strip()
                        if order_info_data.find('orderCellPhone'):	json_order_info['order_cell_phone'] = order_info_data.find('orderCellPhone').text.strip()
                        if order_info_data.find('orderZipcode'):	json_order_info['order_zipcode'] = order_info_data.find('orderZipcode').text.strip()
                        if order_info_data.find('orderZonecode'):	json_order_info['order_zonecode'] = order_info_data.find('orderZonecode').text.strip()
                        if order_info_data.find('orderState'):	json_order_info['order_state'] = order_info_data.find('orderState').text.strip()
                        if order_info_data.find('orderCity'):	json_order_info['order_city'] = order_info_data.find('orderCity').text.strip()
                        if order_info_data.find('orderAddress'):	json_order_info['order_address'] = order_info_data.find('orderAddress').text.strip()
                        if order_info_data.find('orderAddressSub'):	json_order_info['order_address_sub'] = order_info_data.find('orderAddressSub').text.strip()
                        if order_info_data.find('receiverName'):	json_order_info['receiver_name'] = order_info_data.find('receiverName').text.strip()
                        if order_info_data.find('receiverCellPhone'):	json_order_info['receiver_cell_phone'] = order_info_data.find('receiverCellPhone').text.strip()
                        if order_info_data.find('receiverUseSafeNumberFl'):	json_order_info['receiver_use_safe_number_fl'] = order_info_data.find('receiverUseSafeNumberFl').text.strip()
                        if order_info_data.find('receiverSafeNumber'):	json_order_info['receiver_safe_number'] = order_info_data.find('receiverSafeNumber').text.strip()
                        if order_info_data.find('receiverSafeNumberDt'):	json_order_info['receiver_safe_number_dt'] = order_info_data.find('receiverSafeNumberDt').text.strip()
                        if order_info_data.find('receiverZipcode'):	json_order_info['receiver_zipcode'] = order_info_data.find('receiverZipcode').text.strip()
                        if order_info_data.find('receiverZonecode'):	json_order_info['receiver_zonecode'] = order_info_data.find('receiverZonecode').text.strip()
                        if order_info_data.find('receiverCountry'):	json_order_info['receiver_country'] = order_info_data.find('receiverCountry').text.strip()
                        if order_info_data.find('receiverState'):	json_order_info['receiver_state'] = order_info_data.find('receiverState').text.strip()
                        if order_info_data.find('receiverCity'):	json_order_info['receiver_city'] = order_info_data.find('receiverCity').text.strip()
                        if order_info_data.find('receiverAddress'):	json_order_info['receiver_address'] = order_info_data.find('receiverAddress').text.strip()
                        if order_info_data.find('receiverAddressSub'):	json_order_info['receiver_address_sub'] = order_info_data.find('receiverAddressSub').text.strip()
                        if order_info_data.find('deliveryVisit'):	json_order_info['delivery_visit'] = order_info_data.find('deliveryVisit').text.strip()
                        if order_info_data.find('orderinfoCd'):	json_order_info['orderinfo_cd'] = order_info_data.find('orderinfoCd').text.strip()
                        if order_info_data.find('gitMessage'):	json_order_info['gift_message'] = order_info_data.find('gitMessage').text.strip()
                        # print(json.dumps(json_order_info))
                        order_doc.append('order_info_data',
                            json_order_info
                        )

                        # if order_info_data.find('orderZonecode').text.strip() or order_info_data.find('orderZonecode').text.strip()=="":
                        #     if frappe.db.exists('Address',str(order_info_data.find('orderName').text.strip())+'-Billing'):
                        #         address_doc = frappe.get_doc('Address',str(order_info_data.find('orderName').text.strip())+'-Billing')
                        #         address_doc.address_title = order_info_data.find('orderName').text.strip()
                        #         address_doc.address_type = 'Billing'
                        #         address_doc.address_line1 = order_info_data.find('orderAddress').text.strip()
                        #         address_doc.address_line2 = order_info_data.find('orderAddressSub').text.strip()
                        #         address_doc.city = get_territory_by_zipcode(zip_code=order_info_data.find('orderZonecode').text.strip())
                        #         address_doc.country = "Korea, Republic of"
                        #         address_doc.pincode = order_info_data.find('orderZonecode').text.strip()
                        #         address_doc.email_id = order_info_data.find('orderEmail').text.strip()
                        #         address_doc.phone = order_info_data.find('orderCellPhone').text.strip()
                        #         address_doc.is_primary_address = 1
                        #         address_doc.save()
                        #     else:
                        #         address_doc = frappe.new_doc('Address')
                        #         address_doc.address_title = order_info_data.find('orderName').text.strip()
                        #         address_doc.address_type = 'Billing'
                        #         address_doc.address_line1 = order_info_data.find('orderAddress').text.strip()
                        #         address_doc.address_line2 = order_info_data.find('orderAddressSub').text.strip()
                        #         print(order_doc.order_no)
                        #         address_doc.city = get_territory_by_zipcode(zip_code=order_info_data.find('orderZonecode').text.strip())
                        #         address_doc.country = "Korea, Republic of"
                        #         address_doc.pincode = order_info_data.find('orderZonecode').text.strip()
                        #         address_doc.email_id = order_info_data.find('orderEmail').text.strip()
                        #         address_doc.phone = order_info_data.find('orderCellPhone').text.strip()
                        #         address_doc.is_primary_address = 1
                        #         json_address = {}
                        #         json_address['link_doctype']='Customer'
                        #         json_address['link_name']= order_info_data.find('orderEmail').text.strip()
                        #         json_address['link_title']= order_info_data.find('orderName').text.strip()
                        #         address_doc.append('links',json_address)
                        #         address_doc.insert(
                        #             ignore_permissions=True, # ignore write permissions during insert
                        #             ignore_links=True
                        #         )

                        if order_info_data.find('receiverZonecode'):

                            address_datas = frappe.db.sql("""
                                select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                                where ta.name = tdl.parent 
                                and tdl.parenttype ='Address'
                                and tdl.link_doctype ='Customer'
                                and tdl.link_name =%s
                                and ta.pincode =%s
                                and ta.address_line1 =%s
                                and ta.address_line2 =%s
                            """,(order_info_data.find('orderEmail').text.strip() , order_info_data.find('receiverZonecode').text.strip() ,order_info_data.find('receiverAddress').text.strip() ,order_info_data.find('receiverAddressSub').text.strip()),as_dict=0)
                            if address_datas:
                                for addres_data in address_datas:
                                    address_doc = frappe.get_doc('Address',addres_data)
                                    address_doc.address_title = order_info_data.find('receiverName').text.strip() 
                                    address_doc.address_type = 'Shipping'
                                    address_doc.address_line1 = order_info_data.find('receiverAddress').text.strip()
                                    address_doc.address_line2 = order_info_data.find('receiverAddressSub').text.strip()
                                    address_doc.city = get_territory_by_zipcode(zip_code=order_info_data.find('receiverZonecode').text.strip())
                                    address_doc.country = "Korea, Republic of"
                                    address_doc.pincode = order_info_data.find('receiverZonecode').text.strip()
                                    address_doc.email_id = order_info_data.find('orderEmail').text.strip()
                                    address_doc.phone = order_info_data.find('receiverCellPhone').text.strip()
                                    address_doc.is_shipping_address = 1
                                    address_doc.save()
                                    
                            else:
                                address_doc = frappe.new_doc('Address')
                                address_doc.address_title = order_info_data.find('receiverName').text.strip() 
                                address_doc.address_type = 'Shipping'
                                address_doc.address_line1 = order_info_data.find('receiverAddress').text.strip()
                                address_doc.address_line2 = order_info_data.find('receiverAddressSub').text.strip()
                                address_doc.city = get_territory_by_zipcode(zip_code=order_info_data.find('receiverZonecode').text.strip())
                                address_doc.country = "Korea, Republic of"
                                address_doc.pincode = order_info_data.find('receiverZonecode').text.strip()
                                address_doc.email_id = order_info_data.find('orderEmail').text.strip()
                                address_doc.phone = order_info_data.find('receiverCellPhone').text.strip()
                                address_doc.is_shipping_address = 1
                                json_address = {}
                                json_address['link_doctype']='Customer'
                                json_address['link_name']= order_info_data.find('orderEmail').text.strip()
                                json_address['link_title']= order_info_data.find('orderName').text.strip()
                                address_doc.append('links',json_address)
                                address_doc.insert(
                                    ignore_permissions=True, # ignore write permissions during insert
                                    ignore_links=True,
                                    ignore_mandatory=True
                                )

                    
                    order_goods_data_list = order.find_all('orderGoodsData')
                    for order_goods_data in order_goods_data_list:
                        # print(order_goods_data.find('sno').text.strip() )
                        json_order_goods={"order_sno":""}
                        if order_goods_data.find('sno'):	
                            json_order_goods['order_sno'] = order_goods_data.find('orderNo').text.strip() + '-' +order_goods_data.find('sno').text.strip()
                            json_order_goods['sno'] = order_goods_data.find('sno').text.strip()
                        if order_goods_data.find('orderNo'):	json_order_goods['order_no'] = order_goods_data.find('orderNo').text.strip()
                        if order_goods_data.find('mailSno'):	json_order_goods['mall_sno'] = order_goods_data.find('mailSno').text.strip()
                        if order_goods_data.find('apiOrderGoodsNo'):	json_order_goods['api_order_goods_no'] = order_goods_data.find('apiOrderGoodsNo').text.strip()
                        if order_goods_data.find('orderCd'):	json_order_goods['order_cd'] = order_goods_data.find('orderCd').text.strip()
                        if order_goods_data.find('orderGroupCd'):	json_order_goods['order_group_cd'] = order_goods_data.find('orderGroupCd').text.strip()
                        if order_goods_data.find('eventCd'):	json_order_goods['event_sno'] = order_goods_data.find('eventCd').text.strip()
                        if order_goods_data.find('orderStatus'):	json_order_goods['order_status'] = order_goods_data.find('orderStatus').text.strip()
                        if order_goods_data.find('orderDeliverySno'):	json_order_goods['order_delivery_sno'] = order_goods_data.find('orderDeliverySno').text.strip()
                        if order_goods_data.find('invoiceCompanySno'):	json_order_goods['invoice_company_sno'] = order_goods_data.find('invoiceCompanySno').text.strip()
                        if order_goods_data.find('invoiceNo'):	json_order_goods['invoice_no'] = order_goods_data.find('invoiceNo').text.strip()
                        if order_goods_data.find('scmNo'):	json_order_goods['scm_no'] = order_goods_data.find('scmNo').text.strip()
                        if order_goods_data.find('purchaseNo'):	json_order_goods['purchase_no'] = order_goods_data.find('purchaseNo').text.strip()
                        if order_goods_data.find('commission'):	json_order_goods['commission'] = float(order_goods_data.find('commission').text.strip())
                        if order_goods_data.find('scmAdjustAfterNo'):	json_order_goods['scm_adjust_after_no'] = order_goods_data.find('scmAdjustAfterNo').text.strip()
                        if order_goods_data.find('goodsType'):	json_order_goods['goods_type'] = order_goods_data.find('goodsType').text.strip()
                        if order_goods_data.find('timeSaleFl'):	json_order_goods['time_sale_fl'] = order_goods_data.find('timeSaleFl').text.strip()
                        if order_goods_data.find('parentMustFl'):	json_order_goods['parent_must_fl'] = order_goods_data.find('parentMustFl').text.strip()
                        if order_goods_data.find('parentGoodsNo'):	json_order_goods['parent_goods_no'] = order_goods_data.find('parentGoodsNo').text.strip()
                        if order_goods_data.find('goodsNo'):	json_order_goods['goods_no'] = order_goods_data.find('goodsNo').text.strip()
                        if order_goods_data.find('listImageData'):	json_order_goods['list_image_data'] = order_goods_data.find('listImageData').text.strip()
                        if order_goods_data.find('goodsCd'):	json_order_goods['goods_cd'] = order_goods_data.find('goodsCd').text.strip()
                        if order_goods_data.find('goodsModelNo'):	json_order_goods['goods_model_no'] = order_goods_data.find('goodsModelNo').text.strip()
                        if order_goods_data.find('goodsNm'):	json_order_goods['goods_nm'] = order_goods_data.find('goodsNm').text.strip()
                        if order_goods_data.find('goodsNmStandard'):	json_order_goods['goods_nm_standard'] = order_goods_data.find('goodsNmStandard').text.strip()
                        if order_goods_data.find('goodsCnt'):	json_order_goods['goods_cnt'] = int(order_goods_data.find('goodsCnt').text.strip())
                        if order_goods_data.find('goodsPrice'):	json_order_goods['goods_price'] = float(order_goods_data.find('goodsPrice').text.strip())
                        if order_goods_data.find('divisionUseDeposit'):	json_order_goods['division_use_deposit'] = float(order_goods_data.find('divisionUseDeposit').text.strip())
                        if order_goods_data.find('divisionUseMileage'):	json_order_goods['division_use_mileage'] = float(order_goods_data.find('divisionUseMileage').text.strip())
                        if order_goods_data.find('divisionGoodsDeliveryUseDeposit'):	json_order_goods['division_goods_delivery_use_deposit'] = float(order_goods_data.find('divisionGoodsDeliveryUseDeposit').text.strip())
                        if order_goods_data.find('divisionGoodsDeliveryUseMileage'):	json_order_goods['division_goods_delivery_use_mileage'] = float(order_goods_data.find('divisionGoodsDeliveryUseMileage').text.strip())
                        if order_goods_data.find('divisionCouponOrderDcPrice'):	json_order_goods['division_coupon_order_dc_price'] = float(order_goods_data.find('divisionCouponOrderDcPrice').text.strip())
                        if order_goods_data.find('divisionCouponOrderMileage'):	json_order_goods['division_coupon_order_mileage'] = float(order_goods_data.find('divisionCouponOrderMileage').text.strip())
                        if order_goods_data.find('addGoodsPrice'):	json_order_goods['add_goods_price'] = float(order_goods_data.find('addGoodsPrice').text.strip())
                        if order_goods_data.find('optionPrice'):	json_order_goods['option_price'] = float(order_goods_data.find('optionPrice').text.strip())
                        if order_goods_data.find('optionCostPrice'):	json_order_goods['option_cost_price'] = float(order_goods_data.find('optionCostPrice').text.strip())
                        if order_goods_data.find('optionTextPrice'):	json_order_goods['option_text_price'] = float(order_goods_data.find('optionTextPrice').text.strip())
                        if order_goods_data.find('fixedPrice'):	json_order_goods['fixed_price'] = float(order_goods_data.find('fixedPrice').text.strip())
                        if order_goods_data.find('costPrice'):	json_order_goods['cost_price'] = float(order_goods_data.find('costPrice').text.strip())
                        if order_goods_data.find('goodsDcPrice'):	json_order_goods['goods_dc_price'] = float(order_goods_data.find('goodsDcPrice').text.strip())
                        if order_goods_data.find('memberDcPrice'):	json_order_goods['member_dc_price'] = float(order_goods_data.find('memberDcPrice').text.strip())
                        if order_goods_data.find('memberOverlapDcPrice'):	json_order_goods['member_overlap_dc_price'] = float(order_goods_data.find('memberOverlapDcPrice').text.strip())
                        if order_goods_data.find('couponGoodsDcPrice'):	json_order_goods['coupon_goods_dc_price'] = float(order_goods_data.find('couponGoodsDcPrice').text.strip())
                        if order_goods_data.find('timeSalePrice'):	json_order_goods['time_sale_price'] = float(order_goods_data.find('timeSalePrice').text.strip())
                        if order_goods_data.find('brandBankSalePrice'):	json_order_goods['brand_bank_sale_price'] = float(order_goods_data.find('brandBankSalePrice').text.strip())
                        if order_goods_data.find('myappDcPrice'):	json_order_goods['myapp_dc_price'] = float(order_goods_data.find('myappDcPrice').text.strip())
                        if order_goods_data.find('goodsDeliveryCollectPrice'):	json_order_goods['goods_delivery_collect_price'] = float(order_goods_data.find('goodsDeliveryCollectPrice').text.strip())
                        if order_goods_data.find('goodsMileage'):	json_order_goods['goods_mileage'] = float(order_goods_data.find('goodsMileage').text.strip())
                        if order_goods_data.find('memberMileage'):	json_order_goods['member_mileage'] = float(order_goods_data.find('memberMileage').text.strip())
                        if order_goods_data.find('couponGoodsMileage'):	json_order_goods['coupon_goods_mileage'] = float(order_goods_data.find('couponGoodsMileage').text.strip())
                        if order_goods_data.find('goods_delivery_collect_fl'):	json_order_goods['goods_delivery_collect_fl'] = order_goods_data.find('goods_delivery_collect_fl').text.strip()
                        if order_goods_data.find('minusDepositFl'):	json_order_goods['minus_deposit_fl'] = order_goods_data.find('minusDepositFl').text.strip()
                        if order_goods_data.find('minusRestoreDepositFl'):	json_order_goods['minus_restore_deposit_fl'] = order_goods_data.find('minusRestoreDepositFl').text.strip()
                        if order_goods_data.find('minusMileageFl'):	json_order_goods['minus_mileage_fl'] = order_goods_data.find('minusMileageFl').text.strip()
                        if order_goods_data.find('minusRestoreMileageFl'):	json_order_goods['minus_restore_mileage_fl'] = order_goods_data.find('minusRestoreMileageFl').text.strip()
                        if order_goods_data.find('plusMileageFl'):	json_order_goods['plus_mileage_fl'] = order_goods_data.find('plusMileageFl').text.strip()
                        if order_goods_data.find('plusRestoreMileageFl'):	json_order_goods['plus_restore_mileage_fl'] = order_goods_data.find('plusRestoreMileageFl').text.strip()
                        if order_goods_data.find('minusStockFl'):	json_order_goods['minus_stock_fl'] = order_goods_data.find('minusStockFl').text.strip()
                        if order_goods_data.find('minusRestoreStockFl'):	json_order_goods['minus_restore_stock_fl'] = order_goods_data.find('minusRestoreStockFl').text.strip()
                        if order_goods_data.find('optionSno'):	json_order_goods['option_sno'] = order_goods_data.find('optionSno').text.strip()
                        if order_goods_data.find('optionInfo'):	json_order_goods['option_info'] = order_goods_data.find('optionInfo').text.strip()
                        if order_goods_data.find('optionTextInfo'):	json_order_goods['option_text_info'] = order_goods_data.find('optionTextInfo').text.strip()
                        if order_goods_data.find('cateAllCd'):	json_order_goods['cate_all_cd'] = order_goods_data.find('cateAllCd').text.strip()
                        if order_goods_data.find('hscode'):	json_order_goods['hscode'] = order_goods_data.find('hscode').text.strip()
                        if order_goods_data.find('cancelDt'):	json_order_goods['cancel_dt'] = order_goods_data.find('cancelDt').text.strip()
                        if order_goods_data.find('paymentDt'):	json_order_goods['payment_dt'] = order_goods_data.find('paymentDt').text.strip()
                        if order_goods_data.find('invoiceDt'):	json_order_goods['invoice_dt'] = order_goods_data.find('invoiceDt').text.strip()
                        if order_goods_data.find('deliveryDt'):	json_order_goods['delivery_dt'] = order_goods_data.find('deliveryDt').text.strip()
                        if order_goods_data.find('deliveryCompleteDt'):	json_order_goods['delivery_complete_dt'] = order_goods_data.find('deliveryCompleteDt').text.strip()
                        if order_goods_data.find('finishDt'):	json_order_goods['finish_dt'] = order_goods_data.find('finishDt').text.strip()
                        if order_goods_data.find('mileageGiveDt'):	json_order_goods['mileage_give_dt'] = order_goods_data.find('mileageGiveDt').text.strip()
                        if order_goods_data.find('checkoutData'):	json_order_goods['checkout_data'] = order_goods_data.find('checkoutData').text.strip()
                        if order_goods_data.find('statisticsOrderFl'):	json_order_goods['statistics_order_fl'] = order_goods_data.find('statisticsOrderFl').text.strip()
                        if order_goods_data.find('statisticsGoodsFl'):	json_order_goods['statistics_goods_fl'] = order_goods_data.find('statisticsGoodsFl').text.strip()
                        if order_goods_data.find('deliveryMethodFl'):	json_order_goods['delivery_method_fl'] = order_goods_data.find('deliveryMethodFl').text.strip()
                        if order_goods_data.find('enuri'):	json_order_goods['enuri'] = order_goods_data.find('enuri').text.strip()
                        if order_goods_data.find('goodsDiscountInfo'):	json_order_goods['goods_discount_info'] = order_goods_data.find('goodsDiscountInfo').text.strip()
                        if order_goods_data.find('goodsMileageAddInfo'):	json_order_goods['goods_mileage_add_info'] = order_goods_data.find('goodsMileageAddInfo').text.strip()
                        if order_goods_data.find('inflow'):	json_order_goods['inflow'] = order_goods_data.find('inflow').text.strip()
                        if order_goods_data.find('linkMainTheme'):	json_order_goods['link_main_theme'] = order_goods_data.find('linkMainTheme').text.strip()
                        if order_goods_data.find('visitAddress'):	json_order_goods['visit_address'] = order_goods_data.find('visitAddress').text.strip()
                        if order_goods_data.find('dpxDeliveryType'):	json_order_goods['dpx_delivery_type'] = order_goods_data.find('dpxDeliveryType').text.strip()
                        if order_goods_data.find('dawnInfoType'):	json_order_goods['dawn_info_type'] = order_goods_data.find('dawnInfoType').text.strip()
                        if order_goods_data.find('dawnInfoMemo'):	json_order_goods['dawn_info_memo'] = order_goods_data.find('dawnInfoMemo').text.strip()
                        if order_goods_data.find('dawnInfoAlram'):	json_order_goods['dawn_info_alram'] = order_goods_data.find('dawnInfoAlram').text.strip()
                        if order_goods_data.find('requestBagFl'):	json_order_goods['request_bag_fl'] = order_goods_data.find('requestBagFl').text.strip()
                        if order_goods_data.find('goodsVolume'):	json_order_goods['goods_volume'] = order_goods_data.find('goodsVolume').text.strip()
                        if order_goods_data.find('couponMileageFl'):	json_order_goods['coupon_mileage_fl'] = order_goods_data.find('couponMileageFl').text.strip()
                        if order_goods_data.find('deliveryBundleFl'):	json_order_goods['delivery_bundle_fl'] = order_goods_data.find('deliveryBundleFl').text.strip()
                        if order_goods_data.find('deliveryDueDate'):	json_order_goods['delivery_due_date'] = order_goods_data.find('deliveryDueDate').text.strip()
                        if order_goods_data.find('easypayScmReceiptFl'):	json_order_goods['easypay_scm_receipt_fl'] = order_goods_data.find('easypayScmReceiptFl').text.strip()
                            
                            

                        order_doc.append('order_goods_data',
                            json_order_goods
                        )

                        order_claim_data = order_goods_data.find_all('claimData')
                        order_claim_seq = order_goods_data.select('claimData')
                        json_order_claim={"order_sno":""}
                        idx = 0
                        for order_claim in order_claim_data:
                            json_order_claim['order_sno'] =                cur_order_no +'-'+ order_goods_data.find('sno').text.strip()
                            if order_claim.find('beforeStatus'):                json_order_claim['before_status'] = order_claim.find('beforeStatus').text.strip()
                            if order_claim.find('handleMode'):                  json_order_claim['handle_mode'] = order_claim.find('handleMode').text.strip()
                            if order_claim.find('handleCompleteFl'):            json_order_claim['handle_complete_fl'] = order_claim.find('handleCompleteFl').text.strip()
                            if order_claim.find('handleReason'):                json_order_claim['handle_reason'] = order_claim.find('handleReason').text.strip()
                            if order_claim.find('handleDetailReason'):          json_order_claim['handle_detail_reason'] = order_claim.find('handleDetailReason').text.strip()
                            if order_claim.find('handleDetailReasonShowFl'):    json_order_claim['fandle_detail_reason_show_fl'] = order_claim.find('handleDetailReasonShowFl').text.strip()
                            if order_claim.find('handleDt'):                    json_order_claim['handle_dt'] = order_claim.find('handleDt').text.strip()
                            if order_claim.find('refundPrice'):                 json_order_claim['refund_price'] = float(order_claim.find('refundPrice').text.strip())
                            if order_claim.find('refundUseDeposit'):            json_order_claim['refund_use_deposit'] = order_claim.find('refundUseDeposit').text.strip()
                            if order_claim.find('refundUseMileage'):            json_order_claim['refund_use_mileage'] = order_claim.find('refundUseMileage').text.strip()
                            if order_claim.find('refundDeliveryUseDeposit'):    json_order_claim['refund_delivery_use_deposit'] = order_claim.find('refundDeliveryUseDeposit').text.strip()
                            if order_claim.find('refundDeliveryUseMileage'):    json_order_claim['refund_delivery_use_mileage'] = order_claim.find('refundDeliveryUseMileage').text.strip()
                            if order_claim.find('refundDeliveryCharge'):        json_order_claim['refund_delivery_charge'] = order_claim.find('refundDeliveryCharge').text.strip()
                            if order_claim.find('refundDeliveryInsuranceFee'):  json_order_claim['refund_delivery_insurance_fee'] = order_claim.find('refundDeliveryInsuranceFee').text.strip()
                            if order_claim.find('refundDeliveryCoupon'):        json_order_claim['refund_delivery_coupon'] = order_claim.find('refundDeliveryCoupon').text.strip()
                            if order_claim.find('refundCharge'):                json_order_claim['refund_charge'] = order_claim.find('refundCharge').text.strip()
                            if order_claim.find('refundUseDepositCommission'):  json_order_claim['refund_use_deposit_commission'] = order_claim.find('refundUseDepositCommission').text.strip()
                            if order_claim.find('refundUseMileageCommission'):  json_order_claim['refund_use_mileage_commission'] = order_claim.find('refundUseMileageCommission').text.strip()
                            if order_claim.find('handleGroupCd'):               json_order_claim['handle_group_cd'] = order_claim.find('handleGroupCd').text.strip()
                            if order_claim.find('regDt'):                       json_order_claim['reg_dt'] = order_claim.find('regDt').text.strip()
                            idx = idx +1
                            order_doc.append('order_claim_data',
                                json_order_claim
                            )
                    # parent.append("holidays", {
					# 	'holiday_date': holiday_date,
					# 	'description': holiday_name
					# })
					# parent.save()
                    order_doc.insert(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_links=True,
				        ignore_mandatory=True # insert even if mandatory fields are not set
                    )
        except IndexError:
            print("Godomall XML Parsing Error")
    print(cur_order_no+":"+str(resp.status_code))
    
    return cur_order_no
     
@frappe.whitelist()
def get_common_scm_code():
    secrets_file = os.path.join(os.getcwd(), 'secrets.json')
    with open(secrets_file) as f:
        secrets = json.load(f)
    # print(secrets["godomall_partner_key"])
    # print(secrets["godomall_user_key"])
    # print(secrets["godomall_api_url"])
    url = []
    url.append(secrets["godomall_api_url"])
    url.append("/common/Code_Search.php")
    url.append("?partner_key=")
    url.append(secrets["godomall_partner_key"])
    url.append("&key=")
    url.append(secrets["godomall_user_key"])
    url.append("&code_type=scm")

    # https://openhub.godo.co.kr/godomall5/common/Code_Search.php?partner_key=JUQ2JTg1JUJCQVklRjAlMjYlOTc=&key=JUY1JUI0JUNGJTdGSCUxQlUlMkElRkMlRDIlQjIlRDZYJUIzbGElMUMlMjclMjhnJUExJTk5JTlBLiVCRiVBNCU5MyU5NSU5RCU5RCVFQSVBOSU1RSVBQzYlRTQlQUElMDAlMUFw&code_type=scm
# bench execute godomall_api_customization.api.get_common_scm_code
    resp = requests.get("".join(url))
    print("".join(url))
    if (resp.status_code == 200):
        # print(resp)
        xml_common_code = resp.content
        soup = BeautifulSoup(xml_common_code,"xml")

        try:
            code  = soup.find_all(name="code")
            if code[0].text.strip() == "000":

                common_code_list = soup.find_all("code_data")
                for common_code in common_code_list:
                    if frappe.db.exists('Godomall SCM No',common_code.find("scmNo").text.strip()):
                        scm_doc = frappe.get_doc('Godomall SCM No',common_code.find("scmNo").text.strip())
                        scm_doc.code = common_code.find('scmNo').text.strip()
                        if common_code.find('companyNm'):
                            scm_doc.code_name=common_code.find('companyNm').text.strip()
                        
                        if frappe.db.exists('Supplier',common_code.find("scmNo").text.strip()):
                            supplier_doc = frappe.get_doc('Supplier',common_code.find("scmNo").text.strip())
                            supplier_doc.supplier_name = common_code.find('companyNm').text.strip()
                            supplier_doc.country = 'Korea, Republic of'
                            supplier_doc.supplier_group ='Distributor'
                            supplier_doc.supplier_type = 'Company'
                            supplier_doc.save(
                                        ignore_permissions=True, # ignore write permissions during insert
                                        ignore_version=True, # do not create a version record
                                        ignore_mandatory=True
                                    )
                        else:
                            supplier_doc = frappe.new_doc('Supplier')
                            supplier_doc.name = common_code.find('scmNo').text.strip()
                            supplier_doc.supplier_name = common_code.find('companyNm').text.strip()
                            supplier_doc.country = 'Korea, Republic of'
                            supplier_doc.supplier_group ='Distributor'
                            supplier_doc.supplier_type = 'Company'
                            supplier_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True,
                                        ignore_mandatory=True
                                        )

                        supplier_doc.supplier_name = common_code.find('companyNm').text.strip()
                        supplier_doc.country = 'Korea, Republic of'
                        supplier_doc.supplier_group ='Distributor'
                        supplier_doc.supplier_type = 'Company'
                       
                        scm_doc.save(
                                        ignore_permissions=True, # ignore write permissions during insert
                                        ignore_version=True # do not create a version record
                                    )
                        frappe.db.commit()


                    else:
                        scm_doc = frappe.new_doc('Godomall SCM No')
                        scm_doc.code = common_code.find('scmNo').text.strip()
                        if common_code.find('companyNm'):
                            scm_doc.code_name=common_code.find('companyNm').text.strip()
                        
                        supplier_doc = frappe.new_doc('Supplier')
                        supplier_doc.name = common_code.find('scmNo').text.strip()
                        supplier_doc.supplier_name = common_code.find('companyNm').text.strip()
                        supplier_doc.country = 'Korea, Republic of'
                        supplier_doc.supplier_group ='Distributor'
                        supplier_doc.supplier_type = 'Company'

                        supplier_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True,
                                        ignore_mandatory=True
                                        )
                        
                        scm_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True,
                                        ignore_mandatory=True
                                        )
                        frappe.db.commit()
        

        except IndexError:
            print("Xml parsing Error")
    return resp.status_code

@frappe.whitelist()
def get_common_delivery_code():
    secrets_file = os.path.join(os.getcwd(), 'secrets.json')
    with open(secrets_file) as f:
        secrets = json.load(f)
    # print(secrets["godomall_partner_key"])
    # print(secrets["godomall_user_key"])
    # print(secrets["godomall_api_url"])
    url = []
    url.append(secrets["godomall_api_url"])
    url.append("/common/Code_Search.php")
    url.append("?partner_key=")
    url.append(secrets["godomall_partner_key"])
    url.append("&key=")
    url.append(secrets["godomall_user_key"])
    url.append("&code_type=deliveryCompany")

    # https://openhub.godo.co.kr/godomall5/common/Code_Search.php?partner_key=JUQ2JTg1JUJCQVklRjAlMjYlOTc=&key=JUY1JUI0JUNGJTdGSCUxQlUlMkElRkMlRDIlQjIlRDZYJUIzbGElMUMlMjclMjhnJUExJTk5JTlBLiVCRiVBNCU5MyU5NSU5RCU5RCVFQSVBOSU1RSVBQzYlRTQlQUElMDAlMUFw&code_type=deliveryCompany
# bench execute godomall_api_customization.api.get_common_delivery_code
    resp = requests.get("".join(url))
    if (resp.status_code == 200):

        # print(resp)
        xml_common_code = resp.content
        soup = BeautifulSoup(xml_common_code,"xml")

        try:
            code  = soup.find_all(name="code")
            if code[0].text.strip() == "000":

                common_code_list = soup.find_all("code_data")
                for common_code in common_code_list:
                    if frappe.db.exists('Godomall Delivery Code',common_code.find("invoiceCompanySno").text.strip()):
                        scm_doc = frappe.get_doc('Godomall Delivery Code',common_code.find("invoiceCompanySno").text.strip())
                        scm_doc.code = common_code.find('invoiceCompanySno').text.strip()
                        if common_code.find('invoiceCompanyName'):
                            scm_doc.code_name=common_code.find('invoiceCompanyName').text.strip()
                       
                        scm_doc.save(
                                        ignore_permissions=True, # ignore write permissions during insert
                                        ignore_version=True # do not create a version record
                                    )
                        frappe.db.commit()

                    else:
                        scm_doc = frappe.new_doc('Godomall Delivery Code')
                        scm_doc.code = common_code.find('invoiceCompanySno').text.strip()
                        if common_code.find('invoiceCompanyName'):
                            scm_doc.code_name=common_code.find('invoiceCompanyName').text.strip()
                        

                        scm_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True
                                        )
                        frappe.db.commit()

        except IndexError:
            print("Xml parsing Error")
@frappe.whitelist()
def get_common_member_group_code():
    secrets_file = os.path.join(os.getcwd(), 'secrets.json')
    with open(secrets_file) as f:
        secrets = json.load(f)
    # print(secrets["godomall_partner_key"])
    # print(secrets["godomall_user_key"])
    # print(secrets["godomall_api_url"])
    url = []
    url.append(secrets["godomall_api_url"])
    url.append("/common/Code_Search.php")
    url.append("?partner_key=")
    url.append(secrets["godomall_partner_key"])
    url.append("&key=")
    url.append(secrets["godomall_user_key"])
    url.append("&code_type=memberGroup")

    # https://openhub.godo.co.kr/godomall5/common/Code_Search.php?partner_key=JUQ2JTg1JUJCQVklRjAlMjYlOTc=&key=JUY1JUI0JUNGJTdGSCUxQlUlMkElRkMlRDIlQjIlRDZYJUIzbGElMUMlMjclMjhnJUExJTk5JTlBLiVCRiVBNCU5MyU5NSU5RCU5RCVFQSVBOSU1RSVBQzYlRTQlQUElMDAlMUFw&code_type=deliveryCompany
# bench execute godomall_api_customization.api.get_common_member_group_code
    resp = requests.get("".join(url))
    if (resp.status_code == 200):
        # print(resp)
        xml_common_code = resp.content
        soup = BeautifulSoup(xml_common_code,"xml")

        try:
            code  = soup.find_all(name="code")
            if code[0].text.strip() == "000":

                common_code_list = soup.find_all("code_data")
                for common_code in common_code_list:
                    if frappe.db.exists('Godomall Member Group Code',common_code.find("sno").text.strip()):
                        scm_doc = frappe.get_doc('Godomall Member Group Code',common_code.find("sno").text.strip())
                        scm_doc.code = common_code.find('sno').text.strip()
                        if common_code.find('groupNm'):
                            scm_doc.code_name=common_code.find('groupNm').text.strip()
                       
                        scm_doc.save(
                                        ignore_permissions=True, # ignore write permissions during insert
                                        ignore_version=True # do not create a version record
                                    )
                        frappe.db.commit()

                    else:
                        scm_doc = frappe.new_doc('Godomall Member Group Code')
                        scm_doc.code = common_code.find('sno').text.strip()
                        if common_code.find('groupNm'):
                            scm_doc.code_name=common_code.find('groupNm').text.strip()
                        

                        scm_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                        ignore_links=True
                                        )
                        frappe.db.commit()

        except IndexError:
            print("Xml parsing Error")

@frappe.whitelist()           
def create_update_item(**args):
    # print(args)
    goods_filter=[]
    goods_list =[]
    if args.get('goods_no'):
        goods_list = frappe.db.get_list('Godomall Goods master'
            ,filters= [
            ['docstatus','=', '1' ]
			# ,['parent_goods','=','']
            # ,['bundle_yn','=','N']
            ,['goods_no','=',args.get('goods_no')]
            ]
            , pluck='name')
    else:
        goods_list = frappe.db.get_list('Godomall Goods master'
            ,filters= [
                ['docstatus','=', '1' ]
                # ,['parent_goods','=','']
                # ,['bundle_yn','=','N']
            ]
            , pluck='name')


    # print(goods_list)
    for goods in goods_list:
        item_name =""
        if frappe.db.exists('Godomall Goods Option',{"parent": goods}):

            option_list = frappe.db.get_list('Godomall Goods Option',{"parent": goods} , pluck='name')
            goods_doc = frappe.get_doc('Godomall Goods master',goods)

            for option in option_list:
                if frappe.db.exists('Item',option):
                    
                    option_doc1 = frappe.get_doc('Godomall Goods Option',option)
                    item_doc = frappe.get_doc('Item',option)
                    itm_name =goods_doc.goods_nm 
                    if option_doc1.option_value1:
                        itm_name=itm_name +"-"+ option_doc1.option_value1
                    
                    if option_doc1.option_value2:
                        itm_name=itm_name +"-"+ option_doc1.option_value2

                    if option_doc1.option_value3:
                        itm_name=itm_name +"-"+ option_doc1.option_value3

                    if option_doc1.option_value4:
                        itm_name=itm_name +"-"+ option_doc1.option_value4

                    if option_doc1.option_value5:
                        itm_name=itm_name +"-"+ option_doc1.option_value5

                    item_doc.item_name = itm_name
                    item_doc.item_group = goods_doc.goods_cd
                    item_doc.stock_uom = 'EA'
                    item_doc.disabled = 0
                    item_doc.godo_mall_goods_no =  goods_doc.goods_no
                    if goods_doc.bundle_yn == 'N' :
                        if goods_doc.goods_cd == "맛집":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "공동구매":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "직매입":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        else:
                            item_doc.is_stock_item = 0
                            item_doc.item_group = "위탁"
                    # item_doc.opening_stock = goods_doc.goods_no
                    elif goods_doc.bundle_yn == 'Y':  
                        item_doc.is_stock_item = 0
                        if goods_doc.goods_cd == "맛집":
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "공동구매":
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "직매입":
                            item_doc.item_group = goods_doc.goods_cd
                        else:
                            item_doc.item_group = "위탁"
                    item_doc.is_fixed_asset = 0
                    item_doc.include_item_in_maufacturing = 0
                    item_doc.description = goods_doc.goods_search_word
                    item_doc.valuation_method = 'Moving Average'
                    

                    item_doc.purchase_uom = 'EA'
                    item_doc.sales_uom = 'EA'
                    item_doc.is_purchase_item = 1
                    item_doc.is_sales_item = 1
                    item_doc.save(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_version=True # do not create a version record
                    )
                    # update
                else:
                    item_doc = frappe.new_doc('Item')
                    item_doc.name = option
                    item_doc.item_code = option
                    item_doc.item_name = goods_doc.goods_nm
                    item_doc.item_group = goods_doc.goods_cd
                    item_doc.stock_uom = 'EA'
                    item_doc.disabled = 0
                    item_doc.godo_mall_goods_no =  goods_doc.goods_no
                    if goods_doc.bundle_yn == 'N' :
                        if goods_doc.goods_cd == "맛집":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "공동구매":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "직매입":
                            item_doc.is_stock_item = 1
                            item_doc.item_group = goods_doc.goods_cd
                        else:
                            item_doc.is_stock_item = 0
                            item_doc.item_group = "위탁"
                    elif goods_doc.bundle_yn == 'Y':  
                        item_doc.is_stock_item = 0
                        if goods_doc.goods_cd == "맛집":
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "공동구매":
                            item_doc.item_group = goods_doc.goods_cd
                        elif goods_doc.goods_cd == "직매입":
                            item_doc.item_group = goods_doc.goods_cd
                        else:
                            item_doc.item_group = "위탁"
                    # item_doc.opening_stock = goods_doc.goods_no
                    item_doc.is_fixed_asset = 0
                    item_doc.include_item_in_maufacturing = 0
                    item_doc.description = goods_doc.goods_search_word
                    item_doc.valuation_method = 'Moving Average'
                    json_item_defaults={}
                    json_item_defaults['company'] = 'Thingool'
                    json_item_defaults['default_warehouse'] = '통합물류센터 - TG'
                    json_item_defaults['default_price_list'] = 'Standard Selling'
                    json_item_defaults['default_discount_account'] = ''
                    json_item_defaults['buying_cost_center'] = 'Main - TG'
                    json_item_defaults['default_supplier'] = goods_doc.scm_no
                    json_item_defaults['expense_account'] = '5111 - Cost of Goods Sold - TG'
                    json_item_defaults['selling_cost_center'] = 'Main - TG'
                    json_item_defaults['income_account'] = '4110 - Sales - TG'
                    item_doc.append('item_defaults',
                                json_item_defaults
                            )
                    item_doc.purchase_uom = 'EA'
                    item_doc.sales_uom = 'EA'
                    item_doc.is_purchase_item = 1
                    item_doc.is_sales_item = 1
                    json_tax_template={}
                    if goods_doc.tax_free_fl=='t':
                        json_tax_template['item_tax_template'] = '과세 - TG'
                    else :
                        json_tax_template['item_tax_template'] = '면세 - TG'
                    json_tax_template['valid_from'] = '2000-01-01'
                    item_doc.append('taxes',json_tax_template)
                    item_doc.insert(ignore_permissions=True, # ignore write permissions during insert
                                            ignore_links=True
                                            )
                    
                    # insert

        else:
            goods_doc = frappe.get_doc('Godomall Goods master',goods)
            item_name = goods
            if frappe.db.exists('Item',goods):
                item_doc = frappe.get_doc('Item',goods)
                item_doc.item_code = goods_doc.goods_no
                item_doc.item_name = goods_doc.goods_nm
                item_doc.item_group = goods_doc.goods_cd
                item_doc.stock_uom = 'EA'
                item_doc.disabled = 0
                item_doc.godo_mall_goods_no =  goods_doc.goods_no
                if goods_doc.bundle_yn == 'N' :
                    if goods_doc.goods_cd == "맛집":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "공동구매":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "직매입":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    else:
                        item_doc.is_stock_item = 0
                        item_doc.item_group = "위탁"
                elif goods_doc.bundle_yn == 'Y':  
                    item_doc.is_stock_item = 0
                    if goods_doc.goods_cd == "맛집":
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "공동구매":
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "직매입":
                        item_doc.item_group = goods_doc.goods_cd
                    else:
                        item_doc.item_group = "위탁"
                # item_doc.opening_stock = goods_doc.goods_no
                item_doc.is_fixed_asset = 0
                item_doc.include_item_in_maufacturing = 0
                item_doc.description = goods_doc.goods_search_word
                item_doc.valuation_method = 'Moving Average'
                item_doc.purchase_uom = 'EA'
                item_doc.sales_uom = 'EA'
                item_doc.is_purchase_item = 1
                item_doc.is_sales_item = 1
                item_doc.save(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_version=True # do not create a version record
                )
            else:
                
                item_doc = frappe.new_doc('Item')
                item_doc.name = goods_doc.goods_no
                item_doc.item_code = goods_doc.goods_no
                item_doc.item_name = goods_doc.goods_nm
                item_doc.item_group = goods_doc.goods_cd
                item_doc.stock_uom = 'EA'
                item_doc.disabled = 0
                item_doc.godo_mall_goods_no =  goods_doc.goods_no
                if goods_doc.bundle_yn == 'N' :
                    if goods_doc.goods_cd == "맛집":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "공동구매":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "직매입":
                        item_doc.is_stock_item = 1
                        item_doc.item_group = goods_doc.goods_cd
                    else:
                        item_doc.is_stock_item = 0
                        item_doc.item_group = "위탁"
                # item_doc.opening_stock = goods_doc.goods_no
                elif goods_doc.bundle_yn == 'Y':  
                    item_doc.is_stock_item = 0
                    if goods_doc.goods_cd == "맛집":
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "공동구매":
                        item_doc.item_group = goods_doc.goods_cd
                    elif goods_doc.goods_cd == "직매입":
                        item_doc.item_group = goods_doc.goods_cd
                    else:
                        item_doc.item_group = "위탁"
                item_doc.is_fixed_asset = 0
                item_doc.include_item_in_maufacturing = 0
                item_doc.description = goods_doc.goods_search_word
                item_doc.valuation_method =  frappe.db.get_single_value('Godomall API Setting', 'item_valuation_method')
                json_item_defaults={}
                json_item_defaults['company'] = frappe.db.get_single_value('Godomall API Setting', 'company')
                json_item_defaults['default_warehouse'] =  frappe.db.get_single_value('Godomall API Setting', 'default_warehouse')
                json_item_defaults['default_price_list'] = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                json_item_defaults['default_discount_account'] = frappe.db.get_single_value('Godomall API Setting', 'default_discount_account')
                json_item_defaults['buying_cost_center'] = frappe.db.get_single_value('Godomall API Setting', 'buying_cost_center')
                json_item_defaults['default_supplier'] = goods_doc.scm_no
                json_item_defaults['expense_account'] = frappe.db.get_single_value('Godomall API Setting', 'expense_account')
                json_item_defaults['selling_cost_center'] = frappe.db.get_single_value('Godomall API Setting', 'selling_cost_center')
                json_item_defaults['income_account'] = frappe.db.get_single_value('Godomall API Setting', 'income_account')
                item_doc.append('item_defaults',
                            json_item_defaults
                        )
                item_doc.purchase_uom = 'EA'
                item_doc.sales_uom = 'EA'
                item_doc.is_purchase_item = 1
                item_doc.is_sales_item = 1

                json_tax_template={}
                if goods_doc.tax_free_fl=='t':
                    json_tax_template['item_tax_template'] = '과세 - TG'
                    json_tax_template['tax_category']='과세10%'
                else :
                    json_tax_template['item_tax_template'] = '면세 - TG'
                    json_tax_template['tax_category']='과세10%'
                json_tax_template['valid_from'] = '2000-01-01'
                item_doc.append('taxes',json_tax_template)
                # print(item_doc)
                item_doc.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_links=True
                    )
        frappe.db.set_value('Godomall Goods master', goods, 'item_code', item_name)

# bench execute godomall_api_customization.api.create_update_customer --args "{'order_email':'evilwitch37@naver.com'}"                
@frappe.whitelist()           
def create_update_customer(**kwargs):
    if kwargs.get('order_email'):
        email_name = kwargs.get('order_email')
        print(email_name)
        if frappe.db.exists('Customer',email_name):
            cust_doc =frappe.get_doc('Customer',email_name)
            
            cust_datas = frappe.db.sql("""
                        select b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							,max(IFNULL(if(a.mem_group_nm='',NULL,a.mem_group_nm),'손님')) as mem_group
                            ,max(b.order_cell_phone) as order_cell_phone
                            ,max(b.order_zonecode) as order_zonecode
                            ,max(b.order_address) as order_address
                            ,max(b.order_address_sub ) as order_address_sub
                            ,max(b.receiver_name) as receiver_name
                            ,max(b.receiver_cell_phone) as  receiver_cell_phone
                            ,max(b.receiver_zonecode) as receiver_zonecode
                            ,max(b.receiver_address) as receiver_address
                            ,max(b.receiver_address_sub) as receiver_address_sub 
                    from frappedb.`tabGodomall Order` a , frappedb.`tabGodomall Order Info Data` b
                    where 1=1
                    and a.name  = b.parent 
                    and a.order_email = b.order_email 
                    and b.order_email not in (select name from frappedb.`tabCustomer`)
                    and b.order_email = %s
                    group by  b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							
                            """,email_name, as_dict=1)

            for cust_data in cust_datas:
                cust_doc =frappe.get_doc('Customer',cust_data.order_email)
                cust_doc.name = cust_data.order_email
                cust_doc.customer_name = cust_data.order_name
                cust_doc.customer_group = cust_data.mem_group
                cust_doc.customer_type = 'Individual'
                # print(cust_data.order_zonecode[0:2])
                city_name =""
                if cust_data.order_zonecode[0:2]:
                    cust_doc.territory = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)


                cust_doc.so_required = 1
                cust_doc.dn_required = 1
                cust_doc.is_internal_customer = 0
                cust_doc.default_currency = 'KRW'
                cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                cust_doc.save()
                
                if cust_data.order_zonecode:
                    address_datas = frappe.db.sql("""
                        select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                        where ta.name = tdl.parent 
                        and tdl.parenttype ='Address'
                        and tdl.link_doctype ='Customer'
                        and tdl.link_name =%s
                        and ta.pincode =%s
                        and ta.address_line1 =%s
                        and ta.address_line2 =%s
                    """,(cust_data.order_email,cust_data.order_zonecode,cust_data.order_address,cust_data.order_address_sub),as_dict=0)
                    if address_datas:
                        for addres_data in address_datas:
                            address_doc = frappe.get_doc('Address',addres_data)
                            address_doc.address_title = cust_data.order_name
                            address_doc.address_type = 'Billing'
                            address_doc.address_line1 = cust_data.order_address
                            address_doc.address_line2 = cust_data.order_address_sub
                            address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                            address_doc.country = "Korea, Republic of"
                            address_doc.pincode = cust_data.order_zonecode
                            address_doc.email_id = cust_data.order_email
                            address_doc.phone = cust_data.order_cell_phone
                            address_doc.is_primary_address = 1
                            address_doc.save()
                    else:
                        address_doc = frappe.new_doc('Address')
                        address_doc.address_title = cust_data.order_name
                        address_doc.address_type = 'Billing'
                        address_doc.address_line1 = cust_data.order_address
                        address_doc.address_line2 = cust_data.order_address_sub
                        address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                        address_doc.country = "Korea, Republic of"
                        address_doc.pincode = cust_data.order_zonecode
                        address_doc.email_id = cust_data.order_email
                        address_doc.phone = cust_data.order_cell_phone
                        address_doc.is_primary_address = 1
                        json_address = {}
                        json_address['link_doctype']='Customer'
                        json_address['link_name']=cust_data.order_email
                        json_address['link_title']=cust_data.order_name
                        address_doc.append('links',json_address)
                        address_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True
                        )

                if cust_data.receiver_zonecode:
                    address_datas = frappe.db.sql("""
                        select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                        where ta.name = tdl.parent 
                        and tdl.parenttype ='Address'
                        and tdl.link_doctype ='Customer'
                        and tdl.link_name =%s
                        and ta.pincode =%s
                        and ta.address_line1 =%s
                        and ta.address_line2 =%s
                    """,(cust_data.order_email,cust_data.receiver_zonecode,cust_data.receiver_address,cust_data.receiver_address_sub),as_dict=0)
                    if address_datas:
                        for addres_data in address_datas:
                            address_doc = frappe.get_doc('Address',addres_data)
                            address_doc.address_title = cust_data.receiver_name
                            address_doc.address_type = 'Shipping'
                            address_doc.address_line1 = cust_data.receiver_address
                            address_doc.address_line2 = cust_data.receiver_address_sub
                            address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                            address_doc.country = "Korea, Republic of"
                            address_doc.pincode = cust_data.receiver_zonecode
                            address_doc.email_id = cust_data.order_email
                            address_doc.phone = cust_data.receiver_cell_phone
                            address_doc.is_shipping_address = 1
                            address_doc.save()
                    else:
                        address_doc = frappe.new_doc('Address')
                        address_doc.address_title = cust_data.receiver_name
                        address_doc.address_type = 'Shipping'
                        address_doc.address_line1 = cust_data.receiver_address
                        address_doc.address_line2 = cust_data.receiver_address_sub
                        address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                        address_doc.country = "Korea, Republic of"
                        address_doc.pincode = cust_data.receiver_zonecode
                        address_doc.email_id = cust_data.order_email
                        address_doc.phone = cust_data.receiver_cell_phone
                        address_doc.is_shipping_address = 1
                        json_address = {}
                        json_address['link_doctype']='Customer'
                        json_address['link_name']=cust_data.order_email
                        json_address['link_title']=cust_data.order_name
                        address_doc.append('links',json_address)
                        address_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True
                        )

        else:
            cust_doc =frappe.new_doc('Customer')
            cust_doc.name = email_name

            
            cust_datas = frappe.db.sql("""
                        select b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							,max(IFNULL(if(a.mem_group_nm='',NULL,a.mem_group_nm),'손님')) as mem_group
                            ,max(b.order_cell_phone) as order_cell_phone
                            ,max(b.order_zonecode) as order_zonecode
                            ,max(b.order_address) as order_address
                            ,max(b.order_address_sub ) as order_address_sub
                            ,max(b.receiver_name) as receiver_name
                            ,max(b.receiver_cell_phone) as  receiver_cell_phone
                            ,max(b.receiver_zonecode) as receiver_zonecode
                            ,max(b.receiver_address) as receiver_address
                            ,max(b.receiver_address_sub) as receiver_address_sub 
                    from frappedb.`tabGodomall Order` a , frappedb.`tabGodomall Order Info Data` b
                    where 1=1
                    and a.name  = b.parent 
                    and a.order_email = b.order_email 
                    and b.order_email not in (select name from frappedb.`tabCustomer`)
                    and b.order_email = %s
                    group by  b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							
                            """, email_name,  as_dict=1)
            print(cust_datas)
            for cust_data in cust_datas:
                cust_doc =frappe.new_doc('Customer')
                cust_doc.name = cust_data.order_email
                cust_doc.customer_name = cust_data.order_name
                cust_doc.customer_group = cust_data.mem_group
                cust_doc.customer_type = 'Individual'
                # print(cust_data.order_zonecode[0:2])
                city_name =""
                if cust_data.order_zonecode[0:2]:
                    cust_doc.territory = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)


                cust_doc.so_required = 1
                cust_doc.dn_required = 1
                cust_doc.is_internal_customer = 0
                cust_doc.default_currency = 'KRW'
                cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                cust_doc.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_links=True

                )
                
                if cust_data.order_zonecode:
                    address_doc = frappe.new_doc('Address')
                    address_doc.address_title = cust_data.order_name
                    address_doc.address_type = 'Billing'
                    address_doc.address_line1 = cust_data.order_address
                    address_doc.address_line2 = cust_data.order_address_sub
                    address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                    address_doc.country = "Korea, Republic of"
                    address_doc.pincode = cust_data.order_zonecode
                    address_doc.email_id = cust_data.order_email
                    address_doc.phone = cust_data.order_cell_phone
                    address_doc.is_primary_address = 1
                    json_address = {}
                    json_address['link_doctype']='Customer'
                    json_address['link_name']=cust_data.order_email
                    json_address['link_title']=cust_data.order_name
                    address_doc.append('links',json_address)
                    address_doc.insert(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_links=True
                    )

                if cust_data.receiver_zonecode:
                    address_doc = frappe.new_doc('Address')
                    address_doc.address_title = cust_data.receiver_name
                    address_doc.address_type = 'Shipping'
                    address_doc.address_line1 = cust_data.receiver_address
                    address_doc.address_line2 = cust_data.receiver_address_sub
                    address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                    address_doc.country = "Korea, Republic of"
                    address_doc.pincode = cust_data.receiver_zonecode
                    address_doc.email_id = cust_data.order_email
                    address_doc.phone = cust_data.receiver_cell_phone
                    address_doc.is_shipping_address = 1
                    json_address = {}
                    json_address['link_doctype']='Customer'
                    json_address['link_name']=cust_data.order_email
                    json_address['link_title']=cust_data.order_name
                    address_doc.append('links',json_address)
                    address_doc.insert(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_links=True
                    )
            



        
    elif kwargs.get('order_no'):
        email_name =  frappe.db.get_value('Godomall Order', kwargs.get('order_no'), 'order_email')

        if frappe.db.exists('Customer',email_name):
            cust_doc =frappe.get_doc('Customer',email_name)
            
            cust_datas = frappe.db.sql("""
                        select b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							,max(IFNULL(if(a.mem_group_nm='',NULL,a.mem_group_nm),'손님')) as mem_group
                            ,max(b.order_cell_phone) as order_cell_phone
                            ,max(b.order_zonecode) as order_zonecode
                            ,max(b.order_address) as order_address
                            ,max(b.order_address_sub ) as order_address_sub
                            ,max(b.receiver_name) as receiver_name
                            ,max(b.receiver_cell_phone) as  receiver_cell_phone
                            ,max(b.receiver_zonecode) as receiver_zonecode
                            ,max(b.receiver_address) as receiver_address
                            ,max(b.receiver_address_sub) as receiver_address_sub 
                    from frappedb.`tabGodomall Order` a , frappedb.`tabGodomall Order Info Data` b
                    where 1=1
                    and a.name  = b.parent 
                    and a.order_email = b.order_email 
                    and b.order_email = %s
                    and a.name = %s
                    group by  b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							
                            """,email_name,kwargs.get('order_no'), as_dict=1)

            for cust_data in cust_datas:
                cust_doc =frappe.get_doc('Customer',cust_data.order_email)
                cust_doc.name = cust_data.order_email
                cust_doc.customer_name = cust_data.order_name
                cust_doc.customer_group = cust_data.mem_group
                cust_doc.customer_type = 'Individual'
                # print(cust_data.order_zonecode[0:2])
                city_name =""
                if cust_data.order_zonecode[0:2]:
                    cust_doc.territory = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)


                cust_doc.so_required = 1
                cust_doc.dn_required = 1
                cust_doc.is_internal_customer = 0
                cust_doc.default_currency = 'KRW'
                cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                cust_doc.save()
                
                if cust_data.order_zonecode:
                    address_datas = frappe.db.sql("""
                        select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                        where ta.name = tdl.parent 
                        and tdl.parenttype ='Address'
                        and tdl.link_doctype ='Customer'
                        and tdl.link_name =%s
                        and ta.pincode =%s
                        and ta.address_line1 =%s
                        and ta.address_line2 =%s
                    """,(cust_data.order_email,cust_data.order_zonecode,cust_data.order_address,cust_data.order_address_sub),as_dict=0)
                    if address_datas:
                        for addres_data in address_datas:
                            address_doc = frappe.get_doc('Address',addres_data)
                            address_doc.address_title = cust_data.order_name
                            address_doc.address_type = 'Billing'
                            address_doc.address_line1 = cust_data.order_address
                            address_doc.address_line2 = cust_data.order_address_sub
                            address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                            address_doc.country = "Korea, Republic of"
                            address_doc.pincode = cust_data.order_zonecode
                            address_doc.email_id = cust_data.order_email
                            address_doc.phone = cust_data.order_cell_phone
                            address_doc.is_primary_address = 1
                            address_doc.save()
                    else:
                        address_doc = frappe.new_doc('Address')
                        address_doc.address_title = cust_data.order_name
                        address_doc.address_type = 'Billing'
                        address_doc.address_line1 = cust_data.order_address
                        address_doc.address_line2 = cust_data.order_address_sub
                        address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                        address_doc.country = "Korea, Republic of"
                        address_doc.pincode = cust_data.order_zonecode
                        address_doc.email_id = cust_data.order_email
                        address_doc.phone = cust_data.order_cell_phone
                        address_doc.is_primary_address = 1
                        json_address = {}
                        json_address['link_doctype']='Customer'
                        json_address['link_name']=cust_data.order_email
                        json_address['link_title']=cust_data.order_name
                        address_doc.append('links',json_address)
                        address_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True
                        )

                if cust_data.receiver_zonecode:
                    address_datas = frappe.db.sql("""
                        select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                        where ta.name = tdl.parent 
                        and tdl.parenttype ='Address'
                        and tdl.link_doctype ='Customer'
                        and tdl.link_name =%s
                        and ta.pincode =%s
                        and ta.address_line1 =%s
                        and ta.address_line2 =%s
                    """,(cust_data.order_email,cust_data.receiver_zonecode,cust_data.receiver_address,cust_data.receiver_address_sub),as_dict=0)
                    if address_datas:
                        for addres_data in address_datas:
                            address_doc = frappe.get_doc('Address',addres_data)
                            address_doc.address_title = cust_data.receiver_name
                            address_doc.address_type = 'Shipping'
                            address_doc.address_line1 = cust_data.receiver_address
                            address_doc.address_line2 = cust_data.receiver_address_sub
                            address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                            address_doc.country = "Korea, Republic of"
                            address_doc.pincode = cust_data.receiver_zonecode
                            address_doc.email_id = cust_data.order_email
                            address_doc.phone = cust_data.receiver_cell_phone
                            address_doc.is_shipping_address = 1
                            address_doc.save()
                    else:
                        address_doc = frappe.new_doc('Address')
                        address_doc.address_title = cust_data.receiver_name
                        address_doc.address_type = 'Shipping'
                        address_doc.address_line1 = cust_data.receiver_address
                        address_doc.address_line2 = cust_data.receiver_address_sub
                        address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                        address_doc.country = "Korea, Republic of"
                        address_doc.pincode = cust_data.receiver_zonecode
                        address_doc.email_id = cust_data.order_email
                        address_doc.phone = cust_data.receiver_cell_phone
                        address_doc.is_shipping_address = 1
                        json_address = {}
                        json_address['link_doctype']='Customer'
                        json_address['link_name']=cust_data.order_email
                        json_address['link_title']=cust_data.order_name
                        address_doc.append('links',json_address)
                        address_doc.insert(
                            ignore_permissions=True, # ignore write permissions during insert
                            ignore_links=True
                        )

        else:
            cust_doc =frappe.new_doc('Customer')
            cust_doc.name = email_name

            cust_datas = frappe.db.sql("""
                        select b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							,max(IFNULL(if(a.mem_group_nm='',NULL,a.mem_group_nm),'손님')) as mem_group
                            ,max(b.order_cell_phone) as order_cell_phone
                            ,max(b.order_zonecode) as order_zonecode
                            ,max(b.order_address) as order_address
                            ,max(b.order_address_sub ) as order_address_sub
                            ,max(b.receiver_name) as receiver_name
                            ,max(b.receiver_cell_phone) as  receiver_cell_phone
                            ,max(b.receiver_zonecode) as receiver_zonecode
                            ,max(b.receiver_address) as receiver_address
                            ,max(b.receiver_address_sub) as receiver_address_sub 
                    from frappedb.`tabGodomall Order` a , frappedb.`tabGodomall Order Info Data` b
                    where 1=1
                    and a.name  = b.parent 
                    and a.order_email = b.order_email 
                    and b.order_email = %s
                    and a.name = %s
                    group by  b.order_name 
                            ,b.order_email 
                            ,a.mem_no
                            ,a.mem_id
							
                            """,email_name,kwargs.get('order_no'), as_dict=1)
							
            for cust_data in cust_datas:
                cust_doc =frappe.new_doc('Customer')
                cust_doc.name = cust_data.order_email
                cust_doc.customer_name = cust_data.order_name
                cust_doc.customer_group = cust_data.mem_group
                cust_doc.customer_type = 'Individual'
                # print(cust_data.order_zonecode[0:2])
                city_name =""
                if cust_data.order_zonecode[0:2]:
                    cust_doc.territory = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)


                cust_doc.so_required = 1
                cust_doc.dn_required = 1
                cust_doc.is_internal_customer = 0
                cust_doc.default_currency = 'KRW'
                cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
                cust_doc.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_links=True

                )
                
                if cust_data.order_zonecode:
                    address_doc = frappe.new_doc('Address')
                    address_doc.address_title = cust_data.order_name
                    address_doc.address_type = 'Billing'
                    address_doc.address_line1 = cust_data.order_address
                    address_doc.address_line2 = cust_data.order_address_sub
                    address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                    address_doc.country = "Korea, Republic of"
                    address_doc.pincode = cust_data.order_zonecode
                    address_doc.email_id = cust_data.order_email
                    address_doc.phone = cust_data.order_cell_phone
                    address_doc.is_primary_address = 1
                    json_address = {}
                    json_address['link_doctype']='Customer'
                    json_address['link_name']=cust_data.order_email
                    json_address['link_title']=cust_data.order_name
                    address_doc.append('links',json_address)
                    address_doc.insert(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_links=True
                    )

                if cust_data.receiver_zonecode:
                    address_doc = frappe.new_doc('Address')
                    address_doc.address_title = cust_data.receiver_name
                    address_doc.address_type = 'Shipping'
                    address_doc.address_line1 = cust_data.receiver_address
                    address_doc.address_line2 = cust_data.receiver_address_sub
                    address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                    address_doc.country = "Korea, Republic of"
                    address_doc.pincode = cust_data.receiver_zonecode
                    address_doc.email_id = cust_data.order_email
                    address_doc.phone = cust_data.receiver_cell_phone
                    address_doc.is_shipping_address = 1
                    json_address = {}
                    json_address['link_doctype']='Customer'
                    json_address['link_name']=cust_data.order_email
                    json_address['link_title']=cust_data.order_name
                    address_doc.append('links',json_address)
                    address_doc.insert(
                        ignore_permissions=True, # ignore write permissions during insert
                        ignore_links=True
                    )
            

    else:
        cust_datas = frappe.db.sql("""
                    select b.order_email 
                            ,max(b.order_name) as order_name
                            ,max(a.mem_no) as mem_no
                            ,max(a.mem_id) as mem_id
							,max(IFNULL(if(a.mem_group_nm='',NULL,a.mem_group_nm),'손님')) as mem_group
                            ,max(b.order_cell_phone) as order_cell_phone
                            ,max(b.order_zonecode) as order_zonecode
                            ,max(b.order_address) as order_address
                            ,max(b.order_address_sub ) as order_address_sub
                            ,max(b.receiver_name) as receiver_name
                            ,max(b.receiver_cell_phone) as  receiver_cell_phone
                            ,max(b.receiver_zonecode) as receiver_zonecode
                            ,max(b.receiver_address) as receiver_address
                            ,max(b.receiver_address_sub) as receiver_address_sub 
                    from frappedb.`tabGodomall Order` a , frappedb.`tabGodomall Order Info Data` b
                    where 1=1
                    and a.name  = b.parent 
                    and a.order_email = b.order_email 
                    and b.order_email not in (select name from frappedb.`tabCustomer`)
                    and a.order_date between %s and %s
                    group by  b.order_email 
							
                            """,(kwargs.get('from_date'),kwargs.get('to_date')) , as_dict=1)
        # print(cust_datas)
        for cust_data in cust_datas:
            cust_doc =frappe.new_doc('Customer')
            cust_doc.name = cust_data.order_email
            cust_doc.customer_name = cust_data.order_name
            cust_doc.customer_group = cust_data.mem_group
            cust_doc.customer_type = 'Individual'
            # print(cust_data.order_zonecode[0:2])
            city_name =""
            if cust_data.order_zonecode[0:2]:
                cust_doc.territory = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)


            cust_doc.so_required = 1
            cust_doc.dn_required = 1
            cust_doc.is_internal_customer = 0
            cust_doc.default_currency = 'KRW'
            cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
            cust_doc.insert(
                ignore_permissions=True, # ignore write permissions during insert
                ignore_links=True

            )
            print("Address:"+str(cust_data.order_email))
            if cust_data.order_zonecode:
                
                address_doc = frappe.new_doc('Address')
                address_doc.address_title = cust_data.order_name
                address_doc.address_type = 'Billing'
                address_doc.address_line1 = cust_data.order_address
                address_doc.address_line2 = cust_data.order_address_sub
                address_doc.city = get_territory_by_zipcode(zip_code=cust_data.order_zonecode)
                address_doc.country = "Korea, Republic of"
                address_doc.pincode = cust_data.order_zonecode
                address_doc.email_id = cust_data.order_email
                address_doc.phone = cust_data.order_cell_phone
                address_doc.is_primary_address = 1
                json_address = {}
                json_address['link_doctype']='Customer'
                json_address['link_name']=cust_data.order_email
                json_address['link_title']=cust_data.order_name
                address_doc.append('links',json_address)
                address_doc.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_links=True
                )

            if cust_data.receiver_zonecode:
                address_doc = frappe.new_doc('Address')
                address_doc.address_title = cust_data.receiver_name
                address_doc.address_type = 'Shipping'
                address_doc.address_line1 = cust_data.receiver_address
                address_doc.address_line2 = cust_data.receiver_address_sub
                address_doc.city = get_territory_by_zipcode(zip_code=cust_data.receiver_zonecode)
                address_doc.country = "Korea, Republic of"
                address_doc.pincode = cust_data.receiver_zonecode
                address_doc.email_id = cust_data.order_email
                address_doc.phone = cust_data.receiver_cell_phone
                address_doc.is_shipping_address = 1
                json_address = {}
                json_address['link_doctype']='Customer'
                json_address['link_name']=cust_data.order_email
                json_address['link_title']=cust_data.order_name
                address_doc.append('links',json_address)
                address_doc.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    ignore_links=True
                )
            
            print(cust_data)



def get_territory_by_zipcode(**kwargs):
    # 우편번호가 01-09는 서울    서울 경기 인천 충남만 맛집 배송  --> 서울 경인  참조번호 년월일-지역-세자리 코드
    # 10 -20 경기
    # 21-23 인천
    # 24-26강원
    # 27-29 충북
    # 30 세종
    # 31-33 충남
    # 34-35 대전
    # 36-40 경북
    # 41-43 대구
    # 44-45 울산
    # 46-49 부산
    # 50-53 경남
    # 54-56 전북
    # 57-60 전남
    # 61-62 광주
    # 63 제주
    zip_code = kwargs.get('zip_code')
    territory_name =""
    if int(zip_code[0:2])>=1 and int(zip_code[0:2])<=9:
        territory_name = '서울'
    elif int(zip_code[0:2])>=10 and int(zip_code[0:2])<=20:
        territory_name = '경기'
    elif int(zip_code[0:2])>=21 and int(zip_code[0:2])<=23:
        territory_name = '인천'
    elif int(zip_code[0:2])>=24 and int(zip_code[0:2])<=26:
        territory_name = '강원'
    elif int(zip_code[0:2])>=27 and int(zip_code[0:2])<=29:
        territory_name = '충북'
    elif int(zip_code[0:2])==30:
        territory_name = '세종'
    elif int(zip_code[0:2])>=31 and int(zip_code[0:2])<=33:
        territory_name = '충남'
    elif int(zip_code[0:2])>=34 and int(zip_code[0:2])<=35:
        territory_name = '대전'
    elif int(zip_code[0:2])>=36 and int(zip_code[0:2])<=40:
        territory_name = '경북'
    elif int(zip_code[0:2])>=41 and int(zip_code[0:2])<=43:
        territory_name = '대구'
    elif int(zip_code[0:2])>=44 and int(zip_code[0:2])<=45:
        territory_name = '울산'
    elif int(zip_code[0:2])>=46 and int(zip_code[0:2])<=49:
        territory_name = '부산'
    elif int(zip_code[0:2])>=50 and int(zip_code[0:2])<=53:
        territory_name = '경남'
    elif int(zip_code[0:2])>=54 and int(zip_code[0:2])<=56:
        territory_name = '전북'
    elif int(zip_code[0:2])>=57 and int(zip_code[0:2])<=60:
        territory_name = '전남'
    elif int(zip_code[0:2])>=61 and int(zip_code[0:2])<=62:
        territory_name = '광주'
    elif int(zip_code[0:2])==63 :
        territory_name = '제주'
    else:
        territory_name = 'Korea, Republic of'
    return territory_name

def create_customer_by_param(**args):
    order_email = args.get('order_email')
    cust_doc =frappe.new_doc('Customer')
    cust_doc.name =  args.get('order_email')
    cust_doc.customer_name =  args.get('order_name') 
    cust_doc.customer_group =  args.get('mem_group')
    cust_doc.customer_type = 'Individual'
    # print(cust_data.order_zonecode[0:2])
    city_name =""
    if  args.get('order_zonecode')[0:2]:
        cust_doc.territory = get_territory_by_zipcode(zip_code= args.get('order_zonecode'))

    cust_doc.so_required = 1
    cust_doc.dn_required = 1
    cust_doc.is_internal_customer = 0
    cust_doc.default_currency = 'KRW'
    cust_doc.default_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
    cust_doc.insert(
        ignore_permissions=True, # ignore write permissions during insert
        ignore_links=True
    )
    
    if args.get('order_zonecode'):
        address_doc = frappe.new_doc('Address')
        address_doc.address_title = args.get('order_name')
        address_doc.address_type = 'Billing'
        address_doc.address_line1 =  args.get('order_address')
        address_doc.address_line2 =  args.get('order_address_sub')
        address_doc.city = get_territory_by_zipcode(zip_code= args.get('order_zonecode'))
        address_doc.country = "Korea, Republic of"
        address_doc.pincode = args.get('order_zonecode')
        address_doc.email_id = args.get('order_email')
        address_doc.phone = args.get('order_cell_phone')
        address_doc.is_primary_address = 1
        json_address = {}
        json_address['link_doctype']='Customer'
        json_address['link_name']=args.get('order_email')
        json_address['link_title']=args.get('order_name')
        address_doc.append('links',json_address)
        address_doc.insert(
            ignore_permissions=True, # ignore write permissions during insert
            ignore_links=True
        )

    if args.get('receiver_zonecode'):
        address_doc = frappe.new_doc('Address')
        address_doc.address_title = args.get('receiver_name')
        address_doc.address_type = 'Shipping'
        address_doc.address_line1 = args.get('receiver_address')
        address_doc.address_line2 = args.get('receiver_address_sub')
        address_doc.city = get_territory_by_zipcode(zip_code=args.get('receiver_zonecode'))
        address_doc.country = "Korea, Republic of"
        address_doc.pincode = args.get('receiver_zonecode')
        address_doc.email_id = args.get('order_email')
        address_doc.phone = args.get('receiver_cell_phone')
        address_doc.is_shipping_address = 1
        json_address = {}
        json_address['link_doctype']='Customer'
        json_address['link_name']=args.get('order_email')
        json_address['link_title']=args.get('order_name')
        address_doc.append('links',json_address)
        address_doc.insert(
            ignore_permissions=True, # ignore write permissions during insert
            ignore_links=True
        )


def create_sales_order(**args):
    order_list = frappe.db.get_list('Godomall Order'
			,filters= [
				['batch_job_no','=', args.get('batch_no') ]
				]
				, pluck='name')
    for order in order_list:
        s_order = frappe.get_doc('Godomall Order',order) 
        so_doc = frappe.new_doc('Sales Order')
        # so_doc.title= 
        so_doc.nam = order.order_no
        so_doc.customer = s_order.order_email
        so_doc.order_type='Sales'
        so_doc.skip_delivery_note=0
        so_doc.company =  frappe.db.get_single_value('Godomall API Setting', 'company')
        so_doc.transaction_date = s_order.order_date
        address_datas = frappe.db.sql("""
                        select ta.name from frappedb.tabAddress ta , frappedb.`tabDynamic Link` tdl 
                        where ta.name = tdl.parent 
                        and tdl.parenttype ='Address'
                        and tdl.link_doctype ='Customer'
                        and tdl.link_name =%s
                        and ta.pincode =%s
                        and ta.address_line1 =%s
                        and ta.address_line2 =%s
                    """,(s_order.order_email , s_order.receiver_zonecode , s_order.receiver_address , s_order.receiver_address_sub ),as_dict=0)

        
        
        # so_doc.delivery_date = 
        so_doc.cost_center = frappe.db.get_single_value('Godomall API Setting', 'selling_cost_center')
        so_doc.customer_address = address_datas[0]
        # so_doc.contact_person =
        # so_doc.contact_phone =
        # so_doc.contact_email =
        # so_doc.company_address =
        so_doc.shipping_address_name = address_datas[0]
        # so_doc.dispatch_address_name =
        # so_doc.customer_group=
        # so_doc.territory = 
        so_doc.currency = 'KRW'
        so_doc.conversion_rate = 1
        so_doc.selling_price_list = frappe.db.get_single_value('Godomall API Setting', 'default_price_list')
        # so_doc.price_list_currency=
        # so_doc.plc_conversion_rate=
        so_doc.ignore_pricing_rule=1
        so_doc.set_warehouse = frappe.db.get_single_value('Godomall API Setting', 'default_warehouse')
        # so_doc.scan_barcode=    
        
        so_doc.insert(
                ignore_permissions=True, # ignore write permissions during insert
                ignore_links=True
            )
        pass

def create_purchase_order(**args):
    po_doc = frappe.new_doc('Purchase Order')
    po_doc.insert(
            ignore_permissions=True, # ignore write permissions during insert
            ignore_links=True
        )
