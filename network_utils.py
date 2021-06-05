import requests
import logging


def basic_request(url, auth_token, payload, mode):
    header_dict = {'Authorization': 'Bearer ' + auth_token}

    # Uncomment to enable logging
    # logging.basicConfig(level=logging.DEBUG)

    if mode is 'get':
        r = requests.get(url, headers=header_dict, params=payload)
    elif mode is 'post':
        r = requests.post(url, headers=header_dict, params=payload)

    print('\nresponse is ', r)
    return r


def get_request(url, auth_token, payload={}):
    return basic_request(url, auth_token, payload, 'get')


def post_request(url, auth_token, payload={}):
    return basic_request(url, auth_token, payload, 'post')
