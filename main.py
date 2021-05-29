import sys
import pyperclip

from github_utils import get_prs_request
from network_utils import set_auth_token
from slack_utils import create_greetings_message


# currently config is not being passed, can be added later with
# command line args support
def fetch_valid_rmsv2_prs(config=None):
    if config is None:
        config = {
            'label': ['rmsv2'],
            '-label': ['dont_merge', 'changes_requested'],
            'draft': 'false'
        }

    r = get_prs_request('sentieo_web', config)

    valid_prs = []
    if 'items' in r.json():
        valid_prs = r.json()['items']
    return valid_prs


def main(argv):
    print("args is ", argv)
    try:
        auth_token = argv[1]
    except IndexError:
        auth_token = None
    set_auth_token(auth_token)
    valid_prs = fetch_valid_rmsv2_prs()
    greetings_message = create_greetings_message(valid_prs)
    pyperclip.copy(greetings_message)
    print("greetings message is ", greetings_message)


if __name__ == '__main__':
    main(sys.argv)
