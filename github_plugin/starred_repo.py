import requests
import pandas as pd


def paginate(url, headers=None):
    while url:
        response = requests.get(url, headers=headers)
        # For HTTP 204 no-content this yields an empty list
        if response.status_code == 204:
            return
        data = response.json()
        if isinstance(data, dict) and data.get("message"):
            raise response
        try:
            url = response.links.get("next").get("url")
        except AttributeError:
            url = None
        result = []
        for d in data:
            d['repo']['starred_at'] = d['starred_at']
            result.append(d['repo'])
        yield result


def fetch_all_starred(username=None, token=None):
    headers = {
        'Authorization': 'token {}'.format(token),
        'Accept': 'application/vnd.github.v3.star+json'
    }
    url = "https://api.github.com/users/{}/starred".format(username)
    for stars in paginate(url, headers):
        yield from stars


def starred_repo(params, load_functions, save_functions):
    stars = fetch_all_starred(params['username'], params['token'])
    df = pd.DataFrame(stars).astype('str')
    save_functions['output1'](df)
