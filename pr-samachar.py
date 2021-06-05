#!/usr/bin/python3
import pyperclip
import argparse

from github_utils import set_github_pat, fetch_prs_for_repo, get_repos
from slack_utils import create_reminder_message, set_slack_token, send_to_slack, can_send_slack, \
    create_reminder_message_for_slack


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gpat', help="GitHub personal access token")
    parser.add_argument('slacktoken', nargs='?', default=None, help="Slack OAuth token")

    args = parser.parse_args()

    # set GitHub personal access token as auth token
    set_github_pat(args.gpat)
    set_slack_token(args.slacktoken)

    repos = get_repos()
    for repo in repos:
        valid_prs = fetch_prs_for_repo(repo)

        if can_send_slack():
            reminder_text, reminder_blocks = create_reminder_message_for_slack(valid_prs)
            send_to_slack(reminder_text, reminder_blocks)
            print("\nMessage has been sent to slack!")

        else:
            reminder_message = create_reminder_message(valid_prs)

            print("\nReminder message is:\n",
                  reminder_message[:200] + '...' if len(reminder_message) > 202 else reminder_message)
            pyperclip.copy(reminder_message)
            print("\nMessage has been copied to clipboard!")


if __name__ == '__main__':
    main()
