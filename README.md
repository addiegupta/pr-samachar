# pr-samachar
Slack bot for Daily PR Reminders 


Usage: pr-samachar.py [-h] [-e] gpat [slacktoken]

The following arguments are required:
  gpat

positional arguments:
  gpat        GitHub personal access token (with access to repositories listed in config)
  slacktoken  Slack OAuth token (with access to channels listed in config)

optional arguments:
  -h, --help  show this help message and exit
  -e, --eod   generates end of day report
  
For custom usage, only the params in config.json file (default config is for rmsv2 PRs) need to be changed

If slack token is not provided, a slightly different message layout (without use of Slack API blocks) is generated and copied to clipboard



--
