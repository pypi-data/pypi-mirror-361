# -*- codeing = utf-8 -*-
# @Time :2025/2/20 00:27
# @Author :luzebin
import json
import re
import time

import pandas as pd

from smartpush.export.basic import ExcelExportChecker
from smartpush.export.basic.ReadExcel import read_excel_from_oss
from smartpush.export.basic.ReadExcel import read_excel_and_write_to_dict
from smartpush.export.basic.GetOssUrl import get_oss_address_with_retry
from smartpush.utils.DataTypeUtils import DataTypeUtils
from smartpush.flow import MockFlow
from smartpush.utils import EmailUtlis, ListDictUtils

if __name__ == '__main__':
    # # 导出流程
    # oss1 = "https://cdn.smartpushedm.com/material_ec2/2025-02-26/31c1a577af244c65ab9f9a984c64f3d9/ab%E5%BC%B9%E7%AA%97%E6%B5%8B%E8%AF%952.10%E5%88%9B%E5%BB%BA-%E6%9C%89%E5%85%A8%E9%83%A8%E6%95%B0%E6%8D%AE%E9%94%80%E5%94%AE%E9%A2%9D%E6%98%8E%E7%BB%86%E6%95%B0%E6%8D%AE.xlsx"
    # oss2 = "https://cdn.smartpushedm.com/material_ec2/2025-02-26/31c1a577af244c65ab9f9a984c64f3d9/ab%E5%BC%B9%E7%AA%97%E6%B5%8B%E8%AF%952.10%E5%88%9B%E5%BB%BA-%E6%9C%89%E5%85%A8%E9%83%A8%E6%95%B0%E6%8D%AE%E9%94%80%E5%94%AE%E9%A2%9D%E6%98%8E%E7%BB%86%E6%95%B0%E6%8D%AE.xlsx"
    # # # print(check_excel_all(oss1, oss1))
    # oss3 = "https://cdn.smartpushedm.com/material_ec2/2025-03-07/dca03e35cb074ac2a46935c85de9f510/导出全部客户.csv"
    # oss4 = "https://cdn.smartpushedm.com/material_ec2/2025-03-07/c5fa0cc24d05416e93579266910fbd3e/%E5%AF%BC%E5%87%BA%E5%85%A8%E9%83%A8%E5%AE%A2%E6%88%B7.csv"
    # expected_oss = "https://cdn.smartpushedm.com/material_ec2/2025-02-26/757df7e77ce544e193257c0da35a4983/%E3%80%90%E8%87%AA%E5%8A%A8%E5%8C%96%E5%AF%BC%E5%87%BA%E3%80%91%E8%90%A5%E9%94%80%E6%B4%BB%E5%8A%A8%E6%95%B0%E6%8D%AE%E6%A6%82%E8%A7%88.xlsx"
    # # actual_oss = "https://cdn.smartpushedm.com/material_ec2/2025-02-26/757df7e77ce544e193257c0da35a4983/%E3%80%90%E8%87%AA%E5%8A%A8%E5%8C%96%E5%AF%BC%E5%87%BA%E3%80%91%E8%90%A5%E9%94%80%E6%B4%BB%E5%8A%A8%E6%95%B0%E6%8D%AE%E6%A6%82%E8%A7%88.xlsx"
    # url = "https://cdn.smartpushedm.com/material_ec2_prod/2025-03-06/fe6f042f50884466979155c5ef825736/copy%20of%202025-01-16%20%E5%88%9B%E5%BB%BA%E7%9A%84%20A%2FB%20%E6%B5%8B%E8%AF%95%20copy%20of%202025-01-16%20app-%E6%99%AE%E9%80%9A%E6%A8%A1%E6%9D%BF%201%E6%95%B0%E6%8D%AE%E6%80%BB%E8%A7%88.xlsx"
    #
    # # e_person_oss1 = "https://cdn.smartpushedm.com/material_ec2/2025-02-27/b48f34b3e88045d189631ec1f0f23d51/%E5%AF%BC%E5%87%BA%E5%85%A8%E9%83%A8%E5%AE%A2%E6%88%B7.csv"
    # # a_person_oss2 = "https://cdn.smartpushedm.com/material_ec2/2025-02-27/c50519d803c04e3b9b52d9f625fed413/%E5%AF%BC%E5%87%BA%E5%85%A8%E9%83%A8%E5%AE%A2%E6%88%B7.csv"
    #
    # # # #actual_oss= get_oss_address_with_retry("23161","https://cdn.smartpushedm.com/material_ec2_prod/2025-02-20/dae941ec20964ca5b106407858676f89/%E7%BE%A4%E7%BB%84%E6%95%B0%E6%8D%AE%E6%A6%82%E8%A7%88.xlsx","",'{"page":1,"pageSize":10,"type":null,"status":null,"startTime":null,"endTime":null}')
    # # # res=read_excel_and_write_to_dict(read_excel_from_oss(actual_oss))
    # # # print(res)
    # # # print(read_excel_and_write_to_dict(read_excel_from_oss(oss1), type=".xlsx"))
    # # print(check_excel(check_type="all", actual_oss=actual_oss, expected_oss=expected_oss))
    # # print(check_excel_all(actual_oss=oss1, expected_oss=oss2,skiprows =1))
    # # print(check_excel_all(actual_oss=oss1, expected_oss=oss2,ignore_sort=True))
    # # print(check_excel_all(actual_oss=a_person_oss2, expected_oss=e_person_oss1, check_type="including"))
    # # print(ExcelExportChecker.check_excel_all(actual_oss=oss3, expected_oss=oss4, check_type="including"))
    # # read_excel_csv_data(type=)
    # # print(DataTypeUtils().check_email_format())
    # # errors = ExcelExportChecker.check_field_format(actual_oss=oss1, fileds={0: {5: "time"}}, skiprows=1)
    # # ExcelExportChecker.check_excel_name(actual_oss=oss1, expected_oss=url)
    #
    # # flow触发流程 ------------------------------------------------------------------------------------------------------------------------
    # _url = "http://sp-go-flow-test.inshopline.com"
    # host_domain = "https://test.smartpushedm.com/api-em-ec2"
    # cookies = "_ga=GA1.1.88071637.1717860341; _ga_NE61JB8ZM6=GS1.1.1718954972.32.1.1718954972.0.0.0; _ga_Z8N3C69PPP=GS1.1.1723104149.2.0.1723104149.0.0.0; _ga_D2KXR23WN3=GS1.1.1735096783.3.1.1735096812.0.0.0; osudb_lang=; a_lang=zh-hans-cn; osudb_uid=4213785247; osudb_oar=#01#SID0000128BA0RSWIkgaJoBiROHmmY9zaWt+yNT/cLZpKsGBxkFK4G4Fi+YE+5zicSeFaJmg/+zbnZjt543htvh4TVJOox971SEqJXBJuZu1bKK41UleDRJkw1ufT+wR8zbZw/w1VkSProXPqvU3SXTkEAA6ho; osudb_appid=SMARTPUSH; osudb_subappid=1; ecom_http_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTAzMjY4NDgsImp0aSI6IjE1ZjU1ZDUwLTgwMzgtNDFkMS05YzA4LTAwNTUyYTZjYzc0MSIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0MjEzNzg1MjQ3IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmVhcHAuY29tIiwidXNlclJvbGUiOiJvd25lciIsInBsYXRmb3JtVHlwZSI6Nywic3ViUGxhdGZvcm0iOjEsInBob25lIjoiIiwibGFuZ3VhZ2UiOiJ6aC1oYW5zLWNuIiwiYXV0aFR5cGUiOiIiLCJhdHRyaWJ1dGVzIjp7ImNvdW50cnlDb2RlIjoiQ04iLCJjdXJyZW5jeSI6IkpQWSIsImN1cnJlbmN5U3ltYm9sIjoiSlDCpSIsImRvbWFpbiI6InNtYXJ0cHVzaDQubXlzaG9wbGluZXN0Zy5jb20iLCJsYW5ndWFnZSI6ImVuIiwibWVyY2hhbnRFbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmUuY29tIiwibWVyY2hhbnROYW1lIjoiU21hcnRQdXNoNF9lYzJf6Ieq5Yqo5YyW5bqX6ZO6IiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL01hY2FvIn0sInN0b3JlSWQiOiIxNjQ0Mzk1OTIwNDQ0IiwiaGFuZGxlIjoic21hcnRwdXNoNCIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc0NzczNDg0ODc0Miwic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.O3HQgqEvqb2nxm_6EkYX797j_qqeQ21M1ohIWOJu8Uo; JSESSIONID=57D8A7D13DD34650E0FF72DDB3435515"
    #
    # params = {
    #     "abandonedOrderId": "c2c4a695a36373f56899b370d0f1b6f2",
    #     "areaCode": "",
    #     "context": {
    #         "order": {
    #             "buyerSubscribeEmail": True,
    #             "checkoutId": "c2c4a695a36373f56899b370d0f1b6f2",
    #             "discountCodes": [],
    #             "orderAmountSet": {
    #                 "amount": 3,
    #                 "currency": "JPY"
    #             },
    #             "orderDetails": [
    #                 {
    #                     "productId": "16060724900402692190790343",
    #                     "title": "测试2.0-商品同步AutoSync-2023-08-17 20:52:00",
    #                     "titleTranslations": []
    #                 }
    #             ],
    #             "receiverCountryCode": "HK"
    #         },
    #         "user": {
    #             "addresses": [],
    #             "areaCode": "",
    #             "email": "testsmart200+10@gmail.com",
    #             "firstName": "testsmart200+10",
    #             "gender": "others",
    #             "id": "1911625831177650177",
    #             "lastName": "",
    #             "phone": "",
    #             "tags": [],
    #             "uid": "4603296300",
    #             "userName": "testsmart200+10"
    #         }
    #     },
    #     "controlObjectId": "c2c4a695a36373f56899b370d0f1b6f2",
    #     "controlObjectType": 4,
    #     "email": "testsmart200+10@gmail.com",
    #     "handle": "smartpush4",
    #     "language": "en",
    #     "messageId": "1911625832100397058",
    #     "phone": "",
    #     "platform": 4,
    #     "storeId": "1644395920444",
    #     "timezone": "Asia/Macao",
    #     "triggerId": "c1001",
    #     "uid": "4603296300",
    #     "userId": "1911625831177650177"
    # }
    # update_flow_params = {"id": "FLOW6941975456855532553", "version": "10", "triggerId": "c1001",
    #                       "templateId": "TEMP6911595896571704333", "showData": False, "flowChange": True, "nodes": [
    #         {"type": "trigger", "data": {
    #             "trigger": {"trigger": "c1001", "group": "", "suggestionGroupId": "", "triggerStock": False,
    #                         "completedCount": 4, "skippedCount": 0}, "completedCount": 4, "skippedCount": 0},
    #          "id": "92d115e7-8a86-439a-8cfb-1aa3ef075edf"}, {"type": "delay", "data": {
    #             "delay": {"type": "relative", "relativeTime": 0, "relativeUnit": "HOURS", "designatedTime": ""},
    #             "completedCount": 4}, "id": "e0fc258b-fcfc-421c-b215-8e41638072ca"}, {"type": "sendLetter", "data": {
    #             "sendLetter": {"id": 367462, "activityTemplateId": 367462, "activityName": "flowActivity_EwEi3d",
    #                            "activityImage": "http://cdn.smartpushedm.com/frontend/smart-push/staging/1644395920444/1744102089665/1744102093754_f99e3703.jpeg",
    #                            "emailName": "A Message from Your Cart", "merchantId": "1644395920444",
    #                            "merchantName": "SmartPush4_ec2_自动化店铺",
    #                            "brandName": "SmartPush4_ec2_自动化店铺 AutoTestName", "currency": "JP¥",
    #                            "activityType": "NORMAL", "activityStatus": "ACTIVE", "createTime": 1745201732286,
    #                            "updateTime": 1745201825819, "createDate": "2025-04-21 10:15:32",
    #                            "updateDate": "2025-04-21 10:17:05", "pickContactPacks": [], "excludeContactPacks": [],
    #                            "customerGroupIds": [], "excludeCustomerGroupIds": [], "pickContactInfos": [],
    #                            "excludeContactInfos": [], "customerGroupInfos": [], "excludeCustomerGroupInfos": [],
    #                            "sender": "SmartPush4_ec2_自动化店铺", "senderDomain": "DEFAULT_DOMAIN", "domainType": 3,
    #                            "receiveAddress": "", "originTemplate": 33,
    #                            "currentJsonSchema": "{\"id\":\"a4a9fba2a\",\"type\":\"Stage\",\"props\":{\"backgroundColor\":\"#EAEDF1\",\"width\":\"600px\",\"fullWidth\":\"normal-width\"},\"children\":[{\"id\":\"84ba788da\",\"type\":\"Header\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"98d909a48\",\"type\":\"Column\",\"props\":{},\"children\":[]}]},{\"id\":\"84ba7bbda\",\"type\":\"Section\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"8cab9aa48\",\"type\":\"Column\",\"props\":{},\"children\":[]}]},{\"id\":\"b8bbabad9\",\"type\":\"Footer\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"b3bcabad7\",\"type\":\"Column\",\"props\":{},\"children\":[{\"id\":\"b39b6a94a\",\"type\":\"Subscribe\",\"props\":{\"content\":\"<p style=\\\"text-align:center;\\\"><span style=\\\"font-size:12px\\\"><span style=\\\"font-family:Arial, Helvetica, sans-serif\\\">在此處輸入聯繫地址，可以讓你的顧客更加信任這封郵件</span></span></p>\"},\"children\":[]}]}]}],\"extend\":{\"version\":\"1.0.0\",\"updateTime\":\"2025-03-18T09:57:40.953Z\"}}",
    #                            "currentHtml": "<!doctype html>\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:v=\"urn:schemas-microsoft-com:vml\" xmlns:o=\"urn:schemas-microsoft-com:office:office\">\n  <head>\n    <title></title>\n    <!--[if !mso]><!-->\n    <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\n    <!--<![endif]-->\n    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n    <style type=\"text/css\">\n      #outlook a { padding:0; }\n      body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; }\n      table, td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; }\n      img { border:0;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; }\n      pre{margin: 0;}p{ display: block;margin:0;}\n    </style>\n    <!--[if mso]>\n    <noscript>\n    <xml>\n    <o:OfficeDocumentSettings>\n      <o:AllowPNG/>\n      <o:PixelsPerInch>96</o:PixelsPerInch>\n    </o:OfficeDocumentSettings>\n    </xml>\n    </noscript>\n    <![endif]-->\n    <!--[if lte mso 11]>\n    <style type=\"text/css\">\n      .mj-outlook-group-fix { width:100% !important; }\n    </style>\n    <![endif]-->\n    \n      <!--[if !mso]><!-->\n        <link href=\"https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700\" rel=\"stylesheet\" type=\"text/css\">\n        <style type=\"text/css\">\n          @import url(https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700);\n        </style>\n      <!--<![endif]-->\n\n    \n    \n    <style type=\"text/css\">\n      @media only screen and (min-width:480px) {\n        .mj-column-per-100 { width:100% !important; max-width: 100%; }\n      }\n    </style>\n    <style media=\"screen and (min-width:480px)\">\n      .moz-text-html .mj-column-per-100 { width:100% !important; max-width: 100%; }\n    </style>\n    \n  \n    <style type=\"text/css\">\n    \n    \n    </style>\n    <style type=\"text/css\">\n    @import url(https://fonts.googleapis.com/css?family=Arvo:400|Bodoni+Moda:400|DM+Sans:400|Poppins:400|Hammersmith+One:400|Libre+Baskerville:400|Lexend+Giga:400|Ubuntu:400|Montserrat:400|Nunito:400|News+Cycle:400|Roboto:400|Oswald:400);@import url(https://fonts.googleapis.com/css?family=Asar:400|Bruno+Ace:400|Cantata+One:400|League+Gothic:400|Long+Cang:400|Lovers+Quarrel:400|Nanum+Gothic+Coding:400|Nanum+Myeongjo:400|Noto+Sans+Kaithi:400|Noto+Sans+Kannada:400|Noto+Sans+Math:400|Noto+Sans+Syloti+Nagri:400|Noto+Serif+JP:400|Playwrite+AT+Guides:400|Saira+Extra+Condensed:400|Tsukimi+Rounded:400|Waiting+for+the+Sunrise:400);h1,\nh2,\nh3,\nh4,\nh5 {\n  font-weight: bold;\n  margin-bottom: 0;\n}\np {\n  margin-top: 0;\n  margin-bottom: 0;\n  min-height: 1em;\n}\n\nul {\n  margin-bottom: 0;\n}\n\nth {\n  font-weight: bold;\n}\n\na {\n  text-decoration: none;\n}\n\na::-webkit-scrollbar {\n  -webkit-appearance: none;\n}\n\na::-webkit-scrollbar:horizontal {\n  max-height: 8px;\n}\n\na::-webkit-scrollbar-thumb {\n  border-radius: 8px;\n  background-color: rgba(0, 0, 0, 0.5);\n}\n\nul,\nol,\ndl {\n  margin-top: 16px !important;\n}\n\npre {\n  word-break: break-word;\n  padding: 0;\n  margin: 0;\n  white-space: inherit !important;\n}\n\npre p {\n  word-break: break-word;\n  padding: 0;\n  margin: 0;\n  color: #000000;\n}\n\nspan[style*='color'] a {\n  color: inherit;\n}\n\n.mj-column-no-meida-100{\n  width: 100% !important;\n}\n.mj-column-no-meida-50{\n  width: 50% !important;\n}\n.mj-column-no-meida-33-333333333333336{\n  width: 33.333333333333336% !important;\n}\n.mj-column-no-meida-25{\n  width: 25% !important;\n}\n\n.white-nowrap {\n  white-space: nowrap !important;\n}\n\n/* 间距 */\n.sp-m-p-0 {\n  margin: 0;\n  padding: 0;\n}\n\n.nps-content-span a {\n  color: inherit !important;\n}.sp-font-12 {\n  font-size: 12px !important;\n}\n\n.sp-font-14 {\n  font-size: 14px !important;\n}\n\n.sp-font-16 {\n  font-size: 16px !important;\n}\n\n.sp-font-18 {\n  font-size: 18px !important;\n}\n\n.sp-font-20 {\n  font-size: 20px !important;\n}\n\n.sp-font-22 {\n  font-size: 22px !important;\n}\n\n.sp-font-24 {\n  font-size: 24px !important;\n}\n\n.sp-font-26 {\n  font-size: 26px !important;\n}\n\n.sp-font-28 {\n  font-size: 28px !important;\n}\n\n.sp-font-30 {\n  font-size: 30px !important;\n}\n\n.sp-font-32 {\n  font-size: 32px !important;\n}\n\n.sp-font-34 {\n  font-size: 34px !important;\n}\n\n.sp-font-36 {\n  font-size: 36px !important;\n}\n\n.sp-font-38 {\n  font-size: 38px !important;\n}\n\n.sp-font-40 {\n  font-size: 40px !important;\n}\n\n.sp-font-42 {\n  font-size: 42px !important;\n}\n\n.sp-font-44 {\n  font-size: 44px !important;\n}\n\n.sp-font-46 {\n  font-size: 46px !important;\n}\n\n.sp-font-48 {\n  font-size: 48px !important;\n}\n\n.sp-font-50 {\n  font-size: 50px !important;\n}\n\n.sp-font-52 {\n  font-size: 52px !important;\n}\n\n.sp-font-54 {\n  font-size: 54px !important;\n}\n\n.sp-font-56 {\n  font-size: 56px !important;\n}\n\n.sp-font-58 {\n  font-size: 58px !important;\n}\n\n.sp-font-60 {\n  font-size: 60px !important;\n}\n\n.sp-image-icon {\n  width: 50px;\n}\n\n@media only screen and (max-width:600px) {\n\n  .sp-font-12 {\n    font-size: 12px !important;\n  }\n\n  .sp-font-14 {\n    font-size: 12px !important;\n  }\n\n  .sp-font-16 {\n    font-size: 12px !important;\n  }\n\n  .sp-font-18 {\n    font-size: 13px !important;\n  }\n\n  .sp-font-20 {\n    font-size: 15px !important;\n  }\n\n  .sp-font-22 {\n    font-size: 16px !important;\n  }\n\n  .sp-font-24 {\n    font-size: 18px !important;\n  }\n\n  .sp-font-26 {\n    font-size: 19px !important;\n  }\n\n  .sp-font-28 {\n    font-size: 21px !important;\n  }\n\n  .sp-font-30 {\n    font-size: 22px !important;\n  }\n\n  .sp-font-32 {\n    font-size: 24px !important;\n  }\n\n  .sp-font-34 {\n    font-size: 25px !important;\n  }\n\n  .sp-font-36 {\n    font-size: 27px !important;\n  }\n\n  .sp-font-38 {\n    font-size: 28px !important;\n  }\n\n  .sp-font-40 {\n    font-size: 30px !important;\n  }\n\n  .sp-font-42 {\n    font-size: 31px !important;\n  }\n\n  .sp-font-44 {\n    font-size: 32px !important;\n  }\n\n  .sp-font-46 {\n    font-size: 33px !important;\n  }\n\n  .sp-font-48 {\n    font-size: 34px !important;\n  }\n\n  .sp-font-50 {\n    font-size: 35px !important;\n  }\n\n  .sp-font-52 {\n    font-size: 36px !important;\n  }\n\n  .sp-font-54 {\n    font-size: 37px !important;\n  }\n\n  .sp-font-56 {\n    font-size: 38px !important;\n  }\n\n  .sp-font-58 {\n    font-size: 39px !important;\n  }\n\n  .sp-font-60 {\n    font-size: 40px !important;\n  }\n\n  .sp-image-icon {\n    width: 28px !important;\n  }\n\n}@media only screen and (max-width:480px) {\n\n  .sp-img-h-1-TwoVertical-11,\n  .sp-img-h-1-TwoHorizontalColumns-11 {\n    height: 170px !important;\n  }\n\n  .sp-img-h-1-TwoVertical-23,\n  .sp-img-h-1-TwoHorizontalColumns-23 {\n    height: 243px !important;\n  }\n\n  .sp-img-h-1-TwoVertical-34,\n  .sp-img-h-1-TwoHorizontalColumns-34 {\n    height: 227px !important;\n  }\n\n  .sp-img-h-1-TwoVertical-43,\n  .sp-img-h-1-TwoHorizontalColumns-43 {\n    height: 127px !important;\n  }\n\n  .sp-img-h-1-ThreeHorizontalColumns-11 {\n    height: 109px !important;\n  }\n\n  .sp-img-h-1-ThreeHorizontalColumns-23 {\n    height: 163px !important;\n  }\n\n  .sp-img-h-1-ThreeHorizontalColumns-34 {\n    height: 145px !important;\n  }\n\n  .sp-img-h-1-ThreeHorizontalColumns-43 {\n    height: 81px !important;\n  }\n\n  .sp-img-h-2-TwoVertical-11 {\n    height: 164px !important;\n  }\n\n  .sp-img-h-2-TwoVertical-23 {\n    height: 246px !important;\n  }\n\n  .sp-img-h-2-TwoVertical-34 {\n    height: 218px !important;\n  }\n\n  .sp-img-h-2-TwoVertical-43 {\n    height: 123px !important;\n  }\n\n  .sp-img-h-2-ThreeHorizontalColumns-11,\n  .sp-img-h-2-TwoHorizontalColumns-11 {\n    height: 76px !important;\n  }\n\n  .sp-img-h-2-ThreeHorizontalColumns-23,\n  .sp-img-h-2-TwoHorizontalColumns-23 {\n    height: 113px !important;\n  }\n\n  .sp-img-h-2-ThreeHorizontalColumns-34,\n  .sp-img-h-2-TwoHorizontalColumns-34 {\n    height: 101px !important;\n  }\n\n  .sp-img-h-2-ThreeHorizontalColumns-43,\n  .sp-img-h-2-TwoHorizontalColumns-43 {\n    height: 57px !important;\n  }\n}@media only screen and (min-width: 320px) and (max-width: 599px) {\n  .mj-w-50 {\n    width: 50% !important;\n    max-width: 50%;\n  }\n}\n\n@media only screen and (max-width: 480px) {\n  .shop-white-mobile {\n    width: 100% !important;\n  }\n  .mj-td-force-100{\n    display: inline-block;\n    width: 100% !important;\n  }\n\n  .mj-ImageText-screen {\n    width: 100% !important;\n  }\n  .mj-ImageText-img {\n    margin: 0 auto;\n  }\n\n  .mj-ImageText-margin {\n    margin: 0 !important;\n  }\n\n  .mj-ImageText-margin-zero {\n    margin: 0 5px 0 0 !important;\n  }\n\n  .mj-ImageText-margin-one {\n    margin: 0 0 0 5px !important;\n  }\n  .mj-column-per-50-force {\n    width: 50% !important;\n    max-width: 50%;\n  }\n}\n\n@media only screen and (min-width: 480px) {\n  .mj-imagetext-force-100{\n    display: inline-block;\n    width: 100% !important;\n  }\n  .mj-column-per-100 {\n    width: 100% !important;\n    max-width: 100%;\n  }\n\n  .mj-column-per-50 {\n    width: 50% !important;\n    max-width: 50%;\n  }\n\n  .mj-column-per-33-333333333333336 {\n    width: 33.333333333333336% !important;\n    max-width: 33.333333333333336%;\n  }\n\n  .mj-column-per-25 {\n    width: 25% !important;\n    max-width: 25%;\n  }\n\n\n  .mg-column-per-46-5 {\n    width: 46.5% !important;\n    max-width: 46.5%;\n  }\n\n  .mj-AbandonProduct-cloum-align-center {\n    align-items: flex-start !important;\n  }\n\n\n  .mj-OrderInformation-padding-top-220 {\n    padding-top: 20px !important;\n  }\n\n  .mj-OrderInformation-float-left {\n    float: left !important;\n  }\n}@media only screen and (max-width: 480px) {\n  .mt-1{\n    margin-top: 1px;\n  }\n  .mt-2{\n    margin-top: 2px;\n  }\n  .mt-3{\n    margin-top: 3px;\n  }\n  .mt-4{\n    margin-top: 4px;\n  }\n  .mt-5{\n    margin-top: 5px;\n  }\n  .mt-6{\n    margin-top: 7px;\n  }\n  .mt-8{\n    margin-top: 9px;\n  }\n  .mt-10{\n    margin-top: 10px;\n  }\n\n}\n    </style>\n    \n  </head>\n  <body style=\"word-spacing:normal;background-color:#EAEDF1;\">\n    \n    \n      <div\n         style=\"background-color:#EAEDF1;\"\n      >\n        <table className=\"pv-stage\">\n      <tbody>\n        <tr>\n          <td style=\"display:table-column;\"><div style=\"width:1px; height:1px;\"><img style=\"width:1px; height:1px;\" width=\"1\" src=\"${SP_OPEN_EMAIL_URL}\" />\n          </div></td>\n        </tr>\n      </tbody>\n    </table><div mso-hide: all; position: fixed; height: 0; max-height: 0; overflow: hidden; font-size: 0; style=\"display:none;\">${emailSubtitle}</div>\n      \n      <!--[if mso | IE]><table align=\"center\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" class=\"\" role=\"presentation\" style=\"width:600px;\" width=\"600\" bgcolor=\"#ffffff\" ><tr><td style=\"line-height:0px;font-size:0px;mso-line-height-rule:exactly;\"><![endif]-->\n    \n      \n      <div  style=\"background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:600px;\">\n        \n        <table\n           align=\"center\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" role=\"presentation\" style=\"background:#ffffff;background-color:#ffffff;width:100%;\"\n        >\n          <tbody>\n            <tr>\n              <td\n                 style=\"border-bottom:1px none #ffffff;border-left:1px none #ffffff;border-right:1px none #ffffff;border-top:1px none #ffffff;direction:ltr;font-size:0px;padding:20px 0;padding-bottom:0px;padding-left:0px;padding-right:0px;padding-top:0px;text-align:center;\"\n              >\n                <!--[if mso | IE]><table role=\"presentation\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\"><tr><td class=\"\" style=\"vertical-align:top;width:598px;\" ><![endif]-->\n            \n      <div\n         class=\"mj-column-per-100 mj-outlook-group-fix\" style=\"font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;\"\n      >\n        \n      <table\n         border=\"0\" cellpadding=\"0\" cellspacing=\"0\" role=\"presentation\" style=\"vertical-align:top;\" width=\"100%\"\n      >\n        <tbody>\n          \n              <tr>\n                <td\n                   align=\"left\" style=\"font-size:0px;padding:0;word-break:break-word;\"\n                >\n                  \n      <table\n         cellpadding=\"0\" cellspacing=\"0\" width=\"100%\" border=\"0\" style=\"color:#000000;font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:13px;line-height:22px;table-layout:fixed;width:100%;border:none;\"\n      >\n        <table style=\"margin:0;padding:0;width:100%;table-layout:fixed\" class=\"\" sp-id=\"subscribe-area-b39b6a94a\"><tbody><tr style=\"width:100%\"><td style=\"margin:0;padding:0;width:100%;text-align:center;padding-top:20px;padding-left:20px;padding-right:20px;padding-bottom:20px;background-color:transparent;font-family:arial,helvetica,sans-serif,Arial, Helvetica, sans-serif\" class=\"Subscribe\"><table cellPadding=\"0\" cellSpacing=\"0\" style=\"width:100%\"><tbody><tr><td align=\"center\" class=\"sp-font-16\" valign=\"middle\" style=\"padding-left:10px;padding-right:10px;padding-top:10px;text-align:left;font-size:16px\"><div><p style=\"text-align:center;\"><span style=\"font-size:12px\"><span style=\"font-family:Arial, Helvetica, sans-serif\">在此處輸入聯繫地址，可以讓你的顧客更加信任這封郵件</span></span></p></div></td></tr><tr><td align=\"center\" valign=\"middle\" height=\"20\" style=\"font-size:12px;font-family:arial,helvetica,sans-serif,Arial, Helvetica, sans-serif;padding-left:10px;padding-right:10px;padding-bottom:20px\"></td></tr><div><tr style=\"${hide_logo}\" sp-id=\"subscribe-dom-b39b6a94a\">\n      <td class='sp-font-16' style=\"padding-left:20px;padding-right:20px;padding-top:20px;text-align:center;font-size:16px\" >\n        <div style=\"border-top: 1px solid #EEF1F6\">\n          <img src=\"https://cdn.smartpushedm.com/frontend/smart-push/product/image/1731577171577_83853d55.png\" style=\"padding: 10px;vertical-align: middle;width: 158px;\"alt=\"\" />\n        </div>\n        <p style=\"color:#343434;font-size:12px\">Providing content services for [[shopName]]</p>\n      </td>\n    </tr></div></tbody></table></td></tr></tbody></table>\n      </table>\n    \n                </td>\n              </tr>\n            \n        </tbody>\n      </table>\n    \n      </div>\n    \n          <!--[if mso | IE]></td></tr></table><![endif]-->\n              </td>\n            </tr>\n          </tbody>\n        </table>\n        \n      </div>\n    \n      \n      <!--[if mso | IE]></td></tr></table><![endif]-->\n    \n    \n      </div>\n    \n  </body>\n</html>\n  ",
    #                            "previewJsonSchema": "{\"id\":\"a4a9fba2a\",\"type\":\"Stage\",\"props\":{\"backgroundColor\":\"#EAEDF1\",\"width\":\"600px\",\"fullWidth\":\"normal-width\"},\"children\":[{\"id\":\"84ba788da\",\"type\":\"Header\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"98d909a48\",\"type\":\"Column\",\"props\":{},\"children\":[]}]},{\"id\":\"84ba7bbda\",\"type\":\"Section\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"8cab9aa48\",\"type\":\"Column\",\"props\":{},\"children\":[]}]},{\"id\":\"b8bbabad9\",\"type\":\"Footer\",\"props\":{\"backgroundColor\":\"#ffffff\",\"borderLeft\":\"1px none #ffffff\",\"borderRight\":\"1px none #ffffff\",\"borderTop\":\"1px none #ffffff\",\"borderBottom\":\"1px none #ffffff\",\"paddingTop\":\"0px\",\"paddingBottom\":\"0px\",\"paddingLeft\":\"0px\",\"paddingRight\":\"0px\",\"cols\":[12]},\"children\":[{\"id\":\"b3bcabad7\",\"type\":\"Column\",\"props\":{},\"children\":[{\"id\":\"b39b6a94a\",\"type\":\"Subscribe\",\"props\":{\"content\":\"<p style=\\\"text-align:center;\\\"><span style=\\\"font-size:12px\\\"><span style=\\\"font-family:Arial, Helvetica, sans-serif\\\">在此處輸入聯繫地址，可以讓你的顧客更加信任這封郵件</span></span></p>\"},\"children\":[]}]}]}],\"extend\":{\"version\":\"1.0.0\",\"updateTime\":\"2025-03-18T09:57:40.953Z\"}}",
    #                            "generatedHtml": False,
    #                            "templateUrl": "https://cdn2.smartpushedm.com/material/2021-11-29/d4f96fc873e942a397be708c932bbbe4-自定义排版.png",
    #                            "sendStrategy": "NOW", "totalReceiver": 0, "utmConfigEnable": False,
    #                            "subtitle": "Items in your cart are selling out fast!", "language": "en",
    #                            "languageName": "英语", "timezone": "Asia/Shanghai", "timezoneGmt": "GMT+08:00",
    #                            "type": "FLOW", "relId": "FLOW6941975456855532553",
    #                            "parentId": "TEMP6911595896571704333", "nodeId": "2503b475-ce3e-4906-ab04-0ebc387f0d7e",
    #                            "version": "10", "nodeOrder": 0, "sendType": "EMAIL", "productInfos": [], "blocks": [
    #                     {"domId": "subscribe-dom-b39b6a94a", "blockId": "", "areaId": "", "type": "SP_LOGO",
    #                      "column": 1, "fillStyle": 0, "ratio": ""}], "discountCodes": [], "reviews": [], "awards": [],
    #                            "selectProducts": [], "createSource": "BUILD_ACTIVITY", "contentChange": True,
    #                            "activityChange": False, "imageVersion": "1744102089665", "subActivityList": [],
    #                            "warmupPack": 0, "boosterEnabled": False, "smartSending": False, "boosterCreated": False,
    #                            "gmailPromotion": False, "sendTimeType": "FIXED", "sendTimezone": "B_TIMEZONE",
    #                            "sendTimeDelay": False, "sendOption": 1, "hasUserBlock": False, "hasAutoBlock": False,
    #                            "smsSendDelay": True, "payFunctionList": [], "minSendTime": "2025-04-21 10:15:32",
    #                            "completedCount": 4, "skippedCount": 0, "openRate": 1, "clickRate": 0, "orderIncome": 0,
    #                            "openDistinctUserRate": 1, "clickDistinctUserRate": 0}, "completedCount": 4,
    #             "skippedCount": 0, "openRate": 1, "clickRate": 0, "orderIncome": 0, "openDistinctUserRate": 1,
    #             "clickDistinctUserRate": 0}, "id": "2503b475-ce3e-4906-ab04-0ebc387f0d7e"}],
    #                       "showDataStartTime": 1745164800000, "showDataEndTime": 1745251199000}
    # # mock_pulsar = MockFlow.check_flow(mock_domain=_url, host_domain=host_domain, cookies=cookies,
    # #                                   flow_id="FLOW6966717528141252274", pulsar=params,
    # #                                   split_node=["true"])
    # # print(mock_pulsar)
    #
    # old_flow_counts, old_versions, email_contents = MockFlow.get_current_flow(host_domain=host_domain, cookies=cookies,
    #                                                                           flow_id="FLOW6966717528141252274",
    #                                                                           splits=["false","true","true","true","true","true"],
    #                                                                           get_email_content=True)
    # print(old_flow_counts, old_versions, email_contents)
    #
    # # mock_pulsar_step1, _ = MockFlow.check_flow(mock_domain=_url, host_domain=host_domain, cookies=cookies,
    # #                                            flow_id="FLOW6966717528141252274", pulsar=params,
    # #                                            split_steps="one", split_node=["false", "true", "true"])
    # # print(mock_pulsar_step1)
    # # # time.sleep(60)
    # # mock_pulsar_step2, email_contents = MockFlow.check_flow(mock_domain=_url, host_domain=host_domain, cookies=cookies,
    # #                                                         flow_id="FLOW6966717528141252274",
    # #                                                         old_flow_counts=mock_pulsar_step1,
    # #                                                         split_steps="two", split_node=["false", "true", "true"],
    # #                                                         get_email_content=True)
    # # print(mock_pulsar_step2)
    # # print(email_contents)
    #
    #                                         # split_steps="two")
    # # node_counts, versions = MockFlow.get_current_flow(host_domain=host_domain, cookies=cookies,
    # #                                                   flow_id="FLOW6749144046546626518")
    #
    # # 调试
    # # a = [{'049fd321-5a22-4f92-9692-a3da9507ee4b': {'completedCount': 44}},
    # #      {'09ff19db-33a3-41d8-88e9-12e6017ddfd3': {'completedCount': 44}},
    # #      {'31941d3a-910b-48fa-b302-0f3cf7790401': {'skippedCount': 7}},
    # #      {'01e7c21d-ab57-4f89-98ad-1a437bca1138': {'completedCount': 5}},
    # #      {'f3af15d5-848e-43d3-9ad3-d8f5172df6e0': {'completedCount': 5}},
    # #      {'15630c25-75fa-4456-a6ee-a2bd1e3e64a1': {'completedCount': 42}}]
    # # b = [{'049fd321-5a22-4f92-9692-a3da9507ee4b': {'completedCount': 44}},
    # #      {'09ff19db-33a3-41d8-88e9-12e6017ddfd3': {'completedCount': 44}},
    # #      {'31941d3a-910b-48fa-b302-0f3cf7790401': {'skippedCount': 7}},
    # #      {'01e7c21d-ab57-4f89-98ad-1a437bca1138': {'completedCount': 5}},
    # #      {'f3af15d5-848e-43d3-9ad3-d8f5172df6e0': {'completedCount': 5}},
    # #      {'15630c25-75fa-4456-a6ee-a2bd1e3e64a1': {'completedCount': 42}}]
    # # result = ListDictUtils.compare_lists(temp1=a,
    # #                                      temp2=b, num=1,
    # #                                      check_key=["completedCount", "skippedCount"],
    # #                                      all_key=False)
    # # print(result)
    #
    # # 断言邮件
    # loginEmail, password = 'lulu9600000@gmail.com', 'evvurakhttndwspx'
    # email_property = [{'1AutoTest-固定B-营销-生产2.0-2025-04-24 10:19:47.341333-🔥🔥': {'activityId': 408764,
    #                                                                                   'utmConfigInfo': {
    #                                                                                       'utmSource': '1',
    #                                                                                       'utmMedium': '2',
    #                                                                                       'utmCampaign': '3'},
    #                                                                                   'receiveAddress': 'autotest-smartpushpro5@smartpush.com',
    #                                                                                   'sender': 'SmartPush_Pro5_ec2自动化店铺 AutoTestName',
    #                                                                                   'subtitle': 'AutoTest-2025-04-24 10:19:47.341333-subtitle-[[contact.name]]-🔥🔥'}},
    #                   {'AutoTest-固定B-营销-生产2.0-2025-04-24 10:19:59.023150-🔥🔥': {'activityId': 408765,
    #                                                                                  'utmConfigInfo': {'utmSource': '1',
    #                                                                                                    'utmMedium': '2',
    #                                                                                                    'utmCampaign': '3'},
    #                                                                                  'receiveAddress': '1autotest-smartpushpro5@smartpush.com',
    #                                                                                  'sender': 'SmartPush_Pro5_ec2自动化店铺 AutoTestName',
    #                                                                                  'subtitle': 'AutoTest-2025-04-24 10:19:59.023150-subtitle-[[contact.name]]-🔥🔥'}},
    #                   {'测试邮件-AutoTest_营销_生产2.0_2025_04_24 10:20:28.529290_🔥🔥-😈': {'activityId': None,
    #                                                                                       'utmConfigInfo': None,
    #                                                                                       'receiveAddress': 'autotest-smartpushpro5@smartpush.com',
    #                                                                                       'sender': '1SmartPush_Pro5_ec2自动化店铺 AutoTestName',
    #                                                                                       'subtitle': '营销测试邮件-2025-04-24 10:20:29.560357-😈'}}]
    #
    # # result = EmailUtlis.check_email_content(emailProperty=email_property, loginEmail=loginEmail, password=password)
    # # print(result)
    oss1 = "https://cdn.smartpushedm.com/material_ec2/2025-07-09/861b4821e1874c188bfdd6dd54eff6e9/2025-05-28 18:02 校验群组_2025-07-09.xlsx"
    oss2 = "https://cdn.smartpushedm.com/material_ec2/2025-05-29/5657e9a34727461b8a23969f291b7d69/2025-05-28%2018%3A02%20%E6%A0%A1%E9%AA%8C%E7%BE%A4%E7%BB%84_2025-05-29.xlsx"
    ExcelExportChecker.check_excel_all(actual_oss=oss1, expected_oss=oss2, no_check_name=False)

