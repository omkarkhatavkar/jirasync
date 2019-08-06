# coding: utf-8
import click
import os
import time

from passlib.context import CryptContext
from xdg import BaseDirectory

from wrappers.jirawrapper import MyJiraWrapper

from plugins.jira_workflow import (
    start_issue_workflow,
    start_create_pull_requests_workflow,
    start_review_pull_requests_workflow
)

from utils.utils import (
    echo_success,
    echo_error,
    update_yaml,
    configure_interval,
    get_yaml_data
)
from plugins.github import (
    GitHubPlugin,
)
from plugins.redmine import (
    RedminePlugin,
)


class Config(object):

    def __init__(self):
        self.config_file = self.get_config_file("config.yaml")
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=30000
        )

    def get_config_file(self, filename):
        """Look for the proper config file path based on
        https://github.com/omkarkhatavkar/jirasync/issues/5
        """
        # Try to find the file from path exported to JIRASYNC_SETTINGS_PATH
        # this variable can be a directory path like /foo/bar
        # and also can be full path like /etc/foo/config.yaml
        path = os.environ.get('JIRASYNC_SETTINGS_PATH')
        if path is not None:
            if not path.endswith(("yaml", "yml")):
                path = os.path.join(path, filename)
            if os.path.exists(path):
                echo_success("Found config file in {}".format(path))
                return path
            else:
                echo_error(
                    "JIRASYNC_SETTINGS_PATH={0} cannot be found"
                    .format(path)
                )

        # Try to find in the XDG paths
        # look ~/.config/jirasync/config.yaml
        # then /etc/xdg/jirasync/config.yaml
        # then /etc/jirasync/config.yaml
        BaseDirectory.xdg_config_dirs.append('/etc')
        for dir_ in BaseDirectory.load_config_paths("jirasync"):
            path = os.path.join(dir_, filename)
            if os.path.exists(path):
                echo_success("Found config file in {}".format(path))
                return path

        # load from current directory
        path = os.path.join(os.curdir, filename)
        if os.path.exists(path):
            echo_success("Found config file in {}".format(path))
            return path

        raise IOError("{0} cannot be found".format(path))


pass_config = click.make_pass_decorator(Config, ensure=True)


def encrypt_password(pwd_context, password):
    return pwd_context.encrypt(password)


def check_encrypted_password(pwd_context, password, hashed):
    return pwd_context.verify(password, hashed)


def set_config_properties(git_urls, config_dict):
    content = {}
    git_urls = {'git_urls': str(git_urls).encode().split(',')}
    content.update(git_urls)
    if config_dict is None:
        config_dict = dict()
    for key, value in config_dict.items():
        content.update({key: value})
    return content


def formatting(header, github_list):
    echo_error("=================================")
    echo_error(header)
    echo_error("=================================")
    if len(github_list) == 0:
        echo_error("No new item found !")
    else:
        for item in github_list:
            echo_error(item.data['html_url'])
    print("\n")


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    """This CLI tool to sync and track GitHub issues, pr's, pr_reviews
     with Jira. Currently supported to only for create, update and
     close status.
    """
    pass


@cli.command()
@click.option('--git-urls', default=None, prompt=True,
              help="Pass the git project names for Jira sync e.g. airgun, robottelo")
@click.option('--jira-url', prompt=True, confirmation_prompt=False,
              help="Pass the Jira url")
@click.option('--github-username', default=None, prompt=True,
              help="Pass GitHub username")
@click.option('--github-token', default=None, prompt=True,
              help="Pass GitHub token")
@click.option('--jira-username', default=None, prompt=True,
              help="Pass Jira username")
@click.option('--jira-email-id', default=None, prompt=True,
              help="Pass Jira Email Id")
@click.option('--jira-board', prompt=True, confirmation_prompt=False,
              help='Pass the Jira board name')
@click.option('--jira-project', prompt=True, confirmation_prompt=False,
              help='Pass the Jira project name')
