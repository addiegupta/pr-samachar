from helper_utils import query_params_to_string
from network_utils import get_request
import json
import os

github_auth_token = 'invalid'

dirname = os.path.dirname(__file__)
github_filename = os.path.join(dirname, 'github_store.json')
github_store = json.load(open(github_filename))


def get_repos():
    return github_store['repos'].keys()


def set_github_pat(token):
    global github_auth_token
    if token is not None:
        github_auth_token = token


# returns full repo name (organisation/repo)
def get_full_repo(repo):
    return github_store['organisation'] + '/' + repo


def get_base_url():
    return 'https://api.github.com'


def get_search_url():
    return get_base_url() + '/search/issues'


def fetch_prs_for_repo(repo):
    print("\nFetching pull requests for: ", repo)
    r = get_prs_request(repo)

    valid_prs = []
    if 'items' in r.json():
        valid_prs = r.json()['items']
    return valid_prs


def get_prs_request(repo):
    query_params = {}
    pulls_url = get_search_url()
    repo_config = github_store['repos'][repo]

    if repo_config['only_prs']:
        query_params['is'] = []
        query_params['is'].append('pr')

    if repo_config['only_open']:
        query_params['is'].append('open')

    if 'draft' in repo_config:
        query_params['draft'] = repo_config['draft']

    query_params['repo'] = get_full_repo(repo)

    label_keys = {'labels': 'label', 'excluded_labels': '-label'}
    for json_key, query_key in label_keys.items():
        if json_key in repo_config:
            query_params[query_key] = []
            for i in range(len(repo_config[json_key])):
                query_params[query_key].append(repo_config[json_key][i])

    print("\nPR criteria: ", query_params)
    payload = repo_config['config']
    payload['q'] = query_params_to_string(query_params)

    return get_request(pulls_url, github_auth_token, payload)
