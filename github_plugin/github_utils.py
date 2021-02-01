import requests


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
        yield data
