# 原始代码版权信息
# Copyright (C) 2025 7aGiven
# 
# 此代码基于Phigros_Resource修改而来，该项目遵循GNU通用公共许可证v3.0
# 本程序是自由软件：您可以在自由软件基金会发布的GNU通用公共许可证v3.0条款下重新分发和/或修改它
# 
# 修改者：ziyangdev910
# 修改日期：2026-01-09

import hashlib
from http.client import HTTPSConnection
import json
import random
import string
import time
import urllib.parse
import uuid

sample = string.ascii_lowercase + string.digits

def taptap(appid):
    uid = uuid.uuid4()
    X_UA = "V=1&PN=TapTap&VN=2.40.1-rel.100000&VN_CODE=240011000&LOC=CN&LANG=zh_CN&CH=default&UID=%s&NT=1&SR=1080x2030&DEB=Xiaomi&DEM=Redmi+Note+5&OSV=9" % uid
    
    conn = HTTPSConnection("api.taptapdada.com")
    conn.request(
        "GET",
        "/app/v2/detail-by-id/%d?X-UA=%s" % (appid, urllib.parse.quote(X_UA)),
        headers={"User-Agent": "okhttp/3.12.1"}
    )
    r = json.load(conn.getresponse())
    # print(r["data"]["download"])
    apkid = r["data"]["download"]["apk_id"]

    # print("")

    nonce = "".join(random.sample(sample, 5))
    t = int(time.time())
    param = "abi=arm64-v8a,armeabi-v7a,armeabi&id=%d&node=%s&nonce=%s&sandbox=1&screen_densities=xhdpi&time=%s" % (apkid, uid, nonce, t)
    byte = "X-UA=%s&%sPeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs" % (X_UA, param)
    md5 = hashlib.md5(byte.encode()).hexdigest()
    body = "%s&sign=%s" % (param, md5)

    conn.request(
        "POST",
        "/apk/v1/detail?X-UA=" + urllib.parse.quote(X_UA),
        body=body.encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "okhttp/3.12.1"}
    )
    r = json.load(conn.getresponse())
    # print(r)
    return r['data']['apk']['download']

# Phigros app id = 165287
if __name__ == "__main__":
    print(taptap(165287))

