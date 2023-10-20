#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信基础的操作接口
"""

import hashlib
import json
import logging
import os.path
import random
import time
import xml.etree.ElementTree as ET

import mmbiztoolsUtil
import util
from StoryXML import *

logger = logging.getLogger()

RES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource')
RETRY = 2

CASE_SVR = "wxunitest.oa.com"


# ------------------------------- 安全策略 ---------------------------------
def set_spam_block_ctrl(username, appname="mmlogin", idc="idc"):
    uin = get_uin(username)
    url = f"http://{CASE_SVR}/mmcasehelper{idc}/mmaccount"
    data = {
        'func_name': 'SpamBlockCtrl',
        'func_args': {'username': username, "OpType": 4, 'appname': appname, 'key': str(uin), 'mask': '0',
                      "keyType": 1,
                      'rulename': 'autotest',
                      'blockLevel': 0, 'whiteLevel': 1, 'ExpiredTime': 86400}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('data').get('ret')


def clear_spam_block_ctrl(username):
    uin = get_uin(username)

    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SpamBlockCtrl',
        'func_args': {'username': username, "OpType": 5, 'appname': 'all', 'key': str(uin), 'mask': '0', "keyType": 1,
                      'rulename': 'autotest',
                      'blockLevel': 0, 'whiteLevel': 1, 'ExpiredTime': 60 * 60 * 24}
    }
    res = util.mmtools_post(url, data=json.dumps(data))
    logger.info("data:%s, res:%s , http status code:%s", data, res.text, res.status_code)
    result = res.json()


def set_whitelist(username, idc="idc"):
    """
    不要主动调用这个接口，后续外网状态在系统上维护：http://wxunitest.oa.com/mockmanager/MainPage?panel=TEST-ACCT-PANEL
    """
    uin = get_uin(username)
    # url = "http://%s/mmautotest/mmtesthelp/setspamticket"
    # data = {"username": user}
    # res = util.retry_get(url, params=data, retry_count=RETRY)
    url = f"http://{CASE_SVR}/mmtools/mmcasehelper{idc}/mmaccount"
    data = {
        'func_name': 'SetSpamTicket',
        'func_args': {"user_uin": uin, "lifetime": 86400, "key": "taw_" + str(uin), "value": ""}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def clearhistory(t_mobile):
    """
    手机注册历史记录清除，避免出现频率拦截的提示
    只能对已经加过安全中心的策略的测试手机号使用，调用成功返回 0
    eg: clearhistory("13250259728")

    :param t_mobile:
    :return:
    """
    # url = "http://%s/mmautotest/mmtesthelp/clearhistory"
    # data = {"uin":"3191000001","mobile":t_mobile}
    # res=util.retry_get(url, params=data, retry_count=RETRY)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    uin = 3191000001
    # IDC = {'shanghai': 1, 'shenzhen': 3, 'hk': 2, 'camel': 8}
    # lifetime = 3600
    mobile = t_mobile.strip()
    data = {
        "func_name": "ClearRegHistory",
        "func_args": {"mobile": str(mobile), "user_uin": int(uin)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def cleardirtydata(t_mobile, type=3):
    """
    手机或者FBuin脏数据清理，避免注册，绑定出现逻辑错误，或者提示失败
    只能对已经加过安全中心的策略的测试手机号使用，调用成功返回0
    eg: cleardirtydata("13250259728")
    eg: cleardirtydata(107730746226250,type=5)

    :param t_mobile:
    :param type:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    optype = "DelAttr"
    mobile = str(t_mobile).strip()
    uin = 3190000002
    itype = type  # [ 1 - username, 2 - uin, 3 - mobile, 4 - email ,5 - fb, 6 - alias  ]
    data = {
        "func_name": "OplogDirtyData",
        "func_args": {"optype": optype, "key": mobile, "itype": itype, "user_uin": int(uin)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def set_RegWhitelist(mobile):
    """
    设置为手机注册白名单-绕过注册的安全策略，调用成功返回0
    只能对已经加过安全中心的策略的测试手机号使用
    eg : 国内号码      set_RegWhitelist("18719460788")
         非大陆手机号   set_RegWhitelist("+8618719460788")

    :param mobile:
    :return:
    """
    # url = "http://%s/mmautotest/mmtesthelp/settestmobile"
    # data = {"mobile":t_mobile}
    # res=util.retry_get(url, params=data, retry_count=RETRY)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    idcuser = ["shrdtest001", "hkrdtest1", "szrdtest001"]  # for route
    all_mobile = AllMobileFormat(mobile)
    _data = {
        "username": "shrdtest001",
        "OpType": 4,
        "appname": "all",
        "key": mobile.strip(),
        "mask": "0",
        "keyType": 1,
        "rulename": "wetest",
        "blockLevel": 0,
        "whiteLevel": 1,
        "ExpiredTime": 86400
    }
    res = None
    for usr in idcuser:
        _data['username'] = usr
        for _mobile in all_mobile:
            _data['key'] = _mobile
            data = {
                "func_name": "SpamBlockCtrl",
                "func_args": _data
            }
            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)

    # add QRCode whitelist
    _data['appname'] = "testnewregmobile"
    _data['whiteLevel'] = 3
    for usr in idcuser:
        _data['username'] = usr
        for _mobile in all_mobile:
            _data['key'] = _mobile
            data = {
                "func_name": "SpamBlockCtrl",
                "func_args": _data
            }
            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)

    _data['appname'] = "mobile_reg_white"
    _data['whiteLevel'] = 1
    for usr in idcuser:
        _data['username'] = usr
        for _mobile in all_mobile:
            _data['key'] = _mobile
            data = {
                "func_name": "SpamBlockCtrl",
                "func_args": _data
            }

            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(_data)
    logger.info(res.json())
    return res.json().get('rtn')


