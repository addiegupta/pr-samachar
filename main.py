import pyperclip
import argparse

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

    repo = 'sentieo_web'
    print("\nFetching pull requests for: ", repo)
    print("\nPR criteria: ", config)
    r = get_prs_request(repo, config)

    valid_prs = []
    if 'items' in r.json():
        valid_prs = r.json()['items']
    return valid_prs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pat', help="GitHub personal access token is required")
    args = parser.parse_args()

    # set GitHub personal access token as auth token
    set_auth_token(args.pat)

    valid_prs = fetch_valid_rmsv2_prs()
    greetings_message = create_greetings_message(valid_prs)
    pyperclip.copy(greetings_message)
    print("\nGreetings message is:\n",
          greetings_message[:200] + '...' if len(greetings_message) > 202 else greetings_message)
    print("\nMessage has been copied to clipboard!")


if __name__ == '__main__':
    main()
