import requests
import logging

auth_token = 'invalid'


def set_auth_token(token):
    global auth_token
    if token is not None:
        auth_token = token


def get_request(url, payload={}):
    header_dict = {'Authorization': 'token ' + auth_token}

    # Uncomment to enable logging
    # logging.basicConfig(level=logging.DEBUG)

    r = requests.get(url, headers=header_dict, params=payload)
    print('\nresponse is ', r)
    return r
