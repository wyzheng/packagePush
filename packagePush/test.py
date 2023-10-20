# -*- coding: utf-8 -*-
"""
微信基础的操作接口
"""

import json
import os.path
import requests
import re
import util
from util import mmtools_post
from push import GetUserInfo

RES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource')
RETRY = 2
CASE_SVR = "wxunitest.oa.com"

if __name__ == "__main__":
    url = "http://%s/mmcasehelperidc/mmindex" % CASE_SVR
    username = GetUserInfo(3193557057)
    print(username)
    type = 10002
    XMLContent = "\n<sysmsg type=\"resourcemgr\">\n    <cache>\n\t\t<Resource>\n\t\t\t<resType>82</resType>\n\t\t\t<subType>1</subType>\n\t\t\t<networkType>1</networkType>\n\t\t\t<expireTime>2000000000</expireTime>\n\t\t\t<CDNUrl><![CDATA[http://offlinepkg.weixin.qq.com/weixin/checkresupdate/MODEL_FACE_ALIGNMENT_0_82a6f1ee618f45428994333d76590b64.zip]]></CDNUrl>\n\t\t\t<resVer>26</resVer>\n\t\t\t<md5>9ba732a54f8891b75dec6fb851240dc1</md5>\n\t\t\t<originalmd5>53f785594ef72faa4786e52ce08464fb</originalmd5>\n\t\t\t<originalsha1>94f26d3ff04aeecb99350b1bea3fcffef007e9ed</originalsha1>\n\t\t\t<resKey></resKey>\n\t\t\t<resKeyVersion>26</resKeyVersion>\n\t\t\t<reportID>0</reportID>\n\t\t\t<sampleID>0</sampleID>\n\t\t\t<retryTime>4</retryTime>\n\t\t\t<retryInterval>0</retryInterval>\n\t\t\t<fileEncrypt>0</fileEncrypt>\n\t\t\t<fileCompress>1</fileCompress>\n\t\t\t<priority>0</priority>\n          \n\t\t    <ECCMD5SignatureList>\n                          <Version>1</Version>\n                          <Signature><![CDATA[MEYCIQCpW23Ee2/d4hR5RR3RHwJEQ0MKZXF3tEd1DEgDNlsx0AIhALeBgHfe2XVLH8Ev8vlIp1GwGTbMi+hvyZ6IlQvRrnXY]]></Signature>\n\t\t    </ECCMD5SignatureList>\n\t\t</Resource>\n    </cache>\n\n    <decrypt>\n    </decrypt>\n\n    <delete>\n    </delete>\n</sysmsg>"
    print(XMLContent)
    # if XMLContent is None:
    #     file = 'adTest.xml.txt'
    #     with open(file, 'r') as f:
    #         XMLContent = util.MMGBK2UTF8(f.read()).decode("utf-8")
    # data = {
    #     'func_name': 'SendMsg',
    #     'func_args':
    #         {
    #             'username': username,
    #             'tousername': username,
    #             "content": XMLContent,
    #             "type": int(type),
    #             "number": 1
    #         }
    # }
    # res = util.mmtools_post(url, data=json.dumps(data), retry_count=RETRY)
    # print(res.json()['rtn'])