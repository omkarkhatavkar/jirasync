import did.cli
import did.base
from utils import utils


# INTERVAL = "--since 2018-01-01 --until 2019-04-24"

CONFIG = """
[general]
email = <email_id>
[gh]
type = github
url = https://api.github.com/
login = <login_name>
token = <token>
"""


# below code is for debugging
def print_issue_list(issue_list):
    utils.echo_error('\n=======================================Start Fetching=======================================')
    for issue_stat in issue_list:
        print("Title ==> " + issue_stat.title)
        print("Description ==> \n" + issue_stat.data['body'])
        print("Number ==> " + str(issue_stat.data['number']))
        print("Assignees ==> " + str(len(issue_stat.data['assignees'])))
        print("Status ==> " + issue_stat.data['state'])
        print("URL ==> " + issue_stat.data['url'])
        print("Project ==> " + issue_stat.project)
        utils.echo_error('===========================================')


def filter_issue_list(git_urls, stats):
    issue_list = []
    for stat in stats:
        for url in git_urls:
            if stat.project in url:
                issue_list.append(stat)
    return issue_list


class GitHubPlugin(object):
    def __init__(self, github_username, email, interval, git_urls, github_token):
        self.config = CONFIG.replace('<login_name>', str(github_username))
        self.config = self.config.replace('<email_id>', str(email))
        self.config = self.config.replace('<token>', str(github_token))
        self.interval = interval
        self.git_urls = git_urls

    # This is Issue are created list
    def get_github_issues_created_list(self):
        did.base.Config(self.config)
        option = "--gh-issues-created --width 160 "
        stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[0].stats
        issue_list = filter_issue_list(self.git_urls, stats)
        # print_issue_list(issue_list)
        return issue_list

    # This will help us to Jira issue is assigned to me
    def get_github_issues_assigned_list(self, status='None'):
        did.base.Config(self.config)
        option = "--gh-issues-open-assigned --width 300 "
        all_stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[2].stats
        stats = []
        for issue_stat in all_stats[:]:
            assignees = len(issue_stat.data['assignees'])
            if assignees > 1 and status is None:
                stats.append(issue_stat)
            elif assignees > 1 and status == str(issue_stat.data['state'].encode()):
                stats.append(issue_stat)
        issue_list = filter_issue_list(self.git_urls, stats)
        # print_issue_list(issue_list)
        return issue_list

    def get_opened_pull_requests(self):
        did.base.Config(self.config)
        option = "--gh-pull-requests-created  --width 160 "
        stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[3].stats
        pr_list = []
        for stat in stats:
            if stat.data['state'] != 'closed':
                pr_list.append(stat)
        pr_list = filter_issue_list(git_urls=self.git_urls, stats=pr_list)
        # print_issue_list(pr_list)
        return pr_list

    def get_pull_requests_merged_closed(self):
        did.base.Config(self.config)
        option = "--gh-pull-requests-created --width 160 "
        stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[3].stats
        pr_list=[]
        for stat in stats:
            if stat.data['state'] == 'closed':
                pr_list.append(stat)
        pr_list = filter_issue_list(git_urls=self.git_urls, stats=pr_list)
        # print_issue_list(pr_list)
        return pr_list

    def get_pull_requests_reviewed(self):
        did.base.Config(self.config)
        option = "--gh-pull-requests-reviewed  --width 160 "
        stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[5].stats
        pr_review_list = filter_issue_list(git_urls=self.git_urls, stats=stats)
        # print_issue_list(pr_review_list)
        return pr_review_list

    def get_pull_requests_review_in_progress(self):
        did.base.Config(self.config)
        option = "--gh-pull-requests-review-in-progress  --width 160 "
        stats = did.cli.main(option + self.interval)[0][0].stats[0].stats[6].stats
        pr_review_list = filter_issue_list(git_urls=self.git_urls, stats=stats)
        # print_issue_list(pr_review_list)
        return pr_review_list

