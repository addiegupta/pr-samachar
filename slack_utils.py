import json

slack_store_file = open('./slack_store.json')
slack_store = json.load(slack_store_file)


def create_greetings_message(valid_prs):
    prs_available = len(valid_prs) > 0
    reviewers = ', '.join(slack_store['reviewers'].values())
    salutation = "Namaste %s!" % reviewers
    message_status_key = 'available' if prs_available else 'not_available'
    message_status = slack_store['message_status'][message_status_key]
    pr_message_body = ''
    for pr in valid_prs:
        pr_title = pr['title']
        pr_author = pr['user']['login']
        pr_url = pr['html_url']
        pr_labels = ''
        # pr_labels = ', '.join(name for pr['labels'])
        for label in pr['labels']:
            if pr_labels:
                pr_labels += ', '
            pr_labels += label['name']
        pr_message_body += '\n%s by %s: %s\nLabels: %s' % (pr_title, pr_author, pr_url, pr_labels)

    return '\n'.join([salutation, message_status, pr_message_body])
