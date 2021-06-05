import json
from datetime import datetime
import os

from network_utils import post_request

slack_oauth_token = None

dirname = os.path.dirname(__file__)
slack_filename = os.path.join(dirname, 'slack_store.json')
slack_store = json.load(open(slack_filename))
date_time_format = '%Y-%m-%dT%H:%M:%SZ'

# To display only emoji for the day; else include all till stale limit
single_emoji_mode = True


def get_base_url():
    return 'https://slack.com/api'


def get_post_message_url():
    return get_base_url() + '/chat.postMessage'


def set_slack_token(token):
    global slack_oauth_token
    slack_oauth_token = token


def emojify(emoji_key):
    return ':%s:' % emoji_key


def get_emoji_for_number(num):
    if num < 10:
        return emojify(slack_store['numeral_to_text_map'][str(num)])
    else:
        a = num // 10
        b = num % 10
        return get_emoji_for_number(a) + get_emoji_for_number(b)


def get_labels_info(pr):
    pr_labels = []
    for label in pr['labels']:
        pr_label = label['name']

        if label['color'] in slack_store['label_emoji']:
            pr_label += emojify(slack_store['label_emoji'][label['color']])

        pr_labels.append(pr_label)

    return ', '.join(pr_labels)


def get_days_since_pr_creation(pr):
    # date received from api is in utc
    created_date = datetime.strptime(pr['created_at'], date_time_format)
    date_now = datetime.utcnow()
    return (date_now - created_date).days


def get_pr_status_message(pr):
    pr_status_store = slack_store['pr_status']

    # obtain days since creation of this pr
    stale_pr_limit = int(slack_store['stale_pr_days'])
    days_since_creation = get_days_since_pr_creation(pr)

    # should not exceed max dict length of pr status
    days_for_status = min(days_since_creation, len(pr_status_store) - 1)

    pr_stale = days_since_creation >= stale_pr_limit
    pr_health = pr_status_store[days_for_status]['health']
    pr_age_emoji = get_emoji_for_number(days_since_creation)

    # if days since creation is less than pr stale limit, emojis shown from day 0 to day stale in reverse (positive
    # emojis) else emojis from day of being stale till number of days (negative emojis)
    emoji_start = stale_pr_limit if pr_stale else days_for_status
    emoji_end = days_for_status + 1 if pr_stale else stale_pr_limit
    pr_emojis = []

    if single_emoji_mode:
        pr_emojis.append(pr_status_store[days_for_status]['emoji'])
    else:
        for i in range(emoji_start, emoji_end):
            pr_emojis.append(pr_status_store[i]['emoji'])

    if not pr_stale:
        pr_emojis.reverse()

    return '_Health_: %s %s %s' % (pr_age_emoji, pr_health, ' '.join(emojify(emoji) for emoji in pr_emojis))


def get_pr_header_text(pr, i):
    pr_title = pr['title']
    pr_author = pr['user']['login']
    return '\n%s) *%s* by %s' % (
        i + 1, pr_title, pr_author)


def get_pr_details_text(pr):
    pr_labels = get_labels_info(pr)
    pr_status = get_pr_status_message(pr)
    return '\n\t_Labels_: %s\n\t%s' % (
        pr_labels, pr_status)


def get_pr_message_text(pr, i):
    pr_header_text = get_pr_header_text(pr, i)
    pr_details_text = get_pr_details_text(pr)
    pr_url = pr['html_url']
    return '%s%s\n\t%s\n\n' % (
        pr_header_text, pr_details_text, pr_url)


def get_top_header_text(prs):
    prs_available = len(prs) > 0
    reviewers = ', '.join(slack_store['reviewers'].values())

    salutation = slack_store['message_template']['salutation'] % reviewers
    message_status_key = 'prs_available' if prs_available else 'prs_not_available'
    message_status = slack_store['message_template'][message_status_key]

    if prs_available:
        message_status = message_status % len(prs)

    mention_template = '@%s'
    if can_send_slack():
        mention_template = '<!%s>'

    username_mention = mention_template % slack_store['message_template']['user_mention']

    return '\n'.join([salutation, message_status, username_mention])


def create_reminder_message(valid_prs):
    top_header_text = get_top_header_text(valid_prs)
    pr_message_body = ''

    for i, pr in enumerate(valid_prs):
        pr_message_body += get_pr_message_text(pr, i)

    return '\n'.join([top_header_text, pr_message_body])


def send_to_slack(message):
    slack_url = get_post_message_url()
    for channel_name in slack_store['channels']:
        channel_id = slack_store['channels'][channel_name]
        body = {
            'channel': channel_id,
            'text': message
        }
        post_request(slack_url, slack_oauth_token, body)


def can_send_slack():
    return slack_oauth_token is not None
