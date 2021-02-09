#!/usr/bin/env python
# --coding:utf-8--
import requests
import pandas as pd


def city_now_weather_plugin(params, load_functions, save_functions):
    APP_ID = params['app_id']
    APP_SECRET = params['app_secret']
    CITY = params['city']
    url = f'https://tianqiapi.com/api?version=v6&appid={APP_ID}&appsecret={APP_SECRET}&city={CITY}'
    rsp_dict = requests.get(url).json()
    df = pd.DataFrame([rsp_dict])
    save_functions['output1'](df.astype({
        'alarm': str
    }))
