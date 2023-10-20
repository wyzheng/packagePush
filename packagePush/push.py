# -*- coding: utf-8 -*-
"""
微信基础的操作接口
"""

import json
import os.path
import requests
import re
import util

RES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource')
RETRY = 2

CASE_SVR = "wxunitest.oa.com"

cookies = {
        "pkgsvr_sessionid": "tk4qxf80tsdq1adi7oljgg1s7qj8ikar"
    }


def GetUserInfo(uin):
    """
    用uin反查username(微信名） 和 aliasname（别名）
    不限号码使用，返回username,查不到返回空串
    eg: GetUserInfo("100069")

    :param uin:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetTestUserInfo',
        'func_args': {'checkname': str(uin)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    ret = res.json()
    return ret['data']['alias']


# -------------------------------- 获取XML(cache) ---------------------------------
def get_xml_info(id, push_mode):
    url = "http://package.weixin.oa.com/package/get_json/%s/" % id
    res = requests.get(url=url, cookies=cookies)
    content_info = json.loads(res.content.decode())
    for item in content_info:
        xml_info_ori = item['fields']['Info']
        xml = item['fields']
        break
    xml_info_ori = xml_info_ori.split('\n')
    xml_info_dct = {}
    xml_info = []
    for item in xml_info_ori:
        if item == '' or item == 'Priority=0' or item == 'RetryInterval=0':
            continue
        key, value = item.split('=') if re.match(".*=.*", item) else ["type_name", item]
        xml_info_dct[key] = value
        xml_info.append(item)
    push_info = [
        'PushMode=%s'%(push_mode),
        'RetryExpireTime=2000000000',
        'MinRetryInterval=1800'
    ]
    xml_info.extend(push_info)
    xml_info_str = '\r\n'.join(xml_info)
    return xml, xml_info_str, xml_info_dct


# -------------------------------- 生成新XML消息 ---------------------------------
def generate_push_newxml_decrypt(id):
    # 创建推送单，返回 xmlContent
    url = "http://package.weixin.oa.com/res/ini_push_gen_newxml/"
    info, info_str, info_dct = get_xml_info(id, 'decrypt')
    DeviceType = info_dct['DeviceType'].lower()
    PushMode = "decrypt"
    Type = info['Type'].lower()
    OverallReportID = 101
    DownloadNetType = 2
    return_json = 1
    ID = id
    AutoBuildPushInfoName = "自动推送-decrypt-miyawei"
    CdnAddr = "offlinepkg.weixin.qq.com"
    data = {
        "DeviceType": DeviceType,
        "PushMode": PushMode,
        "Type": Type,
        "Info": info_str,
        "OverallReportID": OverallReportID,
        "DownloadNetType": DownloadNetType,
        "return_json": return_json,
        "ID": ID,
        "AutoBuildPushInfoName": AutoBuildPushInfoName,
        "CdnAddr": CdnAddr
    }
    res = requests.post(url, cookies=cookies, data=data)
    res_json = json.loads(res.content.decode())
    XMLContent = res_json['data']['XMLContent']
    return XMLContent


# -------------------------------- 生成新XML消息 ---------------------------------
def generate_push_newxml_cache(id):
    # 创建推送单，返回 xmlContent
    url = "http://package.weixin.oa.com/res/ini_push_gen_newxml/"
    info, info_str, info_dct = get_xml_info(id, 'cache')
    # if "Type27" not in str(info_dct['type_name']) or int(info_dct['Id']) != 1:
    #     return 400, {"message": "this is not a searchtmp, please check!!!"}

    DeviceType = info_dct['DeviceType'].lower()
    PushMode = "cache"
    Type = info['Type'].lower()
    OverallReportID = 101
    DownloadNetType = 2
    return_json = 1
    ID = id
    AutoBuildPushInfoName = "自动推送-cache-miyawei"
    CdnAddr = "offlinepkg.weixin.qq.com"
    data = {
        "DeviceType": DeviceType,
        "PushMode": PushMode,
        "Type": Type,
        "Info": info_str,
        "OverallReportID": OverallReportID,
        "DownloadNetType": DownloadNetType,
        "return_json": return_json,
        "ID": ID,
        "AutoBuildPushInfoName": AutoBuildPushInfoName,
        "CdnAddr": CdnAddr
    }
    res = requests.post(url, cookies=cookies, data=data)
    res_json = json.loads(res.content.decode())
    XMLContent = res_json['data']['XMLContent']
    return XMLContent


# -------------------------------- 下发XML消息 ---------------------------------
def send_xml(uin, id, type=10002):
    """
    给测试号码推送xml，限制在测试319号段， 发送成功返回 0
    eg: SendXML("autotest_mmtools_sh", filename="7.xml.txt")
    xml的文件放在和mmtools目录平级的resource目录的下级目录xml中
    msg_type默认为10002,下发xml的时候使用默认值。

    :param uin:
    :param filename:
    :param type:
    :return:
    """
    """type  默认下发adTest.xml.txt 
        adTest.xml.txt    resource/xml 下面的adTest.xml.txt 全局弹窗，各种btn都有
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    username = GetUserInfo(uin)
    XMLContent_cache = generate_push_newxml_cache(id)
    print("XMLContent_cache:%s", XMLContent_cache)
    XMLContent_decrypt = generate_push_newxml_decrypt(id)
    if XMLContent_cache is None:
        file ='adTest.xml.txt'
        with open(file, 'r') as f:
            XMLContent = util.MMGBK2UTF8(f.read()).decode("utf-8")
    data_cache = {
        'func_name': 'SendMsg',
        'func_args':
            {
                'username': username,
                'tousername': username,
                "content": util.MMGBK2UTF8(XMLContent_cache).decode("utf-8"),
                "type": int(type),
                "number": 1
            }
    }
    res_cache = util.mmtools_post(url, data=json.dumps(data_cache), retry_count=RETRY)

    data_decrypt = {
        'func_name': 'SendMsg',
        'func_args':
            {
                'username': username,
                'tousername': username,
                "content": util.MMGBK2UTF8(XMLContent_decrypt).decode("utf-8"),
                "type": int(type),
                "number": 1
            }
    }
    res_decrypt = util.mmtools_post(url, data=json.dumps(data_decrypt), retry_count=RETRY)
    return res_cache.json()['rtn'], res_decrypt.json()['rtn']
