import sys

from github_utils import repos, get_prs_request
from network_utils import set_auth_token


def main(argv):
    print("args is ", argv)
    try:
        auth_token = argv[1]
    except IndexError:
        auth_token = None
    set_auth_token(auth_token)
    r = get_prs_request(repos['sentieo_web'])


if __name__ == '__main__':
    main(sys.argv)
