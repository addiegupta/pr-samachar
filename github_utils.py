from helper_utils import query_params_to_string
from network_utils import get_request

organisation = 'usernames'
repos = {
    "sentieo_web": organisation + '/sentieoweb'
}


def get_base_url():
    return 'https://api.github.com'


def get_search_url():
    return get_base_url() + '/search/issues'


def get_prs_request(repo, query_params={}):
    pulls_url = get_search_url()
    query_params['is'] = 'pr'
    query_params['repo'] = repo
    payload = {'q': query_params_to_string(query_params)}
    return get_request(pulls_url, payload)
