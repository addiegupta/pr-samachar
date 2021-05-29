import requests

auth_token = 'invalid'


def set_auth_token(token):
    global auth_token
    if token is not None:
        auth_token = token


def get_request(url, data={}):
    header_dict = {'Authorization': 'token ' + auth_token}
    print("header_dict is ", header_dict)
    r = requests.get(url, headers=header_dict)
    print("requested pulls url is ", url)
    print('request data is ', r)
    print('json is ', r.json())
    return r
