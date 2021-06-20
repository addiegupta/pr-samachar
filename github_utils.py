import json
import os

from date_utils import get_string_from_date
from helper_utils import query_params_to_string
from network_utils import get_request

github_auth_token = 'invalid'

dirname = os.path.dirname(__file__)
config_filename = os.path.join(dirname, 'config.json')
config_store = json.load(open(config_filename))


def get_repos():
    return config_store['repos'].keys()


def set_github_pat(token):
    global github_auth_token
    if token is not None:
        github_auth_token = token


# returns full repo name (organisation/repo)
def get_full_repo(repo):
    return config_store['organisation'] + '/' + repo


def get_base_url():
    return 'https://api.github.com'


def get_pull_details_url(repo, pr_num):
    return get_base_url() + '/repos/' + get_full_repo(repo) + '/pulls/' + str(pr_num)


def get_search_url():
    return get_base_url() + '/search/issues'


def fetch_eod_prs_for_repo(repo, last_eod_date):
    date_qualifiers = ['created', 'merged']
    results = {}
    for date_qualifier in date_qualifiers:
        r = get_eod_prs_request(repo, date_qualifier, last_eod_date)
        if r is None:
            return None
        if 'items' in r.json():
            results[date_qualifier] = r.json()['items']

    return results


def fetch_prs_for_repo(repo):
    print("\nFetching pull requests for: ", repo)
    r = get_prs_request(repo)

    valid_prs = []
    if 'items' in r.json():
        valid_prs = r.json()['items']
        for pr in valid_prs:
            pr_num = pr['number']
            r = get_pr_details_request(repo, pr_num)
            data = r.json()
            if data:
                pr['additions'] = data['additions']
                pr['deletions'] = data['deletions']
                pr['changed_files'] = data['changed_files']
    return valid_prs


def get_pr_details_request(repo, pr_num):
    pull_details_url = get_pull_details_url(repo, pr_num)
    return get_request(pull_details_url, github_auth_token)


def get_prs_request(repo, query_params={}, is_eod=False):
    pulls_url = get_search_url()
    repo_config = config_store['repos'][repo]

    if is_eod:
        if 'eod' not in repo_config:
            return None
        repo_config = repo_config['eod']

    qualifiers = ['state', 'draft', 'type']

    for qualifier in qualifiers:
        if qualifier in repo_config:
            query_params[qualifier] = repo_config[qualifier]

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


def get_eod_prs_request(repo, date_qualifier, last_eod_date):
    query_params = {}

    date_string = get_string_from_date(last_eod_date)
    query_params[date_qualifier] = '>' + date_string

    return get_prs_request(repo, query_params, True)
