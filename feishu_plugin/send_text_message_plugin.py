#!/usr/bin/env python
# --coding:utf-8--
import requests
from functools import lru_cache
import time


@lru_cache()
def get_tenant_access_token(APP_ID, APP_SECRET, ttl_hash=None):
    print('try to get tenant access token')
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    r = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
        json=payload
    )

    rsp_dict = r.json()
    print('dict', rsp_dict)

    code = rsp_dict.get("code", -1)
    if code != 0:
        print("get tenant_access_token error, code =", code)
        return ""
    return rsp_dict.get("tenant_access_token", "")


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


def send_text_message_plugin(params, load_functions, save_functions):
    app_id = params['app_id']
    app_secret = params['app_secret']
    token = get_tenant_access_token(app_id, app_secret)

    open_id = params['open_id']
    text = params['text']
    content_obj = {"content": {'text': text}}

    url = "https://open.feishu.cn/open-apis/message/v4/send/"

    headers = {
        "Authorization": "Bearer " + token
    }
    payload = {
        "open_id": open_id,
        "msg_type": "text",
        **content_obj
    }

    r = requests.post(
        url,
        json=payload,
        headers=headers
    )

    rsp_dict = r.json()
    code = rsp_dict.get("code", -1)
    if code != 0:
        raise str("send message error, code = ", code, ", msg =", rsp_dict.get("msg", ""))
