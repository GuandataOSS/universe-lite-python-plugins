import pandas as pd
from github_utils import paginate


def fetch_all_starred(username=None, token=None):
    headers = {
        'Authorization': 'token {}'.format(token),
        'Accept': 'application/vnd.github.v3.star+json'
    }
    url = "https://api.github.com/users/{}/starred".format(username)
    for stars in paginate(url, headers):
        # flatten json into more columns
        result = []
        for d in stars:
            d['repo']['starred_at'] = d['starred_at']
            d['repo']['starred_by'] = username
            result.append(d['repo'])
        yield from result


def fetch_all_starred_plugin(params, load_functions, save_functions):
    stars = fetch_all_starred(params['username'], params['token'])
    df = pd.DataFrame(stars).astype('str')
    save_functions['output1'](df)