@pass_config
def set_config(config, git_urls, jira_url, github_username, github_token,
               jira_username, jira_email_id, jira_board, jira_project):
    """Set configuration in jirasync before start using it"""
    if os.path.exists(config.config_file):
        os.unlink(config.config_file)
    try:
        if None not in (git_urls, github_username, github_token, jira_username,
                        jira_email_id, jira_board, jira_project, jira_url):
            auth_dict = {
                'kerberos': True,
                'basic_auth': False,
                'username': str(jira_username).encode()
            }
            content_dict = {
                'url': str(jira_url).encode(),
                'github_username': str(github_username).encode(),
                'github_token': str(github_token).encode(),
                'board': str(jira_board).encode(),
                'project': str(jira_project).encode(),
                'email_id': str(jira_email_id).encode(),
                'auth': auth_dict,
                'ca_cert_path': "/etc/ssl/certs/ca-bundle.crt",
                'verify_ssl': True,
                'label_check': False,
                'check_for_updates': 'false'
            }
            content = set_config_properties(git_urls,
                                            content_dict)
            update_yaml(config.config_file, content)
            echo_success("Configs are set !")
            jira = MyJiraWrapper('config.yaml', 'labels.yaml')

        else:
            echo_error("Please Pass missing options!")
    except Exception as err:
        click.echo(err)


@cli.command()
@click.option('--interval', default='day',
              help="please pass interval e.g. week, day")
@pass_config
def check_github_history(config, interval):
    """see github work history result based on intervals
     e.g. jirasync check-github-history --interval week """
    if interval not in ['week', 'day']:
        echo_error("Please pass correct interval. e.g. 'week', 'day'")
        exit(1)
    else:
        interval = configure_interval(interval)
    yaml_data = get_yaml_data(config.config_file)
    git_hub_plugin = GitHubPlugin(yaml_data['github_username'],
                                  yaml_data['email_id'],
                                  interval,
                                  yaml_data['git_urls'],
                                  yaml_data['github_token']
                                  )
    issue_list = git_hub_plugin.get_github_issues_created_list()
    assigned_issue_list = git_hub_plugin.get_github_issues_assigned_list()
    pr_list = git_hub_plugin.get_opened_pull_requests()
    pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
    pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
    pr_review_list_open = git_hub_plugin.get_pull_requests_review_in_progress()
    formatting('Issues Created', issue_list)
    formatting('Issues Assigned', assigned_issue_list)
    formatting('PR Raised this week', pr_list)
    formatting('PR Raised and now Merged Status', pr_closed_list)
    formatting('PR Reviewed Closed Status', pr_review_list_closed)
    formatting('PR Reviewed Open Status', pr_review_list_open)


@cli.command()
@click.option('--interval', default='day',
              help="please pass interval e.g. week, day")
@pass_config
def start_syncing(config, interval):
    """sync github issues, pr, pr_reviews as jira tasks for individual user.
    currently supported day and week interval
    e.g. jirasync start-syncing --interval week
    """
    if interval not in ['week', 'day']:
        echo_error("Please pass correct interval. e.g. 'week', 'day'")
        exit(1)
    else:
        interval = configure_interval(interval)

    yaml_data = get_yaml_data(config.config_file)
    git_hub_plugin = GitHubPlugin(yaml_data['github_username'],
                                  yaml_data['email_id'],
                                  interval,
                                  yaml_data['git_urls'],
                                  yaml_data['github_token']
                                  )
    created_issue_list = git_hub_plugin.get_github_issues_created_list()
    assigned_issue_list = git_hub_plugin.get_github_issues_assigned_list()
    pr_list = git_hub_plugin.get_opened_pull_requests()
    pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
    pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
    pr_review_list_open = git_hub_plugin.get_pull_requests_review_in_progress()
    jira = MyJiraWrapper('config.yaml', 'labels.yaml')
    start_issue_workflow(github_issues=created_issue_list, jira=jira)
    start_issue_workflow(github_issues=assigned_issue_list, jira=jira)
    start_create_pull_requests_workflow(github_issues=pr_list, jira=jira)
    start_create_pull_requests_workflow(github_issues=pr_closed_list, jira=jira)
    start_review_pull_requests_workflow(github_issues=pr_review_list_closed, jira=jira)
    start_review_pull_requests_workflow(github_issues=pr_review_list_open, jira=jira)


@cli.command()
@click.option('--interval', default='week',
              help="please pass interval e.g. week, day")
@pass_config
def show_team_history(config, interval):
    """see github work history for a team based on intervals
    all users should mentioned in team.yaml
    e.g. jirasync show_team_history --interval week
    """
    config_data = get_yaml_data(config.config_file)
    teams = config_data['teams']
    for team in teams:
        print("For Team ==> {}".format(team))
        users = teams[team]['Users']
        for user in users:
            print("For User ==> {}".format(users[user]['github_username']))
            git_hub_plugin = GitHubPlugin(
                users[user]['github_username'],
                teams[team]['email_id'],
                interval,
                teams[team]['git_urls'],
                teams[team]['github_token']
            )
            assigned_issue_list = git_hub_plugin.get_github_issues_assigned_list()
            time.sleep(3)
            pr_list = git_hub_plugin.get_opened_pull_requests()
            pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
            time.sleep(3)
            pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
            pr_review_list_open = git_hub_plugin.get_pull_requests_review_in_progress()
            time.sleep(3)
            formatting('Github Issues Assigned', assigned_issue_list)
            formatting('PR Raised this week', pr_list)
            formatting('PR Raised and now Merged Status', pr_closed_list)
            formatting('PR Reviewed Closed Status', pr_review_list_closed)
            formatting('PR Reviewed Open Status', pr_review_list_open)


