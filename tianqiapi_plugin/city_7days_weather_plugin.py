#!/usr/bin/env python
# --coding:utf-8--
import requests
import pandas as pd


def translate(rsp_dict: object):
    result = []
    for row in rsp_dict['data']:
        elem = {
            'cityid': rsp_dict['cityid'],
            'update_time': rsp_dict['update_time'],
            'city': rsp_dict['city'],
            'cityEn': rsp_dict['cityEn']
            }
        elem.update(row)
        result.append(elem)
    return result


def city_7days_weather_plugin(params, load_functions, save_functions):
    APP_ID = params['app_id']
    APP_SECRET = params['app_secret']
    CITY = params['city']
    url = f'https://tianqiapi.com/api?version=v1&appid={APP_ID}&appsecret={APP_SECRET}&city={CITY}'
    df = pd.DataFrame(translate(requests.get(url).json()))
    save_functions['output1'](df.astype({
        'alarm': str,
        'win': str,
        'hours': str,
        'index': str
    }))
