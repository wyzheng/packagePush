import json
import logging
import os.path
import requests
import re
import util

URL = "http://package.weixin.oa.com/package/json/list/?page=1&type=mmpackageconfig_type_27"

COOKIES = {
        "pkgsvr_sessionid": "tk4qxf80tsdq1adi7oljgg1s7qj8ikar"
    }

def get_id(versionId):
    res = requests.get(url=URL, cookies=COOKIES)
    if res.status_code != 200:
        return 500, {"message": "get file id failed! please try again!"}
    res_json = json.loads(res.content.decode())
    packages = res_json["data"]["packages"]
    id = 0
    for package_info in packages:
        if re.match(".*%s.*" % versionId, package_info["MemoName"]):
            id = package_info["ID"]
            break
    if id == 0:
        return 500, {"message": "no file id matched! please check versionId you input!"}
    return id