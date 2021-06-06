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

# To display tally marks for the number of days: else display day count in emojis with each digit as an emoji
day_tally_mode = True


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
    if day_tally_mode:
        emoji = get_tally_emoji_for_number(num)
    else:
        emoji = get_numeral_emoji_for_number(num)
    return emoji


def get_tally_emoji_for_number(num):
    emojis = []
    numeral_to_text_map = slack_store['numeral_to_text_map']
    factor_five = num // 5
    remainder = num % 5
    for i in range(factor_five):
        emojis.append(numeral_to_text_map[str(5)])
    if remainder is not 0:
        emojis.append(numeral_to_text_map[str(remainder)])
    return ' '.join(emojify('tally-' + emoji) for emoji in emojis)


def get_numeral_emoji_for_number(num):
    if num < 10:
        return emojify(slack_store['numeral_to_text_map'][str(num)])
    else:
        a = num // 10
        b = num % 10
        return get_numeral_emoji_for_number(a) + get_numeral_emoji_for_number(b)


def get_labels_info(pr):
    pr_labels = []
    for label in pr['labels']:
        pr_label = label['name']

        if label['color'] in slack_store['label_emoji']:
            pr_label += emojify(slack_store['label_emoji'][label['color']])

        pr_labels.append(pr_label)

    return '_Labels_: ' + ', '.join(pr_labels)


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


def get_pr_changes_message(pr):
    message = ''
    if 'additions' in pr:
        additions_string = '%s %s' % (emojify('green-plus'), str(pr['additions']))
        deletion_string = '%s %s' % (emojify('red-minus'), str(pr['deletions']))
        file_string = '%s %s' % (emojify('page_facing_up'), str(pr['changed_files']))
        message += '_Changes_: %s  %s  %s' % (additions_string, deletion_string, file_string)

    return message


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

    return '_Health_: %s %s %s' % (pr_health, emoji_string, pr_age_emoji)


def get_pr_header_text(pr, i):
    pr_title = pr['title']
    pr_author = pr['user']['login']
    return '\n%s) *%s* by %s\n' % (
        i + 1, pr_title, pr_author)


def get_pr_details_text(pr):
    pr_labels = get_labels_info(pr)
    pr_status = get_pr_status_message(pr)
    pr_changes = get_pr_changes_message(pr)
    return '\n\t%s\n\t%s\n\t%s' % (
        pr_labels, pr_changes, pr_status)


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


def get_fields_section(fields_list):
    section = get_section_block()
    section['fields'] = []
    for field in fields_list:
        section['fields'].append({
            "type": "mrkdwn",
            "text": field
        })
    return section


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


def get_button_element(text, url, style='primary'):
    return {
        'type': 'button',
        'text': {
            'type': 'plain_text',
            'text': text
        },
        'url': url,
        'style': style
    }


def get_button_block(text, url, style='primary'):
    return {
        "type": "actions",
        'elements': [
            get_button_element(text, url, style)
        ]
    }


def get_content_blocks(valid_prs, top_header_text=None):
    blocks = []
    if top_header_text:
        blocks.append(get_text_section(top_header_text))

    for i, pr in enumerate(valid_prs):
        pr_url = pr['html_url']
        pr_author = pr['user']['login']

        # not using field section for now as long text wraps to next line, didnt look good
        # pr_header = get_pr_header_text(pr, i)
        # pr_changes = get_pr_changes_message(pr)
        # pr_status = get_pr_status_message(pr)
        # pr_labels = get_labels_info(pr)
        # field_section = get_fields_section([pr_labels, pr_changes, pr_status])

        pr_message = get_pr_message_text(pr, i)

        section = get_text_section(pr_message)

        section['accessory'] = get_image_accessory(pr['user']['avatar_url'], pr_author)

        blocks.append(section)
        emoji_string = get_emoji_string_for_pr(pr, True)  # emoji in button can only support single emoji
        button_block = get_button_block('Open PR ' + emoji_string, pr_url)
        blocks.append(button_block)
        blocks.append(get_divider_block())

    dummy_merge_all_section = get_button_block('Merge All PRs', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'danger')
    blocks.append(dummy_merge_all_section)
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
        block_count = len(blocks)

        # sending 5 prs or 15 blocks at a time to avoid content limit of slack api
        if len(blocks) > 15:
            i = 0
            while block_count is not 0:
                # count of blocks to be sent
                count = min(15, len(blocks) - i)
                required_blocks = blocks[i:i + count]
                body['blocks'] = str(required_blocks)
                i += count
                block_count -= count
                post_request(slack_url, slack_oauth_token, body)
        else:
            post_request(slack_url, slack_oauth_token, body)


def can_send_slack():
    return slack_oauth_token is not None
