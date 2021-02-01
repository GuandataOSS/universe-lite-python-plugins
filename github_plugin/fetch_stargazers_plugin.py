import pandas as pd
from github_utils import paginate


def fetch_stargazers(repo, token=None):
    headers = {
        'Authorization': 'token {}'.format(token),
        'Accept': 'application/vnd.github.v3.star+json'
    }
    url = "https://api.github.com/repos/{}/stargazers".format(repo)
    for stargazers in paginate(url, headers):
        # flatten json into more columns
        result = []
        for d in stargazers:
            d['user']['starred_at'] = d['starred_at']
            result.append(d['user'])
        yield from result


def fetch_stargazers_plugin(params, load_functions, save_functions):
    stargazers = fetch_stargazers(params['repo'], params['token'])
    df = pd.DataFrame(stargazers).astype('str')
    save_functions['output1'](df)
