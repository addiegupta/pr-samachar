from helper_utils import query_params_to_string
from network_utils import get_request
import json
import os

github_auth_token = 'invalid'

dirname = os.path.dirname(__file__)
github_filename = os.path.join(dirname, 'github_store.json')
github_store = json.load(open(github_filename))


def set_github_pat(token):
    global github_auth_token
    if token is not None:
        github_auth_token = token


# returns full repo name (organisation/repo)
def get_full_repo(repo):
    return github_store['organisation'] + '/' + github_store['repos'][repo]


def get_base_url():
    return 'https://api.github.com'


def get_search_url():
    return get_base_url() + '/search/issues'


def get_prs_request(repo, query_params={}):
    pulls_url = get_search_url()
    query_params['is'] = 'pr'
    query_params['is'] = 'open'
    query_params['repo'] = get_full_repo(repo)

    label_keys = ['label', '-label']
    for key in label_keys:
        if key in query_params:
            for i, v in enumerate(query_params[key]):
                query_params[key][i] = github_store['labels'][v]

    # by default per_page is 30, max is 100
    payload = {
        'q': query_params_to_string(query_params),
        'sort': 'created',
        'order': 'asc',
        'per_page': 40
    }

    return get_request(pulls_url, github_auth_token, payload)
