import sys

from github_utils import get_prs_request
from network_utils import set_auth_token


def fetch_rmsv2_prs():
    r = get_prs_request('sentieo_web')


def main(argv):
    print("args is ", argv)
    try:
        auth_token = argv[1]
    except IndexError:
        auth_token = None
    set_auth_token(auth_token)
    fetch_rmsv2_prs()


if __name__ == '__main__':
    main(sys.argv)
