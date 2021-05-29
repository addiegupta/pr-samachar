import requests
import sys

from github_utils import get_pull_requests, repos


def main(argv):
    print("args is ", argv)
    pulls_url = get_pull_requests(repos['sentieo_web'])
    r = requests.get(pulls_url)
    print('request data is ', r)
    print('json is ', r.json())


if __name__ == '__main__':
    main(sys.argv)
