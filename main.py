import sys

from github_utils import get_prs_request
from network_utils import set_auth_token


def fetch_mergeable_rmsv2_prs(config=None):
    # currently config is not being passed, can be added later with
    # command line args support
    if config is None:
        config = {
            'label': ['rmsv2'],
            '-label': ['dont_merge', 'changes_requested'],
            'draft': 'false'
        }

    r = get_prs_request('sentieo_web', config)
    print('result is ', r.json())


def main(argv):
    print("args is ", argv)
    try:
        auth_token = argv[1]
    except IndexError:
        auth_token = None
    set_auth_token(auth_token)
    fetch_mergeable_rmsv2_prs()


if __name__ == '__main__':
    main(sys.argv)
