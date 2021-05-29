import json
from datetime import datetime

slack_store_file = open('./slack_store.json')
slack_store = json.load(slack_store_file)
date_time_format = '%Y-%m-%dT%H:%M:%SZ'


def emojify(emoji_key):
    return ':%s:' % emoji_key


def get_labels_info(pr):
    pr_labels = []
    for label in pr['labels']:
        pr_label = label['name']

        if label['color'] in slack_store['label_emoji']:
            pr_label += emojify(slack_store['label_emoji'][label['color']])

        pr_labels.append(pr_label)

    return ', '.join(pr_labels)


def get_pr_status_message(pr):
    pr_status_store = slack_store['pr_status']

    # obtain days since creation of this pr
    # date received from api is in utc
    stale_pr_limit = int(slack_store['stale_pr_days'])
    created_date = datetime.strptime(pr['created_at'], date_time_format)
    date_now = datetime.utcnow()
    days_since_creation = (date_now - created_date).days

    # should not exceed max dict length of pr status
    days_since_creation = min(days_since_creation, len(pr_status_store) - 1)

    # if days since creation is less than pr stale limit, emojis shown from day 0 to day stale in reverse (positive
    # emojis) else emojis from day of being stale till number of days (negative emojis)
    # pr_status_index = days_since_creation
    pr_stale = days_since_creation >= stale_pr_limit
    pr_health = pr_status_store[days_since_creation]['health']
    emoji_start = stale_pr_limit if pr_stale else days_since_creation
    emoji_end = days_since_creation + 1 if pr_stale else stale_pr_limit
    pr_emojis = []

    for i in range(emoji_start, emoji_end):
        pr_emojis.append(pr_status_store[i]['emoji'])

    if not pr_stale:
        pr_emojis.reverse()

    return '_Health_: %s %s' % (pr_health, ' '.join(emojify(emoji) for emoji in pr_emojis))


def create_greetings_message(valid_prs):
    prs_available = len(valid_prs) > 0
    reviewers = ', '.join(slack_store['reviewers'].values())

    salutation = slack_store['message_template']['salutation'] % reviewers
    message_status_key = 'prs_available' if prs_available else 'prs_not_available'
    message_status = slack_store['message_template'][message_status_key]

    if prs_available:
        message_status = message_status % len(valid_prs)

    pr_message_body = ''

    for i, pr in enumerate(valid_prs):
        pr_title = pr['title']
        pr_author = pr['user']['login']
        pr_url = pr['html_url']
        pr_labels = get_labels_info(pr)
        pr_status = get_pr_status_message(pr)
        pr_message = '\n%s)  *%s* by %s\n\t_Labels_: %s %s\n\t%s\n\n' % (
            i + 1, pr_title, pr_author, pr_labels, pr_status, pr_url)
        pr_message_body += pr_message

    return '\n'.join([salutation, message_status, pr_message_body])
