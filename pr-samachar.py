#!/usr/bin/python3
import pyperclip
import argparse

from date_utils import get_string_from_date, get_utc_now
from file_utils import get_last_eod_script_date, write_to_eod_file
from github_utils import set_github_pat, fetch_prs_for_repo, get_repos, fetch_eod_prs_for_repo
from slack_utils import create_reminder_message, set_slack_token, send_to_slack, can_send_slack, \
    create_reminder_message_for_slack, create_eod_report_message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gpat', help="GitHub personal access token")
    parser.add_argument('slacktoken', nargs='?', default=None, help="Slack OAuth token")
    parser.add_argument('-e', '--eod', action='store_true',
                        help="generates end of day report")

    args = parser.parse_args()

    eod_mode = args.eod
    # set GitHub personal access token as auth token
    set_github_pat(args.gpat)
    set_slack_token(args.slacktoken)

    repos = get_repos()

    if eod_mode:
        last_eod_date = get_last_eod_script_date()
        for repo in repos:
            prs_dict = fetch_eod_prs_for_repo(repo, last_eod_date)
            if prs_dict is None:
                print("\nEOD config not found for repo: ", repo)
                continue

            # can add block sections formatted message for slack later (just like for normal reminder mode)
            eod_report_message = create_eod_report_message(prs_dict, last_eod_date)
            print("\nEOD Report message is:\n",
                  eod_report_message[:200] + '...' if len(eod_report_message) > 202 else eod_report_message)

            if can_send_slack():
                send_to_slack(eod_report_message, repo)
                print("\nMessage has been sent to slack!")

            else:
                pyperclip.copy(eod_report_message)
                print("\nMessage has been copied to clipboard!")

        # write current time for next eod execution
        write_to_eod_file(get_string_from_date(get_utc_now()))

    else:
        for repo in repos:
            valid_prs = fetch_prs_for_repo(repo)

            if can_send_slack():
                reminder_text, reminder_blocks = create_reminder_message_for_slack(valid_prs, repo)
                send_to_slack(reminder_text, repo, reminder_blocks)
                print("\nMessage has been sent to slack!")

            else:
                reminder_message = create_reminder_message(valid_prs, repo)

                print("\nReminder message is:\n",
                      reminder_message[:200] + '...' if len(reminder_message) > 202 else reminder_message)
                pyperclip.copy(reminder_message)
                print("\nMessage has been copied to clipboard!")


if __name__ == '__main__':
    main()
