from network_utils import get_request

repos = {
    "sentieo_web": 'sentieoweb'
}


def get_base_url():
    return 'https://api.github.com/repos/usernames'


def get_pulls_url(repo):
    return get_base_url() + '/%s/pulls' % repo


def get_prs_request(repo):
    pulls_url = get_pulls_url(repo)
    return get_request(pulls_url)
