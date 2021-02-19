import pandas as pd
import requests
import logging


def paginate(headers, bodyFunc):
    url = "https://api.github.com/graphql"
    endCursor = "first: 100"
    while endCursor:
        response = requests.post(url, json ={'query': bodyFunc(endCursor)}, headers=headers)
        # For HTTP 204 no-content this yields an empty list
        if response.status_code == 204:
            return
        try:
            data = response.json()
        except ValueError:
            logging.error('error: github return wrong data. ' + response.text)
            return
        if isinstance(data, dict) and data.get("message"):
            logging.error('encounter wrong data: ' + response.text)
            return
        #
        # sometimes, it will error, and the data will be:
        #  {
        #    'data': {'user': None},
        #    'errors': [
        #      {'type': 'NOT_FOUND',
        #      'path': ['user'],
        #      'locations': [{'line': 3, 'column': 7}],
        #      'message': "Could not resolve to a User with the login of '***'."
        #      }
        #     ]
        # }
        if isinstance(data, dict) and data.get("errors"):
            logging.error('encounter wrong data: ' + response.text)
            return
        try:
            endCursor = None
            if data['data']['user']['starredRepositories']['pageInfo']['hasNextPage']:
                endCursor = 'first: 100, after:"' + data['data']['user']['starredRepositories']['pageInfo']['endCursor'] + '"'
        except AttributeError:
            endCursor = None
        yield data['data']['user']['starredRepositories']['edges']


def fetch_all_starred(username=None, token=None):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept': 'Accept-Encoding: deflate, gzip'
    }
    bodyFunc = lambda next_filter: '''
    query {
      user(login: "''' + username + '''") {
      	starredRepositories(''' + next_filter + ''') {
      	  edges{
            node {
              id,
              name,
              nameWithOwner,
              isFork,
              isArchived,
              isDisabled,
              forkCount,
              stargazerCount,
              diskUsage,
              description,
              licenseInfo {
                key
              }
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

    for stars in paginate(headers, bodyFunc):
        # flatten json into more columns
        result = []
        try:
            for d in stars:
                if not d:
                    logging.error('encountered none')
                    continue
                d['node']['starredAt'] = d['starredAt']
                if (d['node']['licenseInfo'] and 'key' in d['node']['licenseInfo']):
                    d['node']['licenseKey'] = d['node']['licenseInfo']['key']
                else:
                    d['node']['licenseKey'] = None
                del d['node']['licenseInfo']
                d['node']['starredBy'] = username
                result.append(d['node'])
        except Exception:
            logging.error('encountered unknown exception')
        yield from result


def fetch_all_starred_plugin(params, load_functions, save_functions):
    stars = fetch_all_starred(params['username'], params['token'])
    df = pd.DataFrame(stars).astype('str')
    save_functions['output1'](df)