@cli.command()
@click.option('--interval', default='week',
              help="please pass interval e.g. week, day")
@pass_config
def start_syncing_team(config, interval):
    """sync github issues, pr, pr_reviews as jira tasks for whole team.
    currently supported day and week interval for
    all users mentioned in team.yaml
    e.g. jirasync start-syncing-team --interval week
    """
    try:
        config_data = get_yaml_data(config.config_file)
        teams = config_data['teams']
    except Exception as error:
        echo_error("ERROR: config.yaml not configured correctly! ")
        echo_error("Please look at config_sample.yaml file")
    for team in teams:
        print("For Team ==> {}".format(team))
        users = teams[team]['Users']
        for user in users:
            print("For User ==> {}".format(users[user]['github_username']))
            git_hub_plugin = GitHubPlugin(
                users[user]['github_username'],
                teams[team]['email_id'],
                interval,
                teams[team]['git_urls'],
                teams[team]['github_token']
            )

            assigned_issue_list = git_hub_plugin.get_github_issues_assigned_list()
            time.sleep(3)
            pr_list = git_hub_plugin.get_opened_pull_requests()
            pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
            time.sleep(3)
            pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
            pr_review_list_open = git_hub_plugin.get_pull_requests_review_in_progress()
            time.sleep(3)
            jira = MyJiraWrapper(config.config_file, config.config_file)

            start_issue_workflow(
                github_issues=assigned_issue_list,
                jira=jira,
                assignee=users[user]['jira_username']
            )
            start_create_pull_requests_workflow(
                github_issues=pr_list,
                jira=jira,
                assignee=users[user]['jira_username']
            )
            start_create_pull_requests_workflow(
                github_issues=pr_closed_list,
                jira=jira,
                assignee=users[user]['jira_username']
            )
            start_review_pull_requests_workflow(
                github_issues=pr_review_list_closed,
                jira=jira,
                assignee=users[user]['jira_username']
            )
            start_review_pull_requests_workflow(
                github_issues=pr_review_list_open,
                jira=jira,
                assignee=users[user]['jira_username']
            )


@cli.command()
@click.option(
    '--sync',
    default=False,
    is_flag=True,
    help="Perform the writes to Jira"
)
@pass_config
def redmine(config, sync):
    """Reads issues from redmine for users defined on `team.yaml` and sync
    with Jira. By default runs in a `check only` mode (no write is performed)
    to write to jira add `--sync` to the command line.

    Expects Redmine and Jira config on `config.yaml` and users information on
    `team.yaml`. See `team_sample.yaml` and `config_sample.yaml` for examples.
    """
    if not sync:
        echo_error(
            "Running on check-only mode, to write to Jira add `--sync` "
            "to the command line"
        )
    config_data = get_yaml_data(config.config_file)
    teams = config_data['teams']
    redmine_plugin = RedminePlugin(
        config_data['redmine_url'],
        config_data['redmine_username'],
        config_data['redmine_password'],
        config_data['redmine_task_prefix'],
        sync=sync,
        jira=MyJiraWrapper(config.config_file, config.config_file)
    )
    for team in teams:
        click.echo("For Team ==> {}".format(team))
        users = teams[team]['Users']
        for user in users:
            redmine_userid = users[user].get('redmine_userid')
            jira_username = users[user].get('jira_username')
            if not redmine_userid:
                click.echo(
                    "User {0} has no redmine configuration.".format(user)
                )
                continue
            click.echo("For User ==> {0}:{1}".format(user, redmine_userid))
            redmine_plugin.process_issues(redmine_userid, jira_username)


@cli.command()
@pass_config
@click.pass_context
def service_run(ctx, config):
    """Run as a service/daemon based on `service` in `config.yaml`"""
    config_data = get_yaml_data(config.config_file)['service']
    sleep_time = config_data.get('sleep_time', 120)
    while True:
        for command in config_data['commands']:
            ctx.invoke(globals()[command['name']], **command.get('kwargs', {}))
        click.echo()
        click.echo('Next run in {0} seconds...'.format(sleep_time))
        time.sleep(sleep_time)
