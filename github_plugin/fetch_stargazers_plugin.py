import pandas as pd
import requests


def paginate(headers, bodyFunc):
    url = "https://api.github.com/graphql"
    endCursor = "first: 100"
    while endCursor:
        response = requests.post(url, json ={'query': bodyFunc(endCursor)}, headers=headers)
        # For HTTP 204 no-content this yields an empty list
        if response.status_code == 204:
            return
        data = response.json()
        if isinstance(data, dict) and data.get("message"):
            raise data
        try:
            endCursor = None
            if data['data']['repository']['stargazers']['pageInfo']['hasNextPage']:
                endCursor = 'first: 100, after:"' + data['data']['repository']['stargazers']['pageInfo']['endCursor'] + '"'
        except AttributeError:
            endCursor = None
        yield data['data']['repository']['stargazers']['edges']


def fetch_stargazers(repo, token=None):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept': 'Accept-Encoding: deflate, gzip'
    }
    parts = repo.split('/')
    bodyFunc = lambda next_filter: '''
query {
  repository(owner: "''' + parts[0] + '", name: "' + parts[1] + '''") {
  	stargazers(''' + next_filter + ''') {
  	  edges{
        node {
          id,
          login,
          name,
          company,
          email,
          location
        },
        starredAt
      },
      pageInfo {
        endCursor,
        hasNextPage
      }
  	}
  }
}
'''
    for stargazers in paginate(headers, bodyFunc):
        # flatten json into more columns
        result = []
        for d in stargazers:
            d['node']['starredAt'] = d['starredAt']
            result.append(d['node'])
        yield from result


def fetch_stargazers_plugin(params, load_functions, save_functions):
    stargazers = fetch_stargazers(params['repo'], params['token'])
    df = pd.DataFrame(stargazers).astype('str')
    save_functions['output1'](df)
