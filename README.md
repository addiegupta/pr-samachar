# pr-samachar
Slack bot for Daily PR Reminders 


## Usage

### `pr-samachar.py [-h] [-e] gpat [slacktoken]`

```
The following arguments are required:
  gpat

positional arguments:
  gpat        GitHub personal access token (with access to repositories listed in config)
  slacktoken  Slack OAuth token (with access to channels listed in config)

optional arguments:
  -h, --help  show this help message and exit
  -e, --eod   generates end of day report
  ```
  

If slack token is not provided, a slightly different message layout (without use of Slack API blocks) is generated and copied to clipboard
  
### For custom usage:
- Only the params in config.json file (default config is for rmsv2 PRs) need to be changed; 
```
{
  "all_reviewers": {
    "atul_kumar": "Atul Kumar",
    "ayudh": "Ayudh Gupta"
  },
  "all_channels": {
    "rmsv2-pr-samachar": "<channel_id>"
  },
  "organisation": "usernames",
  "repos": {
    "sentieoweb": {
      // all params except 'config' are optional inside this block
      "type": "pr",
      "state": "open",
      "labels": [
        "rmsv2"
      ],
      "excluded_labels": [
        "Don't Merge",
        "Requested"
      ],
      "draft": "false",
      "config": {
        "sort": "created",
        "order": "asc",
        "per_page": 30
      },
      "eod": {
        "type": "pr",
        "labels": [
          "rmsv2"
        ],
        "excluded_labels": [
        ],
        "config": {
          "sort": "created",
          "order": "desc",
          "per_page": 30
        }
      },
      "reviewers": [
        "atul_kumar",
        "ayudh"
      ],
      "channels": [
        "rmsv2-pr-samachar"
      ]
    }
  }
}
```

- A `repo` object can be added to the `repos` object with custom config containing info about which PRs are to be fetched and to which channels is the message to be sent.

- Optional param `eod` can also be added to the repo object if a end of day slack is also to be sent containing count of PRs opened and merged since last time the script was run in `eod` mode.

- Reviewer and channel info also needs to be added to `all_channels` and `all_reviewers` objects

- PR health messages and other message text can be customised in `slack_store.json` file

![image](https://user-images.githubusercontent.com/70014439/122679016-c0ba3e80-d206-11eb-8a7a-0aa8559fd097.png)

