import requests
import json
import pandas as pd
import logging
import math


class BiTool(object):
    def __init__(self, bi_account: dict):
        """
        :param bi_account: BI 登录账户
        """
        self.home_url = bi_account["url"]
        self.domain = bi_account["domain"]
        self.email = bi_account['email']
        self.password = bi_account['password']

    def get_user_auth_token(self) -> str:
        """
        用户登录API，获取Token
        :return: 用户Token，及其过期时间
        """
        body_param = {"domain": self.domain, "email": self.email, "password": self.password}
        sign_in_url = f"{self.home_url}/public-api/sign-in"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url=sign_in_url, headers=headers, json=body_param)
        print(response.status_code)
        print(response)
        assert 200 == response.status_code

        result = json.loads(response.text)["response"]
        return result["token"]

    def upload_bi_dataset(self, df: pd.DataFrame, table_name, dsid=None, primary_keys=None, replace=False):
        """
        :param df: 上传的pd.DataFrame()
        :param dsid: BI上的数据集的dsId
        :param table_name: BI上的数据集的表名
        :param primary_keys: 主键列表；如果设置了主键，则上传时会根据主键覆盖更新
        :param replace: False表示在BI的数据集上追加上传df, True表示使用df全量替换BI上的数据集
        """
        df = df.where(df.notnull(), None)
        data = df.to_dict(orient='records')
        url = f"{self.home_url}/public-api/upload-dataset"
        headers = {"Content-Type": "application/json", "X-Auth-Token": self.get_user_auth_token()}
        for i in range(math.ceil(len(data) / 5000)):
            start = 5000 * i
            end = 5000 * (i + 1) if 5000 * (i + 1) < len(data) else len(data)
            logging.info(f'uploading index {start} to {end}')
            finish = False if end < len(data) else True
            if replace:
                overwrite = i == 0
            else:
                overwrite = False
            body = {
                "tableName": table_name,
                "overwriteExistingData": overwrite,
                "data": data[start:end],
                "batchFinish": finish
            }
            if primary_keys:
                primary_columns = list()
                for key in primary_keys:
                    primary_columns.append(
                        {
                            "name": key,
                            "isPrimaryKey": True
                        }
                    )
                body["columns"] = primary_columns
            if dsid:
                body['dsId'] = dsid
            res = requests.post(url, json=body, headers=headers).json()
            if res['result'] != 'ok':
                logging.error(f'UPLOAD ERROR, ERROR MESSAGE:{res}')
                break
        return None


def upload_bi_dataset(params: dict, load_functions, save_functions):
    bi_tool = BiTool(params)
    dsid = params['dsid'] if 'dsid' in params and params['dsid'] is not None and len(params['dsid']) > 5 else None
    bi_tool.upload_bi_dataset(load_functions['input1'](), params['table_name'], dsid, replace=params['replace'])
