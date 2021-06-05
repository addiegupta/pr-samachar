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


# obtain days since creation of this pr
def get_days_since_pr_creation(pr):
    # date received from api is in utc
    created_date = datetime.strptime(pr['created_at'], date_time_format)
    date_now = datetime.utcnow()
    return (date_now - created_date).days


def get_day_count_for_pr_status(pr):
    days_since_creation = get_days_since_pr_creation(pr)

    # should not exceed max dict length of pr status
    days_for_status = min(days_since_creation, len(slack_store['pr_status']) - 1)
    return days_for_status


def get_emoji_string_for_pr(pr, single_mode=single_emoji_mode):
    pr_status_store = slack_store['pr_status']

    stale_pr_limit = int(slack_store['stale_pr_days'])
    days_since_creation = get_days_since_pr_creation(pr)

    days_for_status = get_day_count_for_pr_status(pr)

    pr_stale = days_since_creation >= stale_pr_limit

    # if days since creation is less than pr stale limit, emojis shown from day 0 to day stale in reverse (positive
    # emojis) else emojis from day of being stale till number of days (negative emojis)
    emoji_start = stale_pr_limit if pr_stale else days_for_status
    emoji_end = days_for_status + 1 if pr_stale else stale_pr_limit
    pr_emojis = []

    if single_mode:
        pr_emojis.append(pr_status_store[days_for_status]['emoji'])
    else:
        for i in range(emoji_start, emoji_end):
            pr_emojis.append(pr_status_store[i]['emoji'])

    if not pr_stale:
        pr_emojis.reverse()

    return ' '.join(emojify(emoji) for emoji in pr_emojis)


def get_pr_status_message(pr):
    pr_status_store = slack_store['pr_status']

    days_since_creation = get_days_since_pr_creation(pr)

    days_for_status = get_day_count_for_pr_status(pr)

    pr_health = pr_status_store[days_for_status]['health']
    pr_age_emoji = get_emoji_for_number(days_since_creation)

    if can_send_slack():
        # ignore emoji for slack block message, will be added to button
        emoji_string = ''
    else:
        emoji_string = get_emoji_string_for_pr(pr)

    return '_Health_: %s %s %s' % (pr_age_emoji, pr_health, emoji_string)


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

    return '%s%s\n' % (pr_header_text, pr_details_text)


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


def get_section_block():
    return {"type": "section"}


def get_text_section(text):
    section = get_section_block()
    section['text'] = {
        "type": 'mrkdwn',
        "text": text
    }
    return section


def get_image_accessory(url, alt_text):
    return {
        "type": "image",
        "image_url": url,
        "alt_text": alt_text
    }


def get_divider_block():
    return {"type": "divider"}


def get_button_element(text, url):
    return {
        'type': 'button',
        'text': {
            'type': 'plain_text',
            'text': text
        },
        'url': url,
        'style': 'primary'
    }


def get_button_block(text, url):
    return {
        "type": "actions",
        'elements': [
            get_button_element(text, url)
        ]
    }


def get_content_blocks(valid_prs, top_header_text=None):
    blocks = []
    if top_header_text:
        blocks.append(get_text_section(top_header_text))

    for i, pr in enumerate(valid_prs):
        pr_url = pr['html_url']
        pr_author = pr['user']['login']
        pr_message = get_pr_message_text(pr, i)

        section = get_text_section(pr_message)

        section['accessory'] = get_image_accessory(pr['user']['avatar_url'], pr_author)

        blocks.append(section)
        emoji_string = get_emoji_string_for_pr(pr, True)  # emoji in button can only support single emoji
        button_block = get_button_block('Open PR ' + emoji_string, pr_url)
        blocks.append(button_block)
        blocks.append(get_divider_block())

    return blocks


def create_reminder_message(valid_prs):
    top_header_text = get_top_header_text(valid_prs)
    pr_message_body = ''

    for i, pr in enumerate(valid_prs):
        pr_message = get_pr_message_text(pr, i)
        pr_url = pr['html_url']
        pr_message_body += '%s\t%s\n\n' % (pr_message, pr_url)

    return '\n'.join([top_header_text, pr_message_body])


def create_reminder_message_for_slack(valid_prs):
    top_header_text = get_top_header_text(valid_prs)
    content_blocks = get_content_blocks(valid_prs, top_header_text)

    return top_header_text, content_blocks


def send_to_slack(message, blocks):
    slack_url = get_post_message_url()
    for channel_name in slack_store['channels']:
        channel_id = slack_store['channels'][channel_name]
        body = {
            'channel': channel_id,
            'text': message,  # fallback for notification etc.
            'blocks': str(blocks)
        }
        post_request(slack_url, slack_oauth_token, body)


def can_send_slack():
    return slack_oauth_token is not None
