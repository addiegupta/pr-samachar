import json

slack_store_file = open('./slack_store.json')
slack_store = json.load(slack_store_file)


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


def create_greetings_message(valid_prs):
    prs_available = len(valid_prs) > 0
    reviewers = ', '.join(slack_store['reviewers'].values())

    salutation = "Namaste %s!" % reviewers

    message_status_key = 'available' if prs_available else 'not_available'
    message_status = slack_store['message_status'][message_status_key]
    if prs_available:
        message_status = message_status % len(valid_prs)

    pr_message_body = ''

    for pr in valid_prs:
        pr_title = pr['title']
        pr_author = pr['user']['login']
        pr_url = pr['html_url']
        pr_labels = get_labels_info(pr)

        pr_message_body += '\n%s by %s\nLabels: %s\n%s\n' % (pr_title, pr_author, pr_labels, pr_url)

    return '\n'.join([salutation, message_status, pr_message_body])
