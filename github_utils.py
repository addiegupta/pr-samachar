from helper_utils import query_params_to_string
from network_utils import get_request
import json

github_store_file = open('./github_store.json')
github_store = json.load(github_store_file)


def get_full_repo(repo):
    return github_store['organisation'] + '/' + github_store['repos'][repo]


def get_base_url():
    return 'https://api.github.com'


def get_search_url():
    return get_base_url() + '/search/issues'


def get_prs_request(repo, query_params={}):
    pulls_url = get_search_url()
    query_params['is'] = 'pr'
    query_params['repo'] = get_full_repo(repo)
    payload = {'q': query_params_to_string(query_params)}
    return get_request(pulls_url, payload)