def GetPureMobile(mobile):
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    mobile = str(mobile)
    data = {
        "func_name": "GetMobileInfo",
        "func_args": {"mobile": mobile}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    data = res.json()
    sCC = data['data']['CC']
    sPureMobile = data['data']['PureMobile']
    return sCC, sPureMobile


def AllMobileFormat(mobile):
    (sCC, sPureMobile) = GetPureMobile(mobile)
    return ['+' + sCC + sPureMobile, '+' + sCC + '-' + sPureMobile, sCC + '-' + sPureMobile, sCC + sPureMobile]


def set_all_whiteList(username):
    """
    # 给微信号加所有的白名单，不光是登录绕过安全验证，还有测试号允许改密码，绑定手机等。终极白名单大杀器
    :param username:
    :return:
    """
    uin = get_uin(username)
    if uin == 0:
        return None
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SpamBlockCtrl',
        'func_args': {'username': username, "OpType": 4, 'appname': 'all', 'key': str(uin), 'mask': '0',
                      "keyType": 1,
                      'rulename': 'autotest',
                      'blockLevel': 0, 'whiteLevel': 1, 'ExpiredTime': 3600000}

    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    set_user_attr(username, "UserBlocked", 0)
    set_user_attr(username, "SpamFlag", 0)
    set_user_attr(username, "SnsAntispamFlag", 0)
    ret = set_whitelist(username)
    return ret


#  -------------------------- 手机验证 ：注册，绑定 --------------------------------------


def reg_smsup(t_mobile):
    """
    国内手机号注册上行验证，需要在同意隐私，点下一步之后，再调用这个工具，在"发送短信以验证"界面稍微等几秒轮询到即可继续
    仅限测试手机号使用，调用成功返回 0
    eg : reg_smsup("13250259748")

    :param t_mobile:
    :return:
    """
    # url = "http://%s/mmautotest/mmtesthelp/smsup"
    # data = {"mobile":t_mobile,"idc":"shanghai"}
    # res=util.retry_get(url, params=data, retry_count=RETRY)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    idc = 'shanghai'
    IDC = {'shanghai': 1, 'shenzhen': 3, 'hk': 2, 'camel': 8}
    lifetime = 3600
    mobile = t_mobile.strip()
    data = {
        "func_name": "SetSmsUpTicket",
        "func_args": {"mobile": str(mobile), "idc": IDC[idc], "ExpiredTime": lifetime, }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def reg_smsdown(t_mobile, t_idc, t_type, code="1234"):
    """
    设置手机号下行短信验证码：注册，绑定，解绑
    仅限测试手机号使用，调用成功返回 0
    eg: reg_smsdown("+85292625614","hk","NewReg","1234")
       reg_smsdown("18719460788","hk","Bind","123456")
    idc 填"shenzhen"（大陆手机号用这个），或"hk"（国外手机号，含港台，用这个）
    type为："NewReg"，"Bind" ,"Change" ， 分别对应 注册，绑定手机，更换手机
    code为需要填写的验证码，大陆手机验证码为6位，港台和国外手机验证为4位，如果不填写，默认为"1234"

    :param t_mobile:
    :param t_idc:
    :param t_type:
    :param code:
    :return:
    """
    # url = "http://%s/mmautotest/mmtesthelp/code"
    # data = {"mobile":t_mobile,"code":code,"idc":t_idc,"type":t_type}
    # res=util.retry_get(url, params=data, retry_count=RETRY)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    regkey = "mobiledoreg__"
    key = "mobilebindnreg_"
    changekey = "mobilechangebind_"

    if t_type == "NewReg":
        _key = regkey

    if t_type == "Bind":
        _key = key

    if t_type == "Change":
        _key = changekey

    IDC = {'shanghai': 1, 'shenzhen': 3, 'hk': 2, 'camel': 8}
    mobile = t_mobile.strip()
    code = code.strip()
    data = {
        "func_name": "SetMobileTicketV2",
        "func_args": {"mobile": str(mobile), "key": _key, "verifycode": str(code), "idc": IDC[t_idc]}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def set_smsup(mobile, idc, prefix="zc"):
    """
    设置申述流程或者注册流程能通过短信上行验证
    没限制使用的手机号，调用成功返回0
    根据申述号码属于不同的idc,填写对应的idc 名称，如：shanghai, shenzhen, hk, camel
    申诉上行短信场景使用 prefix="zm", prefix="ap" 需分别调用一次
    注册上行短信场景使用 prefix="zc"
    eg: set_smsup('13250259748', "shanghai", prefix="zm")

    :param mobile:
    :param idc:
    :param prefix:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    IDC = {'shanghai': 1, 'shenzhen': 3, 'hk': 2, 'camel': 8}
    lifetime = 3600
    data = {
        "func_name": "SetSmsUpTicket",
        "func_args": {"mobile": str(mobile), "idc": IDC[idc], "ExpiredTime": lifetime, "prefix": prefix}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(res.json())
    return res.json().get('rtn')


# ————————————————————————— 绑定关系查询/修改 用户名/uin查询  密码设置/清除 ————————————————————————


def SetBindMobile(user, mobile):
    """
    对指定微信号绑定或者解绑手机，如果是解绑直接为空串""
    只允许对319段测试号码操作，执行成功返回 0
    该手机之前已经有绑定关系的，请先用unbind_mobile(mobile)解除绑定，再执行绑定，否则操作会失败
    eg:SetBindMobile("autotest_mmtools_sh","")
        :param user:
    :param mobile:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    user = user.strip()
    mobile = str(mobile)
    data = {
        "func_name": "SetBindMobile",
        "func_args": {"username": user, "bindmobile": mobile}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def SetBindUin(user, qq):
    """
    对指定微信号绑定或者解绑QQ，如果是解绑直接写0
    只允许对319段测试号码操作，执行成功返回 0
    该QQ之前已经有绑定关系的，请先用unbind_QQ(qq)解除绑定，再执行绑定，否则操作会失败
    eg:SetBindUin("autotest_mmtools_sh",0)

    :param user:
    :param qq:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    user = user.strip()
    binduin = int(qq)
    data = {
        "func_name": "SetBindUin",
        "func_args": {"username": user, "binduin": binduin}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def SetBindEmail(user, email):
    """
    对指定微信号绑定或者解绑邮箱，如果解绑直接为空串""
    只允许对319段测试号码操作，执行成功返回 0
    该邮箱之前已经有绑定关系的，请先用unbind_email(email)解除绑定，再执行绑定，否则操作会失败
    eg:SetBindEmail("autotest_mmtools_sh","88883446@qq.com")

    :param user:
    :param email:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    user = user.strip()
    email = email.strip()
    data = {
        'func_name': 'SetBindEmail',
        'func_args': {"username": user, "bindemail": email}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(data)
    logger.info(res.json())
    return res.json().get('rtn')


def SetUnbind_facebook(username):
    """
    对指定微信号解绑facebook
    只允许319段测试号码操作，成功返回0
    eg:SetUnbind_facebook("autotest_mmtools_sh")

    :param username:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        "func_name": "UnBindFaceBook",
        "func_args": {"username": username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    return res.json().get('rtn')


def GetMobileUserinfo(mobile):
    """
    查询手机号是否有绑定微信
    查询操作不限于测试号段,返回str(uin)，如果没绑定返回为0
    eg: GetMobileUserinfo("13250259748")

    :param mobile:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUinByAttr',
        'func_args': {"type": 3, "attr": str(mobile)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    ret = res.json()
    usruin = 0
    if ret['rtn'] == 0:
        usruin = ret['data']['attruin']
        if usruin == 'Attr Not Exist':
            usruin = 0
    return usruin


def GetQQUserinfo(qq):
    """
    查询QQ号是否有绑定微信
    查询操作不限于测试号段，返回str(uin)，如果没绑定返回为0
    eg: GetQQUserinfo("122213332")

    :param qq:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUinByAttr',
        'func_args': {"type": 2, "attr": str(qq)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    ret = res.json()
    usruin = 0
    if ret['rtn'] == 0:
        usruin = ret['data']['attruin']
        if usruin == 'Attr Not Exist':
            usruin = 0
    return usruin


def GetEmailUserinfo(email):
    """
    查询邮箱是否绑定微信
    查询操作不限于测试号段，返回str(uin)，如果没绑定返回为0
    eg: GetEmailUserinfo("88883446@qq.com")

    :param email:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUinByAttr',
        'func_args': {"type": 4, "attr": str(email)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    ret = res.json()
    logger.info(data)
    logger.info(res.json())
    usruin = 0
    if ret['rtn'] == 0:
        usruin = ret['data']['attruin']
        if usruin == 'Attr Not Exist':
            usruin = 0
    return usruin


def unbind_mobile(iphone_num):
    """
    解绑手机号（手机没绑定也可以执行，返回0）
    绑定用户为非319段不能解绑 返回 -1 表示解绑失败，返回0表现成功解绑
    eg: unbind_mobile("13250259748")

    :param iphone_num:
    :return:
    """
    uin = GetMobileUserinfo(iphone_num)
    uin = str(uin)
    rtn = 0
    if uin != "0":  # 有绑定关系
        if str(uin)[0:3] != "319":
            # print("非319不是测试号码不能解绑")
            logger.info("非319不是测试号码不能解绑")
            rtn = -1
        else:
            # 解绑手机
            user = GetUsername(str(uin))
            rtn = SetBindMobile(user, "")
    return rtn


def unbind_QQ(qq_num):
    """
    解绑QQ号（QQ没绑定也可以执行，返回0）
    绑定用户为非319段不能解绑 返回 -1 表示解绑失败，返回0表现成功解绑
    eg: unbind_qq("122213332")

    :param qq_num:
    :return:
    """
    uin = GetQQUserinfo(qq_num)
    uin = str(uin)
    rtn = 0
    if uin != "0":  # 有绑定关系
        if str(uin)[0:3] != "319":
            # print("非319不是测试号码不能解绑")
            logger.info("非319不是测试号码不能解绑")
            rtn = -1
        else:
            # 解绑QQ
            user = GetUsername(str(uin))
            rtn = SetBindUin(user, 0)
    return rtn


def unbind_email(email):
    """
    解绑邮箱 （QQ没绑定也可以执行，返回0）
    绑定用户为非319段不能解绑 返回 -1 表示解绑失败，返回0表现成功解绑
    eg: unbind_email("122213332@qq.com")

    :param email:
    :return:
    """
    uin = GetEmailUserinfo(email)
    uin = str(uin)
    rtn = 0
    if uin != "0":  # 有绑定关系
        if str(uin)[0:3] != "319":
            # print("非319不是测试号码不能解绑")
            logger.info("非319不是测试号码不能解绑")
            rtn = -1
        else:
            # 解绑邮箱
            user = GetUsername(str(uin))
            rtn = SetBindEmail(user, "")
    return rtn


g_uin_cache = {}


def get_uin(username):
    """
    反查微信号或者微信别名对应的uin
    不限号码使用，返回uin，找不到返回0
    eg:get_uin("autotest_mmtools_sh")

    :param username:
    :return:
    """
    if username in g_uin_cache:
        return g_uin_cache[username]
    url = "http://%s/mmcasehelpershanghai/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUserByUsername',
        'func_args': {'username': username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    uin = res.json().get('data').get('user_uin')
    if len(g_uin_cache) < 1024:
        g_uin_cache[username] = uin
    return uin


def GetUin(username):
    """
    反查微信号或别名对应的uin，跟get_uin()功能一样
    不限号码使用，返回uin，如果不存在返回为0,
    eg:GetUin("autotest_mmtools_sh")

    :param username:
    :return:
    """
    return get_uin(username)
    # url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    # data = {
    #     'func_name': 'GetUinByAttr',
    #     'func_args': {"type": 1, "attr": username}
    # }
    # res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # ret = res.json()
    # usruin = 0
    # if ret['rtn'] == 0:
    #     usruin = ret['data']['attruin']
    #     if usruin == 'Attr Not Exist':
    #         usruin = 0
    # return usruin


def GetUserInfo(uin):
    """
    用uin反查username(微信名） 和 aliasname（别名）
    不限号码使用，有aliasname的时候优先返回,否则返回username,查不到返回空串
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
    return ret['data']


def get_user_accid(username, appuin=2391140741):
    """
    获取用户的accid

    :param username:
    :param appuin:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    user_uin = get_uin(username)
    data = {
        'func_name': 'GetOuterAcctId',
        'func_args': {'user_uin': user_uin, 'appuin': appuin}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    logger.info(result)
    data = result.get('data')
    rtn = result.get('rtn')
    msg = result.get('msg')
    if rtn == 0:
        return data.get('OpenId')
    else:
        return msg


def GetFBBindUin(fbuserid):
    """
    通过FBUserID来反查绑定的微信uin
    成功返回uin, 没绑定关系返回0
    eg: GetFBBindUin(100001418780183)

    user_uin :做路由uin用
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetFBBindUin',
        'func_args': {"user_uin": 3192000002, "fbuserid": int(fbuserid)}
    }

    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    info = result['data']
    return info['fbbinduin']


def clearPasswd(username):
    """
    清空微信独立密码
    仅限SH IDC 319测试号段使用 , 成功返回0
    eg: clearPasswd("autotest_mmtools_sh")

    :param username:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmaccount"   #这个不限idc使用
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    username = username.strip()
    data = {
        "func_name": "CleanUserPassword",
        "func_args": {"username": username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['rtn']


def set_user_password(username, new_password):
    """
    设置微信独立密码
    仅限SH IDC 319测试号段使用 , 成功返回0
    eg: set_user_password("autotest_mmtools_sh"，"test1234")

    :param username:
    :param new_password:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SetPassword',
        'func_args': {'username': username, "password": new_password}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['rtn']


def GetAlias(username):
    """
    用username反查aliasname
    不限号码使用，查不到返回-1
    eg: GetAlias("test_sh01")
    :param username:
    :return:
    """
    uin = get_uin(username)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetTestUserInfo',
        'func_args': {'checkname': str(uin)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    ret = res.json()
    if ret['rtn'] == 0:
        usr = ret['data']['alias']
        return usr
    else:
        return -1


def set_alias(username, new_alias):
    """
    设置微信别名
    仅限SH IDC 319测试号段使用 , 成功返回0
    eg: set_alias("wxid*******", "yunwuxin_sh_9988")

    :param username:
    :param new_alias:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmaccount"   #这个不限idc使用
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SetAlias',
        'func_args': {'username': username, "alias": new_alias}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['rtn']


def GetUsername(uin):
    """
    用uin反查username
    不限号码使用，查不到返回-1 （不返回aliasname）
    eg: GetUsername("100014")

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
    if ret['rtn'] == 0:
        usr = ret['data']['username']
        alias = ret['data']['alias']
        if alias == "":
            return usr
        else:
            return alias
    else:
        return -1


def set_user_name(user_uin, new_username):
    """
    不要用，会删掉微信号的，最好不要用！！！！

    :param user_uin:
    :param new_username:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SetUsername',
        'func_args': {'user_uin': user_uin, "setname": new_username}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())


# -------------------------------- 下发XML消息 ---------------------------------

def SendXML(username, filename='1.xml.txt', type=10002):
    """
    给测试号码推送xml，限制在测试319号段， 发送成功返回 0
    eg: SendXML("autotest_mmtools_sh", filename="7.xml.txt")
    xml的文件放在和mmtools目录平级的resource目录的下级目录xml中
    msg_type默认为10002,下发xml的时候使用默认值。

    :param username:
    :param filename:
    :param type:
    :return:
    """
    """type  默认下发1.xml.txt 全局弹窗
        1.xml.txt    resource/xml 下面的1.xml.txt 全局弹窗，各种btn都有
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR

    res_path = os.path.join(RES_PATH, 'xml')
    file = os.path.join(res_path, filename)
    with open(file, 'r') as f:
        content = f.read()
    data = {
        'func_name': 'SendMsg',
        'func_args':
            {
                'username': username,
                'tousername': username,
                "content": util.MMGBK2UTF8(content),
                "type": int(type),
                "number": 1
            }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['rtn']


def Sendipxx(username, xml):
    """
    给测试号码推送ipxx
    限制在测试319号段， 发送成功返回0
    eg: Sendipxx("autotest_mmtools_sh", xml)

    :param username:
    :param xml:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'SendMsg',
        'func_args':
            {
                'username': username,
                'tousername': username,
                "content": xml,
                "type": 9998,
                "number": 1
            }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)

    return res.json()['rtn']


# ------------------------------------- 收、发消息：群聊，单聊 ----------------------------------

def getallmicromsg(username, last_num=10):
    """
    获取index最新消息
    只能供上海 idc，且为319测试号段的号码使用，其他号码使用拿不到数据
    如果要查询其他idc 的数据，只能使用 mmcasehelperidc
    eg: getallmicromsg("autotest_mmtools_sh", last_num=10)

    :param username:
    :param last_num:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmindex"     # 所有idc
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'GetAllMicromsg',
        'func_args': {'username': username, 'last_num': last_num}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()


def send_1to1_msg(msg_from, msg_to, msg_type, num=1):
    """
    发送1对1消息,允许指定消息类型，消息数量
    限制发送号码只能为319测试号段且IDC为上海的号码使用，成功返回0
    eg:send_1to1_msg("rdgztest_atm1","autotest_mmtools_sh", 0, 5)

    :param msg_from: 发送微信号
    :param msg_to: 接收微信号
    :param msg_type: 消息类型
        0 随机
        1 文本
        3 图片
        33 小程序
        34 audio
        44 video
        48 location
        47 emoji
        496 appmsg
        497 music link
        498 file

    :param num:
    :return:
    """
    uin = get_uin(msg_from)
    msg_type = int(msg_type)
    num = int(num)
    if msg_to.find("@chatroom") == -1:
        flag = add_friend(msg_from, msg_to)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4

        if int(msg_type) == 3:  # 如果选发送图片类型的消息，使用本地资源库，图片可以展示不会过期
            for i in range(0, int(num)):
                j = random.randint(1, 8)
                # flag=send_1to1_pic(msg_from, msg_to, '%s.jpg'%j)
                # url = "http://%s/mmcasehelperidc/mmindex"    #所有IDC
                url = "http://%s/mmcasehelperclient/mmindex" % CASE_SVR
                res_path = os.path.join(RES_PATH, "pic", '%s.jpg' % j)
                buffer = util.file_2_int_buffer(res_path)
                data = {
                    'func_name': 'SendImgv2',
                    'func_args': {'fromusername': msg_from, 'tousername': msg_to, 'buffer': buffer}
                }
                # logger.info(data)
                res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
                flag = res.json().get('rtn')
                if flag != 0:
                    logger.info("send pic fail!")
                    break
            return flag

        if int(msg_type) == 44:  # 如果选发送视频类型的消息，使用本地资源库，视频可以展示不会过期
            for i in range(0, int(num)):
                j = random.randint(1, 2)
                flag = send_1to1_video(msg_from, msg_to, '%s.mp4' % j)
                if flag != 0:
                    logger.info("send video fail!")
                    break
            return flag

    url = 'http://%s/mmcasehelperidc/mmindex' % CASE_SVR
    remain_num = num
    while True:
        if remain_num > 10:
            data = {
                'func_name': 'sendmsg',
                'func_args': {
                    'user_uin': uin,
                    'tousername': msg_to,
                    'type': msg_type,
                    'number': 10
                }
            }
            remain_num = remain_num - 10
            util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
        else:
            data = {
                'func_name': 'sendmsg',
                'func_args': {
                    'user_uin': uin,
                    'tousername': msg_to,
                    'type': msg_type,
                    'number': remain_num
                }
            }
            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
            break
    return res.json().get('rtn')


def send_1to1_pic_by_path(from_username, to_username, res_path):
    """
    发送不过期图片，已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用,发送成功返回0
    图片为放在和mmtools目录平级的resource目录的下级pic目录中
    eg: send_1to1_pic("autotest_mmtools_sh", "rdgztest_atm1", pic="1.jpg")

    :param from_username:
    :param to_username:
    :param res_path:
    :return:
    """
    # 发送前先互加好友,群聊不用加
    if to_username.find("@chatroom") == -1:
        flag = add_friend(from_username, to_username)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4
    else:
        # print("不支持发这种类型的群聊消息，请选择其他消息类型")
        logger.info("Error：不支持发这种类型的群聊消息，请选择其他消息类型")
        return -1
    # url = "http://%s/mmcasehelperidc/mmindex"    #所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR

    buffer = util.file_2_int_buffer(res_path)
    data = {
        'func_name': 'SendImgv2',
        'func_args': {'fromusername': from_username, 'tousername': to_username, 'buffer': buffer}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def send_1to1_pic(from_username, to_username, pic="1.jpg"):
    """
    发送不过期图片，已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用,发送成功返回0
    图片为放在和mmtools目录平级的resource目录的下级pic目录中
    eg: send_1to1_pic("autotest_mmtools_sh", "rdgztest_atm1", pic="1.jpg")

    :param from_username:
    :param to_username:
    :param pic:
    :return:
    """
    res_path = os.path.join(RES_PATH, "pic", pic)
    send_1to1_pic_by_path(from_username, to_username, res_path)


def send_1to1_gif(from_username, to_username, pic="1.gif"):
    """
    发送不过期的GIF图片，已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用,发送成功返回0
    图片为放在和mmtools目录平级的resource目录的下级pic目录中
    eg: send_1to1_gif("autotest_mmtools_sh", "rdgztest_atm1", pic="1.gif")

    :param from_username:
    :param to_username:
    :param pic:
    :return:
    """
    # 发送前先互加好友,群聊不用加
    if to_username.find("@chatroom") == -1:
        flag = add_friend(from_username, to_username)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4
    # url = "http://%s/mmcasehelperidc/mmindex"    #所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    res_path = os.path.join(RES_PATH, "pic", pic)
    buffer = util.file_2_int_buffer(res_path)
    with open(res_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        md5str = md5obj.hexdigest()
    data = {
        'func_name': 'SendEmojiv2',
        'func_args': {'fromusername': from_username, 'tousername': to_username, 'buffer': buffer, "md5": md5str}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def send_1to1_video(from_username, to_username, video="1.mp4"):
    """
    发送不过期的视频,已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用,发送成功返回0
    图片为放在和工具mmtools目录平级的resource目录的下级video目录中
    eg: send_1to1_video("autotest_mmtools_sh", "rdgztest_atm1", video="1.mp4")

    :param from_username:
    :param to_username:
    :param video:
    :return:
    """
    # 发送前先互加好友,群聊不用加
    if to_username.find("@chatroom") == -1:
        flag = add_friend(from_username, to_username)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4
    else:
        # print("不支持发这种类型的群聊消息，请选择其他消息类型")
        logger.info("Error：不支持发这种类型的群聊消息，请选择其他消息类型")
        return -1
    # url = "http://%s/mmcasehelperidc/mmindex"       #所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    res_path = os.path.join(RES_PATH, "video", video)
    buffer = util.file_2_int_buffer(res_path)
    data = {
        'func_name': 'SendVideov2',
        'func_args': {'fromusername': from_username, 'tousername': to_username, 'buffer': buffer}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def send_1to1_voice(from_username, to_username, voice="0.silk"):
    """
    发送1对1语音消息,已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用，发送成功返回0
    声音文件放在和工具mmtools目录平级的resource目录的下级voice目录中
    eg: send_1to1_voice("autotest_mmtools_sh", "rdgztest_atm1",voice="1.aud")

    :param from_username:
    :param to_username:
    :param voice:
    :return:
    """
    # 发送前先互加好友,群聊不用加
    if to_username.find("@chatroom") == -1:
        flag = add_friend(from_username, to_username)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4
    # url = "http://%s/mmcasehelperidc/mmindex"       #所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    res_path = os.path.join(RES_PATH, "voice", voice)
    buffer = util.file_2_int_buffer(res_path)
    data = {
        'func_name': 'SendVoicev2',
        'func_args': {'username': from_username, 'tousername': to_username, 'buffer': buffer}
    }
    # logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def send_1to1_msg_with_content(from_username, to_username, content):
    """
    发送1对1指定文字消息,已经预处理先互加好友再发消息
    限制发送号码只能为319测试号段且IDC为上海的号码使用，发送成功返回0
    eg: send_1to1_msg_with_content("autotest_mmtools_sh", "rdgztest_atm1", "测试文字")

    :param from_username:
    :param to_username:
    :param content:
    :return:
    """
    if to_username.find("@chatroom") == -1:
        flag = new_add_friend(from_username, to_username)
        if flag != 0:
            # print("非测试号码不能操作")
            logger.info("No test account!")
            return -4
    uin = get_uin(from_username)
    # url = "http://%s/mmcasehelperidc/mmindex"       #所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'sendmsg',
        'func_args': {'user_uin': uin, 'tousername': to_username, 'type': 1, 'number': 1, 'content': content}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.url)
    logger.info(res.json())
    return res.json().get('rtn')


def send_nto1_msg(start_num, send_num, to_username, type, num):
    """
    发送n对1消息,消息类型可定义可随机
    发送消息测试号码从测试号码池中选出： rdgztest_atm1 -rdgztest_atm9999
    接收消息的用户限制只为319测试号段，发送成功返回0
    eg:send_nto1_msg(1000, 8, "autotest_mmtools_sh", 0, 5) # 从rdgztest_atm1000-rdgztest_atm1007 发出消息

    :param start_num:
    :param send_num:
    :param to_username:
    :param type:
    :param num:
    :return:
    """
    # url = "http://%s/mmtools/sendntoonemsg"
    # data = {
    #     "start": start_num,
    #     "from": send_num,
    #     "to": to,
    #     "send_type": type,
    #     "num": num
    # }
    # res = util.retry_get(url, params=data, retry_count=RETRY)
    if int(start_num) == 0 or int(send_num) == 0:
        # print("error: 开始值start_num和步长值send_num都需要大于0")
        return -1
    i = 0
    flag = 0
    while i < int(send_num):
        from_username = "rdgztest_atm" + str(int(start_num) + i)
        flag = send_1to1_msg(from_username, to_username, type, num)
        i = i + 1
        if flag != 0:
            break
    return flag


def send_chatroom_msg(msg_from, chatroom, type, num):
    """
     指定微信号往测试群聊里面里面塞消息
     可以使用工具set_test_chatroom(username,chatroomid),把普通群聊设置为测试群
     限制发送号码只能为319测试号段且IDC为上海的号码使用，发送成功返回0
     eg:send_chatroom_msg("autotest_mmtools_sh","12105179502@chatroom",0,5)

    :param msg_from:
    :param chatroom:
    :param type:
    :param num:
    :return:
    """
    rtn = send_1to1_msg(msg_from, chatroom, type, num)
    return rtn


def mass_send_chatroom_msg(chatroomid, num, msg_type=0):
    """
    往特定测试群发送n条群聊消息，消息类型可定义可随机
    可以使用工具set_test_chatroom(username,chatroomid),把普通群聊设置为测试群，使用工具发送群聊消息
    但群里面如果没有包含至少一个 rdgztest_atm1~rdgztest_atm9999 的测试号，会导致工具执行出错。工具执行成功会返回0
    eg:mass_send_chatroom_msg(16403917850,15)

    :param chatroomid:
    :param num:
    :param msg_type:
    :return:
    """
    # url = "http://%s/mmtools/masssendchatroommsg"
    # data = {
    #     "to": chatroom_id,
    #     "send_type": msg_type,
    #     "num": num }
    chatroom = str(chatroomid) + "@chatroom"
    remain_num = num
    url = 'http://%s/mmcasehelperidc/mmindex' % CASE_SVR
    while True:
        if remain_num > 10:
            data = {
                'func_name': 'sendmsg',
                'func_args': {
                    # 'user_uin': 0,
                    'tousername': chatroom,
                    'type': int(msg_type),
                    'number': 10
                }
            }
            remain_num = remain_num - 10
            util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
        else:
            data = {
                'func_name': 'sendmsg',
                'func_args': {
                    # 'user_uin': 0,
                    'tousername': chatroom,
                    'type': int(msg_type),
                    'number': remain_num
                }
            }
            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
            break
    logger.info(res.json())
    # print((res.json()))
    return res.json().get('rtn')


def send_verify_msg(tousername, num):
    """
    发送num条新的好友验证信息
    仅限为测试319号段使用，不限idc,返回0表示发送成功
    eg:  send_verify_msg("autotest_mmtools_sh", 2)

    :param tousername:
    :param num:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'SendntestVerifyMsg',
        'func_args': {"tousername": tousername, "number": num}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def sendappmsg(fromusername, tousername, filename, title, apptype=1):
    """
    发送任意类型的本地文件
    成功返回 0，仅限319段测试号使用
    eg: sendappmsg("autotest_mmtools_sh", "yunwuxin_sh_001", "/Users/coolliang/Downloads/test333.doc", "3.doc")
    buff_data 为文件的全路径
    title为文件名（要带后缀名）
    :param fromusername: 发送的微信号
    :param tousername:  接受的微信号
    :param filename:    文件路径
    :param title:   文件名
    :param apptype: 文件类型
    :return:
    """
    buff = MMGetFileContent(filename)
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    uin = get_uin(fromusername)
    data = {
        "func_name": "SendAppMsg",
        "func_args": {"user_uin": uin, "tousername": tousername, "buffer": buff, "title": title,
                      "apptype": int(apptype)}
    }
    # # print len(buff)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.url)
    logger.info(res.json())
    # print(res.json())
    return res.json().get('rtn')


def MMGetFileContent(filename):
    dataList = []
    if not os.path.exists(filename):
        # print(("ERROR: file not exit: %s" % (filename)))
        return dataList
    if not os.path.isfile(filename):
        # print(("ERROR: %s not a filename." % (filename)))
        return dataList
    f = open(filename, "rb")
    content = f.read()

    for byte in content:
        temp = ord(byte)
        dataList.append(temp)
    f.close()
    return dataList


def MMGetFileContent1(filename):
    imgStr = []
    with open(filename, 'rb') as f:
        while 1:
            byte_s = f.read(1)
            if not byte_s:
                break
            byte = byte_s[0]
            byte2 = '{0:08b}'.format(ord(byte))
            byte10 = int(byte2, 2)
            imgStr.append(byte10)
    # print((len(imgStr)))


# -------------------------------------- 好友关系 ----------------------------------------

def relationship(username, friendname):
    """
    比较2个微信号之间的相互关系：只给出陌生人，好友，单向好友，黑名单这几种关系
    仅限sh ,sz IDC 的319段测试号码使用。陌生人返回1，双向好友返回2，单向好友返回3，黑名单返回4或5
    eg: relationship("autotest_mmtools_sh", "rdgztest_atm1")

    :param username:
    :param friendname:
    :return:
    """
    Type = get_simple_contact(username, friendname, 0)
    _Type = get_simple_contact(friendname, username, 0)
    ralation = 0
    a = CompareContact(username, friendname, Type)
    b = CompareContact(friendname, username, _Type)
    if a == 1 and b == 1:
        # print("两个人没好友关系")
        ralation = 1
    if a == 2 and b == 2:
        # print("两个人为双向好友关系")
        ralation = 2
    if (a == 1 and b == 2) or (a == 2 and b == 1):
        # print("两者为单向好友关系")
        ralation = 3
    if a == 3:
        # print((friendname + "在" + username + "黑名单内"))
        ralation = 4
    if b == 3:
        # print((username + "在" + friendname + "黑名单内"))
        ralation = 5
    return ralation


def CompareContact(username, friendname, Type):
    """
    微信号正向表内容（供relationship调用）

    :param username:
    :param friendname:
    :param Type:
    :return:
    """

    MM_CONTACTFLAG_NONE = -1
    MM_CONTACTFLAG_CONTACT = 0x01
    MM_CONTACTFLAG_CHATCONTACT = 0x02
    MM_CONTACTFLAG_CHATROOMCONTACT = 0x04
    MM_CONTACTFLAG_BLACKLISTCONTACT = 0x08  # 黑名单
    MM_CONTACTFLAG_DOMAINCONTACT = 0x10
    MM_CONTACTFLAG_HIDECONTACT = 0x20
    MM_CONTACTFLAG_FAVOURCONTACT = 0x40  # 星标好友
    MM_CONTACTFLAG_3RDAPPCONTACT = 0x80
    MM_CONTACTFLAG_SNSBLACKLISTCONTACT = 0x100  # 不让看我朋友圈（朋友圈黑名单）
    MM_CONTACTFLAG_MUTECONTACT = 0x200  # 会话静默
    MM_CONTACTFLAG_UNDELIVERCONTACT = 0x400
    MM_CONTACTFLAG_TOP = 0x800  # 会话置顶
    MM_CONTACTFLAG_AUTOADD = 0x1000
    MM_CONTACTFLAG_SNSNOTSEE = 0x10000  # 不看对方朋友圈
    MM_CONTACTFLAG_TEXTTRANSLATE = 0x2000
    MM_CONTACTFLAG_FROZEN = 0x4000
    # MM_CONTACTFLAG_ALL = 0xffffffff
    # 剔除其他 ContactFlag
    if Type > 0:
        Type &= ~MM_CONTACTFLAG_CHATROOMCONTACT
        Type &= ~MM_CONTACTFLAG_DOMAINCONTACT
        Type &= ~MM_CONTACTFLAG_HIDECONTACT
        Type &= ~MM_CONTACTFLAG_FAVOURCONTACT
        Type &= ~MM_CONTACTFLAG_3RDAPPCONTACT
        Type &= ~MM_CONTACTFLAG_SNSBLACKLISTCONTACT
        Type &= ~MM_CONTACTFLAG_MUTECONTACT
        Type &= ~MM_CONTACTFLAG_UNDELIVERCONTACT
        Type &= ~MM_CONTACTFLAG_TOP
        Type &= ~MM_CONTACTFLAG_AUTOADD
        Type &= ~MM_CONTACTFLAG_SNSNOTSEE
        Type &= ~MM_CONTACTFLAG_TEXTTRANSLATE
        Type &= ~MM_CONTACTFLAG_FROZEN
    AandB = 0

    if Type == 0 or Type == -1 or Type == 2:
        _str = friendname + " is not Friend of " + username
        ColorLog(_str, "red")
        AandB = 1
    if Type == 1 or Type == 3:
        _str = friendname + " is Friend of " + username
        ColorLog(_str, "green")
        AandB = 2
    if Type == 8 or Type == 10:
        _str = friendname + "is in " + username + "'s BlackList "
        ColorLog(_str, "blue")
        AandB = 3
    if Type == 9 or Type == 11:
        _str = friendname + " is Friend of " + username + ", but in " + username + "'s BlackList"
        ColorLog(_str, "blue")
        AandB = 3

    return AandB


def add_friend(username, friendname):
    """
    添加双向好友 ，只需要调用一次
    可以跨 IDC使用,限制在 319测试号段,成功添加好友返回0
    eg: add_friend("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friendname:
    :return:
    """
    url = 'http://%s/mmcasehelperidc/mmaddrbook' % CASE_SVR
    data = {
        'func_name': 'addfriend',
        'func_args': {'username': username, 'friend': friendname}}
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    v1 = res.json().get('rtn')
    data = {
        'func_name': 'addfriend',
        'func_args': {'username': friendname, 'friend': username}}
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    v2 = res.json().get('rtn')
    if v1 == 0 and v2 == 0:
        logger.info(username + "成功添加好友" + friendname)
        return 0
    else:
        logger.error(username + "添加双向好友" + friendname + "失败")
        return -1


def addNfriends(username, start_num=100, number=10):
    """
    添加 n个好友, 测试号码池从 rdgztest_atm1 -rdgztest_atm9999
    start_num => rdgztest_atm100为初始值,偏移量为start_num,如50 则从rdgztest_atm100开始添加50个好友
    可以跨 IDC使用,限制在 319测试号段,成功添加 n 个好友返回0
    eg:  addNfriends("autotest_mmtools_sh",100,50)

    :param username:
    :param start_num:
    :param number:
    :return:
    """
    if start_num == 0:
        # print("Error：不能从0开始添加，至少要从1开始")
        return -1
    else:
        start_num = int(start_num)
        number = int(number)
        i = 0
        while i < number:
            rtn = add_friend(username, "rdgztest_atm" + str(i + start_num))
            i = i + 1
            if rtn != 0:
                # print("添加好友失败，终止继续添加，请检查操作的号码是否为符合条件的测试号码")
                return rtn
        return 0


def add_simple_friend(username, friend):
    """
    添加单向好友
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    add_simple_friend("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag = set_contact(username, friend, 0, 3)
    if flag == 0:
        return 0
    else:
        return -1


def new_add_friend(username, friendname):
    """
    添加双向好友 ，只需要调用一次
    可以跨IDC使用,支持新加坡,限制在 319测试号段,成功添加好友返回0
    eg: new_add_friend("autotest_mmtools_sh","rdgztest_atm1")
    :param username:
    :param friendname:
    :return:
    """
    v1 = set_simple_contact(username, friendname, 0, 3)
    v2 = set_simple_contact(friendname, username, 0, 3)
    if v1 == 0 and v2 == 0:
        logger.info(username + "成功添加好友" + friendname)
        return 0
    else:
        logger.error(username + "添加双向好友" + friendname + "失败")
        return -1


def set_block(username, friend):
    """
    设置黑名单 username将friend添加到黑名单中
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    set_block("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """

    flag = set_contact(username, friend, 0, 11)
    if flag == 0:
        return 0
    else:
        return -1


def undo_block(username, friend):
    """
    取消设置黑名单
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    undo_block("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag = set_contact(username, friend, 0, 3)
    if flag == 0:
        return 0
    else:
        return -1


def set_chatonly(username, friend):
    """
    设置仅聊天好友 username将friend设置为仅聊天好友
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    set_block("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """

    flag = set_contact(username, friend, 0, 0x800003)
    if flag == 0:
        return 0
    else:
        return -1


def unset_chatonly(username, friend):
    """
    恢复正常好友 username将friend设置为恢复正常好友
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    set_block("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """

    flag = set_contact(username, friend, 0, 0x3)
    if flag == 0:
        return 0
    else:
        return -1


def set_contact(username, to_username, contacttype, type):
    """
    设置通讯录标志位(设置自己的正向表，对方的反向表)
    仅限319测试号段使用，支持sh,sz idc(hk idc不支持),成功返回0
    eg:set_contact("autotest_mmtools_sh","rdgztest_atm1",0,3)

    :param username:
    :param to_username:
    :param contacttype:
    :param type: 参考 CompareContact 里面的定义
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    data = {
        'func_name': 'setcontact',
        'func_args': {'username': username, 'tousername': to_username, 'contacttype': contacttype, 'type': type}
    }
    # logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def get_simple_contact(username, to_username, contacttype):
    """
    读取通讯录正向表标志位
    仅限 SH ,SZ IDC 319测试号段使用，成功返回标志位
    eg: get_simple_contact("autotest_mmtools_sh","rdgztest_atm1",0)
    type 的定义请参考 CompareContact 里面的定义
    如果对群聊操作，to_username已经先用工具加为测试群，以防出错
    eg: get_simple_contact("autotest_mmtools_sh", "11799220724@chatroom", 2)

    :param username:
    :param to_username:
    :param contacttype:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    if to_username.find("@chatroom") > 0:
        set_test_chatroom(username, to_username[:-9])
    user_uin = int(get_uin(username))
    touser_uin = int(get_uin(to_username))
    data = {
        'func_name': 'GetSimpleContact',
        'func_args': {'user_uin': user_uin, 'touser_uin': touser_uin, 'contacttype': contacttype}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['data']['Type']


def set_simple_contact(username, to_username, contacttype, type):
    """
    设置通讯录正向表标志位（只设置自己的正向表，不写反向表）
    不限319测试号段，所有idc 都可以使用，使用成功返回0
    eg:set_simple_contact("autotest_mmtools_sh","rdgztest_atm1",0，3)
    type 的定义请参考 CompareContact 里面的定义
    :param username:
    :param to_username:
    :param contacttype: 群聊 contacttype 为2 ，单个微信号为0
    :param type:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    user_uin = int(get_uin(username))
    if to_username.endswith("chatroom"):
        touser_uin = int(to_username.split('@')[0])
    else:
        touser_uin = int(get_uin(to_username))
    data = {
        'func_name': 'SetSimpleContact',
        'func_args': {'user_uin': user_uin, 'touser_uin': touser_uin, 'contacttype': contacttype, 'type': type}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(res.json())
    return res.json()['rtn']


def ColorLog(_string, color):
    """
    染色打印
    :param _string:
    :param color:
    :return:
    """
    redFmt, grnFmt, yelFmt, bluFmt, pikFmt, ltgrnFmt = ('\033[1;31m%s\033[m', '\033[1;32m%s\033[m',
                                                        '\033[1;33m%s\033[m', '\033[1;34m%s\033[m',
                                                        '\033[1;35m%s\033[m', '\033[1;36m%s\033[m')

    colorDic = {"red": redFmt, "green": grnFmt, "yellow": yelFmt, "blue": bluFmt, "pink": pikFmt,
                "lightgreen": ltgrnFmt, "": '"\\033[1;29m%s\\033[m"'}

    # print((colorDic[color] % _string))


# ———————————————————————————---———— 通讯录 ————————————————————————————————————


def get_all_contacts(username, contact_type=0):
    """
    获取通讯录所有联系人列表
    仅限319测试号段使用，不限IDC ,返回通讯录的好友数据，执行出错返回None
    eg: get_all_contacts("autotest_mmtools_sh")

    :param username:
    :param contact_type: 0是好友，2是群聊
    :return:
    """
    uin = get_uin(username)
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    send_data = {'func_name': "GetAllSimpleContact", "func_args": {"user_uin": uin, "contact_type": contact_type}}
    res = util.mmtools_post(url, data=json.dumps(send_data), retry_count=RETRY)
    contact_data = res.json()
    if contact_data.get('rtn') < 0:
        return None
    _data = contact_data['data']['contact_vec']
    return _data


def set_remark(username, to_username, remark):
    """
    设置或者清理通讯录备注，清理备注的时候，写成""
    username仅限319段测试号码使用,IDC不限制，to_username没限制，执行成功返回0
    eg: set_remark("autotest_mmtools_sh","rdgztest_atm1","这是备注")

    :param username:
    :param to_username:
    :param remark:
    :return:
    """
    uin = get_uin(username)
    to_uin = get_uin(to_username)
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    data = {
        'func_name': 'SetContactRemark',
        'func_args': {'user_uin': uin, 'touser_uin': to_uin, 'remark': remark}
    }

    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def get_remark(uin, to_uin):
    """
    获取通讯录备注
    uin仅限319段测试号码使用,IDC不限制，执行成功返回0
    eg: get_remark(3191009616,3192010080)

    :param uin:
    :param to_uin:
    :return:
    """
    i_uin = int(uin)
    i_touin = int(to_uin)
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    data = {
        'func_name': 'GetContactRemark',
        'func_args': {'user_uin': i_uin, 'touser_uin': i_touin}
    }

    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('data').get('remark')


def set_fav_friend(username, to_username, flag=1):
    """
    设置或者去掉星标好友 : 默认是设置为1，去掉星标写0
    2个操作号码都要求是319段的测试号段，不限IDC ，执行成功返回0
    eg: set_fav_friend("autotest_mmtools_sh","rdgztest_atm1",1)

    :param username:
    :param to_username:
    :param flag:
    :return:
    """
    MM_CONTACTFLAG_FAVOURCONTACT = 0x40
    flag_1 = get_simple_contact(username, to_username, 0)
    if flag_1 == -1:
        # print("不是好友关系，无法去掉或者设置星标，请先设置好友关系")
        return -1
    else:
        a = flag_1 & MM_CONTACTFLAG_FAVOURCONTACT  # 如果a是64表示是星标，如果是0表示不是星标
        type = flag_1 | MM_CONTACTFLAG_FAVOURCONTACT
        type_1 = flag_1 & ~ MM_CONTACTFLAG_FAVOURCONTACT
    flag = int(flag)
    if flag == 1:  # 设置星标
        if a == 0:
            return set_simple_contact(username, to_username, 0, type)
        else:
            if a == MM_CONTACTFLAG_FAVOURCONTACT:
                # print("本来就是星标好友，无需设置")
                return 0

    if flag == 0:  # 去掉星标
        if a == MM_CONTACTFLAG_FAVOURCONTACT:
            return set_simple_contact(username, to_username, 0, type_1)
        else:
            if a == 0:
                # print("不是星标好友，无需去掉星标")
                return -1
    else:
        # print("参数错误")
        return -1


def del_all_favorite_friends(username):
    """
    取消通讯录所有好友星标
    只限319测试号段，所有idc 都可以使用, 全部执行成功取消星标好友返回0
    eg:del_all_favorite_friends("autotest_mmtools_sh")

    :param username:
    :return:
    """

    MM_CONTACTFLAG_FAVOURCONTACT = 0x40
    all_contacts = get_all_contacts(username)
    favourcontact = get_all_favorite(all_contacts)
    flag = 0
    for _fav in favourcontact:
        _type = _fav['type'] & ~MM_CONTACTFLAG_FAVOURCONTACT
        to_username = GetUsername(str(_fav['contactuin']))
        ret = set_simple_contact(username, to_username, _fav['contacttype'], _type)
        if ret:
            flag = -1
            break
    return flag


def get_all_favorite(contact_list):
    """
    过滤星标好友 (仅供 del_favorite_friend 调用）

    :param contact_list:
    :return:
    """
    MM_CONTACTFLAG_FAVOURCONTACT = 0x40
    _favourcontact = []
    for one in contact_list:
        if one['type'] & MM_CONTACTFLAG_FAVOURCONTACT and util.is_test_uin(one['contactuin']):
            _favourcontact.append(one)
    return _favourcontact


def get_contact_labels(username):
    """
    查询用户通讯录里所有的标签
    返回：dict，
    {"count":5,"label_list":[{"LabelID":1,"LabelName":"测试标签1561028201"}]}
    """
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    data = {'func_name': 'GetContactLabel',
            'func_args': {'username': username}
            }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('data')


def set_contact_label(username, label_id, label_name, version=0):
    """label_id
    """
    url = "http://%s/mmcasehelperidc/mmaddrbook" % CASE_SVR
    data = {'func_name': 'SetContactLabel',
            'func_args': {'username': username,
                           "label_id": int(label_id),
                           "label_name": label_name,
                           "version": version}
            }

    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')

# --------------------------------------- 朋友圈  -----------------------------


def hide_my_moments(username, friend):
    """
    设置不让他(她)看我的朋友圈
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    hide_my_moments("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag1 = set_contact(username, friend, 0, 259)
    flag2 = add_sns_tag(username, friend, 4)
    if flag1 == 0 and flag2 == 0:
        return 0
    else:
        return -1


def hide_friend_moments(username, friend):
    """
    设置不看他(她)的朋友圈
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    hide_friend_moments("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag1 = set_contact(username, friend, 0, 65539)
    flag2 = add_sns_tag(username, friend, 5)
    if flag1 == 0 and flag2 == 0:
        return 0
    else:
        return -1


def undo_hide_moments(username, friend):
    """
    取消设置不让看和不看朋友圈
    仅限319测试号段使用，支持SH、SZ Idc，成功返回0
    undo_hide_moments("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag1 = set_contact(username, friend, 0, 3)
    flag2 = add_sns_tag(username, friend, 0)
    flag3 = del_sns_tag(username, friend, 0)
    # del_sns_tag(username, friend, 5)
    if flag1 == 0 and flag2 == 0 and flag3 == 0:
        return 0
    else:
        return -1


def post_text_feed(username, content):
    """
    发表朋友圈文本动态
    仅限319测试号段使用, 只支持上海IDC，发布成功返回一串snsid，发布失败返回0
    post_text_feed("autotest_mmtools_sh","发布正文")

    :param username:
    :param content:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmindex"   #这个支持所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'postsns',
        'func_args': {'username': username, 'content': content}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    logger.info(result)

    snsid = 0
    if not result.get('rtn'):
        snsid = result.get('data').get('snsid')

    return snsid


def post_pic_feed(username, number, content=None):
    """
    发表朋友圈图片动态
    仅限319测试号段使用, 只支持上海IDC，发布成功返回一串snsid，发布失败返回0
    post_pic_feed("autotest_mmtools_sh",2,"发布正文")

    :param username:
    :param number:
    :param content:
    :return:
    """
    """number为图片数"""
    # url = "http://%s/mmcasehelperidc/mmindex"    #这个支持所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'postsns',
        'func_args': {'username': username, 'number': int(number), 'content': content}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()

    snsid = 0
    if not result.get('rtn'):
        snsid = result.get('data').get('snsid')

    return snsid


def post_other_feed(username, type, content=None):
    """
    发表除了文本和图片之外的朋友圈动态
    仅限319测试号段使用, 只支持sh IDC，发布成功返回一串snsid，发布失败返回0
    post_other_feed("autotest_mmtools_sh",'link',"发布正文")

    :param username:
    :param type:
    :param content:
    :return:
    """
    types = {
        'link': 1,
        'video': 3,
        'music_link': 4,
        'video_link': 5,
        'sticker_link': 6,
        'ad': 7
    }
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'postsns',
        'func_args': {'username': username, 'link': types.get(type), 'content': content}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()

    snsid = 0
    if not result.get('rtn'):
        snsid = result.get('data').get('snsid')

    return snsid


def snscomment(username, snsid, content=None):
    """
    对朋友圈动态点赞/发表评论，带文字为发表评论，不带文字表示点赞
    仅限319测试号段使用, 只支持sh IDC，发布成功返回0
    eg:snscomment("autotest_mmtools_sh", 13006325618931208283, content="这是评论")

    :param username:
    :param snsid:
    :param content:
    :return:
    """
    """content指评论内容，为空时表示点赞"""
    # url = "http://%s/mmcasehelperidc/mmindex"    #这个支持所有IDC
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'snscomment',
        'func_args': {'username': username, 'content': content, 'snsid': int(snsid)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def snscomment2(username, snsid, content="评论不为空，最好带时间戳保证不重复"):
    """
    对朋友圈动态点赞/发表评论，发表的文字最好带上时间戳保证是唯一不重复的,int(time.time())
    仅限319测试号段使用, 只支持sh IDC，发布成功返回commentID,否则返回-1
    eg:snscomment2("autotest_mmtools_sh", 13006325618931208283, content="评论正文+1550478722")

    :param username:
    :param snsid:
    :param content:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmindex"    #这个支持所有IDC
    if content is None:
        # print("Err：评论不允许为空")
        return -1
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'snscomment',
        'func_args': {'username': username, 'content': content, 'snsid': int(snsid)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    if res.json().get('rtn') == 0:
        datajson = res.json().get("data")
        for n in datajson:
            if datajson[n] == content:
                return n
    else:
        return -1


def del_snscomment(username, snsid, commentid):
    """
    删除特定动态下的特定评论
    仅限319测试号段使用, 只支持sh IDC，成功返回0
    eg:del_snscomment("autotest_mmtools_sh", 13006325618931208283,193)

    :param username:
    :param snsid:
    :param commentid:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmindex"
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': "DelSnsComment",
        'func_args': {"username": username, "snsid": snsid, "commentid": commentid}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def snsadcomment(username, snsid, content=None):
    """
    # 对广告动态点赞／发表评论'
    :param username:
    :param snsid:
    :param content:
    :return:
    """
    """content指评论内容，为空时表示点赞"""
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'snsadcomment',
        'func_args': {'username': username, 'content': content, 'snsid': snsid}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())


def add_sns_tag(username, friend, tagid):
    """
    设置朋友圈关系标记
      MM_SNS_TAG_ID_OUTSIDERS  = 0x4,  //不让他看我的朋友圈
      MM_SNS_TAG_ID_BLACKLIST  = 0x5,  //不看他的朋友圈
    :param username:
    :param friend:
    :param tagid:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmindex"
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'AddSnsTagMember',
        'func_args': {'user_uin': get_uin(username), 'memberuin': get_uin(friend), 'tagid': tagid}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())
    # print((res.json()))
    return res.json().get('rtn')


def del_sns_tag(username, friend, tagid):
    """
    删除朋友圈黑名单标记
    :param username:
    :param friend:
    :param tagid:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'DelSnsTagMember',
        'func_args': {'user_uin': get_uin(username), 'memberuin': get_uin(friend), 'tagid': tagid}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


# ------------------------------ 微信运动 ---------------------------------------


def get_steps(username):
    """
    微信运动 获取步数
    仅限319测试号段使用, 支持所有IDC，成功返回步数
    eg ：get_steps("autotest_mmtools_sh")

    :param username:
    :return:
    """
    uin = get_uin(username)

    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'GetWeRunStep',
        'func_args': {'user_uin': uin, 'timestamp': 0}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    steps = result.get('steps')
    return steps


def set_steps(username, steps):
    """
    微信运动 设置步数,step 要少于40000
    仅限319测试号段使用, 支持所有 IDC，成功返回0
    eg： set_steps("autotest_mmtools_sh",8999)

    :param username:
    :param steps:
    :return:
    """
    uin = get_uin(username)
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'SetWeRunStep',
        'func_args': {'user_uin': uin, 'steps': int(steps), 'timestamp': 0, 'timezone': 8}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def like_werun(from_username, to, type=1):
    """
    微信运动点赞,from- 点赞发起者 to- 被点赞者 type=1表示点赞步数, type=3表示点赞封面
    仅限319测试号段使用, 支持所有 IDC，成功返回0
    eg: like_werun("autotest_mmtools_sh","rdgztest_atm1",1)

    :param from_username:
    :param to:
    :param type:
    :return:
    """
    from_uin = get_uin(from_username)

    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'AddWeRunLike',
        'func_args': {'user_uin': from_uin, 'tousername': to, 'type': int(type)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def set_werun_black(username, friend):
    """
    微信运动 不与他(她)排行
    仅限319测试号段使用, 支持所有 IDC( 除HK IDC），成功返回0
    set_werun_black("autotest_mmtools_sh","rdgztest_atm1")
    :param username:
    :param friend:
    :return:
    """
    flag = set_contact(username, friend, 0, 524291)
    return flag


def undo_werun_black(username, friend):
    """
    微信运动 取消不与他(她)排行
    仅限319测试号段使用, 支持所有 IDC( 除HK IDC），成功返回0
    undo_werun_black("autotest_mmtools_sh","rdgztest_atm1")

    :param username:
    :param friend:
    :return:
    """
    flag = set_contact(username, friend, 0, 3)
    return flag


def enable_werun(username):
    """
    启用微信运动
    仅限319测试号段使用, 支持所有 IDC，成功返回0
    enable_werun("autotest_mmtools_sh")
    :param username:
    :return:
    """
    flag = mmbiztoolsUtil.subscribe(username, "werun-wechat")
    return flag


def disable_werun(username):
    """
    禁用微信运动
    仅限319测试号段使用, 支持所有 IDC，成功返回0
    disable_werun("autotest_mmtools_sh")
    :param username:
    :return:
    """
    flag = mmbiztoolsUtil.unsubscribe(username, "werun-wechat")
    return flag


# —————————————————————————————————获取、设置 用户属性 —————————————————————————————————————
G_PLUGIN_FuncDic = {
    "SNS": 1,  # 朋友圈
    "SCAN": 2,  # 扫一扫
    "SHAKE": 3,  # 摇一摇
    "KANYIKAN": 4,  # 看一看
    "SOUYISOU": 5,  # 搜一搜
    "LBS": 6,  # 附近的人
    "BOTTLE": 7,  # 漂流瓶
    "JD": 8,  # 购物
    "GAME": 9,  # 游戏
    "APPBRAND": 10,  # 小程序
    "WECHATOUT": 11,  # Wechat Out
    "FACEBOOK": 12,  # FaceBook
    "TXNEWS": 13,  # 腾讯新闻
    "MASSSEND": 14,  # 群发助手
    "TEENAGER_MODE": 27  # 青少年模式
}


def plugin_switch_op(username, opname, value):
    """
    设置发现页管理的插件，和辅助功能的插件
    仅限上海IDC测试号使用，value: 0为关闭, 1为打开，成功返回0
    eg: plugin_switch('autotest_mmtools_sh',"SNS",1)

    :param username:
    :param opname:
    :param value:
    :return:
    """

    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'OplogSwitch',
        'func_args': {'username': username, "opname": opname, "value": int(value)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json()['rtn']


def plugin_switch(username, key, value):
    """
    设置发现页管理的插件，和辅助功能的插件,会T账号
    仅限上海IDC测试号使用，value: 0为关闭, 1为打开，成功返回0
    eg: plugin_switch('autotest_mmtools_sh',"SNS",1)

    :param username:
    :param key:
    :param value:
    :return:
    """
    return plugin_switch_op(username, G_PLUGIN_FuncDic.get(key), value)


def op_voiceprint(username, value=0):
    """
    打开或者关闭声音锁登录
    仅限制sh idc的测试号码使用。value：1-打开，0-关闭 没有注册声音锁或者无权访问返回 -1，正常操作返回 0
    eg: op_voice# print("autotest_sh_cool_001", 1)

    :param username:
    :param value:
    :return:
    """
    uin = get_uin(username)
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'VoicePrintSwitch',
        'func_args': {'user_uin': uin, "value": int(value)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    # print(result)
    rtn = result.get('rtn')
    return rtn


def get_Regcountry(username):
    """
    获取用户注册国家
    限319测试号段使用，不限idc, 成功返回国家代码，如："HK"，"CN"，不成功返回None
    eg: get_Regcountry("autotest_mmtools_sh")

    :param username:
    :return:
    """
    flag = get_user_attr(username, 'RegCountry')
    return flag


def set_Regcountry(username, country):
    """
    设置用户注册国家，限319测试号段使用，只能对sh idc的319段测试号码操作, 成功返回0

    eg: set_Regcountry("autotest_mmtools_sh","HK")

    :param username: 微信号
    :param country: 国家
    :return:
    """
    flag = set_user_attr(username, 'RegCountry', country)
    return flag


def get_user_attr(username, key):
    """
    获取用户某项属性, 限319测试号段使用，不限idc,如果号码不存在或者key值不对，返回None ，否则返回 key的内容
    key的值有很多，如:

        'City'（地区），'Province'（省份），'Country'（国家），'RegCountry'（注册国家），'Language'（语言），
        'Signature'（签名），'NickName'（名字），'Sex'（性别）等等信息

    eg: get_user_attr("autotest_mmtools_sh", "Language")    # 获取用户设置的语言,key值大小写敏感

    :param username:
    :param key:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUserAttr',
        'func_args': {'username': username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    data = res.json()['data']
    if data:
        return data.get(key)
    else:
        return None


def set_user_attr(username, key, value):
    """
    设置用户某项属性
    只能对sh idc的319段测试号码操作，如果执行成功会返回0
    eg:   set_user_attr("autotest_mmtools_sh", "City", "Guangzhou")    # 设置地区为广州

    :param username:
    :param key:
    :param value:
    :return:
    """
    # url = "http://%s/mmcasehelperidc/mmaccount"
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'SetUserAttr',
        'func_args': {'username': username, "key": key, "value": str(value)}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def get_user_attr_all(username):
    """
    展示用户所有属性
    限319测试号段使用，不限idc,如果号码不存在或者key值不对，返回None ，否则返回 data 的内容
    eg: get_user_attr_all("autotest_mmtools_sh")

    :param username:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUserAttr',
        'func_args': {'username': username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    data = result.get('data')
    logger.info(result)
    if result.get('rtn') == 0:
        return data
    else:
        return None


# -------------------------- 群聊，单聊会话profile信息 -------------------------------
def set_contact_mute(username, to_username, mute=True):
    """
    设置或者去掉单聊、群聊会话静音，  True 为会话静音，False为 正常
    单聊会话，username, to_username都必须是319号段测试号码，username还必须是非HKIDC的，操作成功返回0
    单聊会话  eg:  set_contact_mute("autotest_mmtools_sh", "rdgztest_atm1", mute=True)
    群聊必须是用工具建的群才能生效，自己在手机上创建的群聊无效,可以用工具set_test_chatroom设置为测试群
    群聊会话  eg:  set_contact_mute("autotest_mmtools_sh", "11799220724@chatroom", mute=False)

    :param username:
    :param to_username:
    :param mute:
    :return:
    """
    if to_username.find("@chatroom") > 0:
        itype = 2
    else:
        itype = 0
    origin_type = get_simple_contact(username, to_username, itype)
    if origin_type < 0:
        return -1
    if mute:
        origin_type |= 512
    else:
        origin_type &= ~512
    if itype == 0:
        flag = set_contact(username, to_username, itype, origin_type)
    else:
        roomid = to_username[:-9]
        status = get_chatroom_member(username, roomid).get('Status')
        if status is not None:
            flag1 = set_simple_contact(username, to_username, itype, origin_type)
            if mute:
                status &= 0
            else:
                status |= 0x1
            flag2 = set_chatroom_member(username, roomid, 'Status', status)
            if flag1 == 0 and flag2 == 0:
                flag = 0
            else:
                flag = -1
        else:
            raise util.MMToolsError("tools error")
    return flag


def get_chatroom_displayname(username, roomid):
    """
    获取群聊中群昵称
    仅允许319测试号段操作，群ID不存在或用户不在群里返回-1，找到会返回群别名（没设置过为空 Null）
    eg: get_chatroom_displayname("autotest_mmtools_sh", 11799220724)

    :param username:
    :param roomid:
    :return:
    """
    roomid = int(roomid)
    data = get_chatroom_member(username, roomid)
    if data is not None:
        if data['Uin'] == 0:
            # print("这个微信号不在该群中")
            return -1
        else:
            displayname = data['DisplayName']
            return displayname
    else:
        # print("无效的群ID或者非测试号码")
        return -1


def set_chatroom_displayname(username, roomid, displayname):
    """
    修改群聊中群昵称
    仅允许319测试号段操作，群ID不存在或用户不在群中均返回-1，设置失败，设置成功返回0。
    eg: set_chatroom_displayname("autotest_mmtools_sh", 11799220724, u"测试中文别名")

    :param username:
    :param roomid:
    :param displayname:
    :return:
    """
    roomid = int(roomid)
    display = displayname.encode("utf-8")
    res = set_chatroom_member(username, roomid, "DisplayName", display)
    return res == 0


def set_chatroom_display_switch(username, roomid, value="1"):
    """
    打开或者关闭群聊中别名显示开关，默认为打开，关闭value为0
    仅允许319测试号段操作，群ID不存在或用户不在群中均返回-1，设置失败，设置成功返回0
    eg: set_chatroom_display_switch("autotest_mmtools_sh", 11799220724)

    :param username:
    :param roomid:
    :param value:
    :return:
    """
    roomid = int(roomid)
    value = str(value)
    res = set_chatroom_member(username, roomid, "Flag", value)
    return res == 0


def set_chatroom_topic(username, roomid, name):
    """
    修改群名，不限于测试群
    仅允许319测试号段操作，无权修改群名或者不在群里，会操作失败，返回-2，修改成功返回0
    eg: set_chatroom_topic("autotest_mmtools_sh",12008154509,u"修改后的群名")

    :param username:
    :param roomid:
    :param name:
    :return:
    """
    uin = GetUin(username)
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    roomid = int(roomid)
    key = 'Topic'
    # name = util.MMGBK2UTF8(name)
    data = {
        'func_name': 'SetChatRoomAttr',
        'func_args': {"user_uin": uin, "roomid": roomid, "key": key, "value": name}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.url)
    logger.info(res.json())
    return res.json().get('rtn')


def demand_chatroom(username, chatroomid):
    """
    设置按需拉取群标志位
    只能对319段的上海 idc(SZ,HK IDC 都不行)的测试号码操作,操作成功返回0
    群聊必须是用工具建的群才能生效，脚本预设置了测试群
    eg: demand_chatroom("autotest_mmtools_sh", 11799220724)

    :param username:
    :param chatroomid:
    :return:
    """
    # set_test_chatroom(username,chatroomid)
    flag1 = set_contact_mute(username, str(chatroomid) + "@chatroom", mute=True)
    flag2 = set_chatroom_member(username, int(chatroomid), "Status", str(0x2))
    if flag1 == 0 and flag2 == 0:
        return 0
    else:
        return -1


def set_test_chatroom(username, chatroomid):
    """
    设置为测试群，后续可以使用其他群相关的工具(但对测试群聊增加成员的工具没有用）
    对IDC 和号码没有做限制,成功返回0
    使用前最好能先确定这个号码在该群聊中，可以使用get_chatroom_member来确定
    eg: set_test_chatroom("autotest_mmtools_sh", 12149179564)

    :param username:
    :param chatroomid:
    :return:
    """
    uin = get_uin(username)
    try:
        # chatroom = chatroom[:chatroom.find('@')]
        roomid = int(chatroomid)
    except:
        # print("invalid chatroom")
        return False
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    data = {
        'func_name': "SetTestChatroom",
        'func_args': {"user_uin": uin, "roomid": roomid}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(data)
    logger.info(res.json())
    # print((res.json()))
    return res.json()['rtn']


def get_chatroom_member(username, roomid):
    """
    获取群聊属性
    所有idc的319段测试号码可用,群ID错误或者非测试号码返回负数，其他返回data数据
    get_chatroom_member("autotest_mmtools_sh", roomid)
    返回结果 status  消息免打扰开关: 1 -没打开   0 - 打开
            flag    显示群成员昵称  1- 打开     0- 没打开
            displayname 在本群的昵称
    :param username:
    :param roomid:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    data = {
        'func_name': 'GetChatRoomMember',
        'func_args': {'username': username, "roomid": int(roomid)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    data = result.get('data')
    return data


def set_chatroom_member(username, roomid, key, value):
    """
    设置群聊属性
    所有idc的319段测试号码可用,执行失败返回 -1,非测试号段返回-4，成功返回0
    set_chatroom_member("autotest_mmtools_sh", roomid,"Flag",1) # 打开别名开关
    :param username:
    :param roomid:
    :param key:
    :param value:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    data = {
        'func_name': 'SetChatRoomMember',
        'func_args': {'username': username, "roomid": int(roomid), "key": str(key), "value": str(value)}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print((res.json()))
    logger.info(res.json())
    return res.json().get('rtn')


def get_chatroom_attr(username, roomid):
    """
    获取群聊天室的信息，目前只能返回跟群公告相关内容，没啥用
    测试319号段可操作
    返回： Announcement 群公告  AnnouncementEditor 公告发表人
    eg: get_chatroom_attr("autotest_mmtools_sh",11138223964)

    :param username:
    :param roomid:
    :return:
    """
    uin = GetUin(username)
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    roomid = int(roomid)
    data = {
        'func_name': 'GetChatRoomAttr',
        'func_args': {"user_uin": uin, "roomid": roomid, "key": "key"}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())
    return res.json().get('data')


def get_chatroommemberlist(username, roomid):
    """
    不限于测试群使用,需要填写一个群成员，和群id ,成功返回群成员列表
    eg: get_chatroommemberlist("yunwuxin_sh_008", "17708083342")

    :param username:
    :param roomid:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    roomid = int(roomid)
    data = {
        'func_name': 'GetChatRoomMemberList',
        'func_args': {"username": username, "roomid": roomid}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('data')['member_vec']


# --------------------------------- 群聊工具 ：建群、加人-------------------------------------

def create_chatroom(group_owner, num=5):
    """
    创建测试群聊会话，可以指定群成员数目num(num>=5)，群成员（除群主外）从测试号码池子里面选：rdgztest_atm1 - rdgztest_atm9999
    仅限群主为319段各IDC测试号段使用，群成员数量至少大于等于5人，成功返回群id，失败返回负值
    eg: create_chatroom("autotest_mmtools_sh", 8)

    :param group_owner:
    :param num:
    :return:
    """
    uin = get_uin(group_owner)
    url = 'http://%s/mmcasehelperidc/mmchatroom' % CASE_SVR
    data = {
        'func_name': 'createchatroom',
        'func_args': {'user_uin': uin}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    group_id = res.json()['data']['chatroom_name'].split('@')[0]
    if int(num) > 5:
        add_n_chatroom_member(group_id, num - 5)
    return group_id


def create_n_chatroom(group_owner, group_num, member_num):
    """
    建N个测试群,群里有num(num>=5)个成员，群成员（除群主外）从测试号码池子里面选：rdgztest_atm1 - rdgztest_atm9999
    仅限群主为319段各IDC测试号段使用，群成员数量至少s大于等于5人，成功返回0
    eg: create_n_chatroom("autotest_mmtools_sh", 5, 8)

    :param group_owner:
    :param group_num:
    :param member_num:
    :return:
    """
    n = 0
    while n < group_num:
        flag = create_chatroom(group_owner, member_num)
        n = n + 1
        if flag < 0:
            logger.info("create chatroom fail ")
            # print("创群失败")
            return -1
        time.sleep(0.1)
    logger.info("create chatroom success ")
    return 0

def get_default_chatroom_creator():
    """
    获取当前创建群聊的测试号, 用于添加成员 (不同url,chatroom_creator可能不一样)
    """
    url = 'http://%s/mmcasehelperidc/mmchatroom' % CASE_SVR
    data = {
        'func_name': 'GetCreateChatRoomInfo',
        'func_args': {
        }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    
    try:
        default_chatroom_creator = res.json().get('data').get('chatroom_creator', "rdgztest_atm2040")
        logger.info("GetCreateChatRoomInfo succ, chatroom_creator is {}".format(default_chatroom_creator))
        return default_chatroom_creator
    except:
        logger.info("GetCreateChatRoomInfo Error, chatroom_creator set to rdgztest_atm2040")
        return "rdgztest_atm2040"


def add_chatroom_member(group_id, username, invitor=None):
    """
    往特定群聊添加成员
    仅限使用工具create_chatroom(group_owner, num=5)创造的群使用，添加的成员为319段测试号码，成功返回0
    eg: 添加单个 add_chatroom_member(17720985741,"autotest_mmtools_hk")

    :param group_id:
    :param username:
    :param invitor: 邀请进群的人
    :return:
    """
    return add_chatroom_member_list(group_id, [username], invitor)


def add_chatroom_member_list(group_id, member_list, invitor=None):
    """
    往特定群聊添加成员
    仅限使用工具create_chatroom(group_owner, num=5)创造的群使用，添加的成员为319段测试号码，成功返回0
    eg: 添加单个 add_chatroom_member(17720985741,"autotest_mmtools_hk")

    :param group_id:
    :param username:
    :param invitor: 邀请进群的人
    :return:
    """
    if invitor is None:
        invitor = get_default_chatroom_creator()  # "rdgztest_atm2040"
    group_id = str(group_id) + "@chatroom"
    url = 'http://%s/mmcasehelperidc/mmchatroom' % CASE_SVR
    data = {
        'func_name': 'addchatroommember',
        'func_args': {
            'username': invitor,
            'chatroom': group_id,
            'member_list': member_list
        }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def add_n_chatroom_member(group_id, num, invitor=None):
    """
    使用群ID往群聊加num个人,群成员（除群主外）从测试号码池子里面选：rdgztest_atm1 - rdgztest_atm9999
    仅限使用工具create_chatroom(group_owner, num=5)创造的群使用，成功返回0
    eg: add_n_chatroom_member(17720985741,8)

    :param group_id:
    :param num:
    :param invitor: 邀请人
    :return:
    """
    if invitor is None:
        invitor = get_default_chatroom_creator() #'rdgztest_atm2040'
    group_id = str(group_id) + "@chatroom"
    num = int(num)
    remain_num = num
    if remain_num == 0:
        # print("num为0，不需要操作")
        logger.info("num为0，不需要操作")
        return -1
    url = 'http://%s/mmcasehelperidc/mmchatroom' % CASE_SVR
    while True:
        if remain_num > 20:
            data = {
                'func_name': 'addtestchatroommember',
                'func_args': {
                    'username': invitor,
                    'chatroom': group_id,
                    'number': 20
                }
            }
            util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
            remain_num = remain_num - 20
        else:
            data = {
                'func_name': 'addtestchatroommember',
                'func_args': {
                    'username': invitor,
                    'chatroom': group_id,
                    'number': remain_num
                }
            }
            res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
            break
    if res.json().get('rtn') == 0:
        # print(("添加%s个群成员成功" % num))
        return 0
    else:
        # print("添加群成员失败")
        return -1


def get_chatroommember_list(username, roomid):
    """
    列出所有群成员
    限制319段的号码操作，成功返回群成员信息,否则返回负值
    eg: get_chatroommember_list("autotest_mmtools_sh", 6174306626)

    :param username:
    :param roomid:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    memberuin = get_uin(username)
    data = {
        'func_name': 'getchatroommemberlist',
        'func_args': {
            'user_uin': memberuin,
            "roomid": int(roomid)
        }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    if res.json().get('rtn') == 0:
        return res.json().get('data')
    else:
        return res.json().get('rtn')


# ------------------------------- 消息提醒 ---------------------------------


def set_push_flag(username, open_flag=True):
    """
    打开或者关闭设置-新消息消息-新消息通知提醒，True 为打开新消息通知 ，False为关闭消息通知
    只允许SH IDC的319段测试号码可用,成功返回0
    set_push_flag("autotest_mmtools_sh")
    :param username:
    :param open_flag:
    :return:
    """
    ext_status = get_user_attr(username, "ExtStatus")
    # # print ext_status
    if ext_status is None:
        return -1
    if open_flag:
        ext_status &= ~0x40
    else:
        ext_status |= 0x40
    flag = set_user_attr(username, "ExtStatus", ext_status)
    return flag


def set_push_detail_flag(username, close_flag=False):
    """
    打开或者关闭设置-新消息消息-消息提醒详情，True 为不显示消息详情 ，False为显示详情
    只允许SH IDC的319段测试号码可用,成功返回0
    set_push_flag("autotest_mmtools_sh")
    :param username:
    :param close_flag:
    :return:
    """
    status = get_user_attr(username, "Status")

    if status is None:
        # raise MMToolsError('Status None')
        return -1
    if close_flag:
        status |= 2048
    else:
        status &= ~2048
    flag = set_user_attr(username, "Status", status)
    return flag


def send_push(username, content="test", type=1):
    """
    发送push 消息，工具失效，木有用！！！

    :param username:
    :param content:
    :param type:
    :return:
    """
    """发送push type 1为apns push ,type 2为voip push"""
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'sendiospush',
        'func_args': {'username': username, 'content': content, 'type': type}
    }

    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())


# ------------------------------ 微信、企业微信互通群 ---------------------------


def create_imchatroom(owner, tpuser, wxuser):
    """
    新建互通群聊，以下用户需要好友关系:
    Owner  微信用户名,
    tpuser 企业微信用户名, ***@openim
    wxuser 微信用户名
    :param owner:
    :param tpuser:
    :param wxuser:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    data = {
        'func_name': 'CreateOpenIMChatroom',
        'func_args': {"owner": owner, "tpuser": tpuser, "wxuser": wxuser}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())
    result = res.json().get('data')
    group_id = result["openimchatroom_name"]
    # print(group_id)


def add_imchatroom_member(username, chatroom, userlist):
    """
    互通群聊加人
    user        在群内的用户
    imchatroom  连接群的群名  如********@im.chatroom
    member_list 需要加入群的的用户列表, 包含微信用户或者企业微信用户
    :param username:
    :param chatroom:
    :param userlist:
    :return:
    """
    # if type(userlist) == type(""):
    if isinstance(userlist, str):
        userlist = [userlist]
    url = "http://%s/mmcasehelperidc/mmchatroom" % CASE_SVR
    data = {
        'func_name': 'AddOpenIMChatroomMember',
        'func_args': {"user": username, "imchatroom": chatroom, "member_list": userlist, }
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.url)
    logger.info(res.json())


# -------------------------------- 企业微信 -------------------------------------

# -------------------------------- 支付  ---------------------------------------
def send_1to1_hongbao(username, to_username, title='test'):
    """
    发送支付红包消息，为避免出错，发送之前会互加好友,收到只能看表现不能点击
    仅限 319测试号段使用，发送成功返回0
    eg : send_1to1_hongbao("autotest_mmtools_sh", "autotest_sh_cool_006", u"恭喜发财，红包拿来")

    :param username:
    :param to_username:
    :param title:
    :return:
    """
    add_friend(username, to_username)
    # url = "http://%s/mmcasehelperidc/mmindex"
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'SendHongBaoMsg',
        'func_args': {'username': username, 'tousername': to_username, "aeskey": "aeskdddey", "extinfo": "extinfoddd",
                      "title": title}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())
    return res.json().get('rtn')


def send_1to1_wepay_transfer(username, to_username, title="测试转账给你", amount=10):
    """
    发送支付转账消息，为避免出错，发送之前会互加好友,收到只能看表现不能点击
    仅限 319段测试号段使用，amount是转账的钱，只能为整数（单位：元），发送成功返回0
    eg:send_1to1_wepay_transfer("autotest_mmtools_sh", "autotest_sh_cool_006", u"测试转账给你",10)

    :param username:
    :param to_username:
    :param title:
    :param amount:
    :return:
    """
    add_friend(username, to_username)
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'SendPayTransferMsg',
        'func_args': {'username': username, 'tousername': to_username, "paymemo": title, "amount": amount}
    }
    logger.info(data)
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(res.json())
    # print((res.json()))
    return res.json().get('rtn')


# -------------------------------- 时光视频 -------------------------------------
def PostStory(username):
    """
    随机发不同Story，返回storyid ,可供发表评论和查询之用
    不同的视频的xml存放在StoryXML.py 里面，可以根据自己需要增减
    仅限于深圳，上海IDC的用户,成功返回 storyid
    eg: PostStory("autotest_mmtools_sh")

    :param username:
    :return:
    """
    uin = get_uin(username)

    # Now = int(time.time())
    # _username = get_realusername(username)

    # n=random.randrange(0,3)
    # file= eval("XML"+str(n))
    # DescBuff = Str2Bytes(MMGBK2UTF8(file % (_username, Now)))
    # DescBuff = Str2Bytes(MMGBK2UTF8(XML5 % (_username, Now)))

    rand_idx = random.choice(list(story_xml.keys()))
    XML = story_xml[rand_idx]
    # DescBuff = Str2Bytes(MMGBK2UTF8(XML % (_username, Now)))  # 同一个视频xml被使用超过200次后，md5重复了，不能再使用
    DescBuff = gen_storybuffer(XML)

    # 如果需要推某条视频，可直接用下面这句，定义一下XML即可
    # DescBuff = Str2Bytes(MMGBK2UTF8(XML % (_username, Now)))

    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'PostStory',
        'func_args': {"user_uin": uin, "buffer": DescBuff}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    logger.info(data)
    result = res.json()
    # print(result)
    storyid = result.get('data').get('storyid')
    return storyid


def AddStoryComment(fromusername, tousername, storyid, content, bubbleenhance=1, color=0):
    """
    对视频发表评论
    fromusername仅限于上海，深圳idc号码,为保证成功工具会自动添加tousername为双向好友，成功返回0
    eg: AddStoryComment("autotest_mmtools_sh", "rdgztest_atm1", 13007098044360036486, u"hahaha", 1, 1)

    :param fromusername:
    :param tousername:
    :param storyid:
    :param content:
    :param bubbleenhance:
    :param color:
    :return:
    """
    uin = get_uin(fromusername)
    content = util.MMGBK2UTF8(content)
    add_friend(fromusername, tousername)

    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'AddStoryComment',
        'func_args': {"user_uin": uin, "tousername": tousername, "storyid": int(storyid), "content": content,
                      "bubbleenhance": bubbleenhance, "bubblecolor": color}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def GetAllStory(username):
    """
    获取并返回用户所有StoryId(不仅是24H可见的视频），没有视频的时候返回空列表
    目前仅支持上海IDC的测试号码
    eg: GetAllStory("autotest_mmtools_sh")

    :param username:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'GetAllStoryId',
        'func_args': {"username": username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    _storyid = []
    if result.get('data', []):
        _storyid = result.get('data').get('storyid')
    # # print _storyid
    logger.info(res.json())
    return _storyid


def DelStory(username, storyid, realdel):
    """
    删除时光视频
    删除成功返回 0，仅限上海测试号使用
    eg: DelStory("autotest_mmtools_sh", 12965914539720380470, 0)
    参数2: storyid, 0:删除所有story,非0则为已发表的storyid
    参数3: realdel, 1:硬删除, 0:软删除

    :param username:
    :param storyid:
    :param realdel:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'DelStory',
        'func_args': {"username": username, "storyid": storyid, "realdel": int(realdel)}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    return res.json().get('rtn')


def Str2Bytes(input):
    # if type(input) != type(""):
    if not isinstance(input, str):
        # print("Str2Bytes arg1 must be str")
        return input
    dataList = []
    for byte in input:
        temp = ord(byte)
        dataList.append(temp)
    return dataList


def get_realusername(username):
    url = "http://%s/mmcasehelperidc/mmaccount" % CASE_SVR
    data = {
        'func_name': 'GetUser',
        'func_args': {'username': username}
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    result = res.json()
    # print(result)
    usr = result.get('data').get('username')
    return str(usr)


def getmd5(source):
    # if type(source) != type(""):
    if not isinstance(source, str):
        # print("input must be string")
        return ""
    return hashlib.md5(source).hexdigest()


def gen_storybuffer(xml):
    try:
        tree = ET.fromstring(xml)  # ET.parse(path)
    except:
        # print("xml path Error ,Please Check!")
        return []
    root = tree

    time_str = str(time.time())
    time_md5 = getmd5(time_str)

    time_element = root.find('createTime')
    if time_element is not None:
        time_element.text = time_str
    else:
        # print("Error, please Check  createTime  element!")
        return []

    url_element = root.find('ContentObject/mediaList/media/url')
    if url_element is not None:
        url_element.attrib['videomd5'] = time_md5  # md5videomd5,videomd5

    else:
        # print("Error, please Check url element!")
        return []

    try:
        XMLCotent = ET.tostring(root, encoding="utf-8")
    except:
        # print("XMLContent tostring Error!")
        return []
    return Str2Bytes(util.MMGBK2UTF8(XMLCotent))


# ---------------------------------------  收藏 ----------------------------------
def del_all_favitems(tousername):
    """
    删除所有的收藏数据，只限上海IDC测试号码使用，删除成功返回0
    eg: del_all_favitems("autotest_mmtools_sh")

    :param tousername:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'DelAllFavItems',
        'func_args': {"username": tousername}
    }

    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


def add_favitems(username, _type, content):
    """
     添加各种格式的收藏数据,只限上海IDC测试号码使用，成功返回0
     eg: add_favitems("autotest_mmtools_sh",1,u"测试文字" )
     _type:
     MM_FAV_ITEM_TYPE_TXT             = 1, 文本 ,通过content自定义文本
     MM_FAV_ITEM_TYPE_IMG             = 2, 图片
     MM_FAV_ITEM_TYPE_VOICE           = 3, 语音
     MM_FAV_ITEM_TYPE_VIDEO           = 4, 视频
     MM_FAV_ITEM_TYPE_WEBPAGE         = 5, 网页
     MM_FAV_ITEM_TYPE_LOC             = 6, 位置
     MM_FAV_ITEM_TYPE_MUSIC           = 7, 音乐
     MM_FAV_ITEM_TYPE_FILE            = 8, 文件
     MM_FAV_ITEM_TYPE_RECORD          = 14, 聊天记录
     MM_FAV_ITEM_TYPE_NOTE            = 18, 笔记

    :param username:
    :param _type:
    :param content:
    :return:
    """
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    data = {
        'func_name': 'AddFavItem',
        'func_args': {"username": username, "type": int(_type), "content": util.MMGBK2UTF8(content)}
        # , "buffer": xml }
    }
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    return res.json().get('rtn')


# ---------------------------------------  其他 ----------------------------------
def query_crash(username, begintime, endtime):
    """
    查询号码在时间段内是否有crash，不限号码
    begintime,endtime 为时间戳-整数，如： begintime = int(time.time() - 2 * 60 * 60) #2小时之前

    :param username:
    :param begintime:
    :param endtime:
    :return:
    """

    uin = get_uin(username)

    url = "http://%s/mmcrashas/ic_log_wechat/_search?pretty" % CASE_SVR
    data = {
        "query": {"bool": {"filter": [{"term": {"uin": uin}},
                                      {"range": {"c_time": {"gte": begintime, "lte": endtime}}}]}
                  }
    }

    res = util.mmtools_get(url, json=data, retry_count=RETRY)
    ret = res.json()
    crash_num = ret['hits']['total']
    result = []
    if crash_num > 0:
        for crash in ret['hits']['hits']:
            raw_path = crash['_source']['raw_path']
            link = "http://qualityback.oa.com/iOS_platform/crashfileview.php?raw_path=%s&app_name=wechat" % raw_path
            result.append(link)
    return result


# ---------------------------------------  测试中 ----------------------------------
def unbind_facebook2(username):
    pluginSwitch = int(get_user_attr(username, "PluginSwitch"))
    pluginSwitch &= (~0x4)  # MM_STATUS_RECFBFRIEND_OPEN
    set_user_attr(username, "FBAccessToken", "")
    set_user_attr(username, "FBUserID", "")
    set_user_attr(username, "FBUserName", "")
    set_user_attr(username, "PluginSwitch", pluginSwitch)


def add_outside_whitelist(username, idc="idc"):
    #  给新注册的号码加白名单，不然在外网会被T出登录
    url = f'http://{CASE_SVR}/mmcasehelper{idc}/mmaccount'
    data = {'func_name': 'MarkOuterTestUin', 'func_args': {'username': username, 'expiredtime': 864000}}
    res = util.mmtools_post(url, data=json.dumps(data), retry_count=2)
    logger.info(res.json())
    return res.json().get('rtn')


def del_all_friends(username):
    """
    删除通讯录所有测试号好友
    只限319测试号段，所有idc 都可以使用, 全部执行成功删除好友返回0
    eg:del_all_friends("autotest_mmtools_sh")
    
    :param username:
    :return:
    """
    all_contacts = get_all_contacts(username)
    favourcontact = get_all_friend(all_contacts)
    flag = 0
    for _fav in favourcontact:
        to_username = GetUsername(str(_fav['contactuin']))
        ret = set_contact(username, to_username, 0, 0)
        if not ret:
            logger.info("del friend %s succ!" % _fav['contactuin'])
        else:
            logger.info("del friend %s Err!" % _fav['contactuin'])
            flag = -1
    return flag


def get_all_friend(contact_list):
    """
    过滤319段测试号码好友 (仅供 del_all_friends 调用）
    
    :param contact_list:
    :return:
    """
    _insidecontact = []
    for one in contact_list:
        if util.is_test_uin(one['contactuin']) and one['type'] == 3:
            _insidecontact.append(one)
    return _insidecontact


if __name__ == "__main__":
    print ('report')
    SendXML(cutebot333, filename='adTest.xml.txt', type=10002)
