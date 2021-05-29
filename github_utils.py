repos = {
    "sentieo_web": 'sentieoweb'
}


def get_base_url():
    return 'https://api.github.com/repos/usernames'


def get_pulls_url(repo):
    return get_base_url() + '/%s/pulls' % repo


def get_pull_requests(repo):
    pulls_url = get_pulls_url(repo)
    print("requested pulls url is ", pulls_url)
    return pulls_url
