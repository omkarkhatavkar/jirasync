# coding: utf-8
import time

import click

from jirasync.plugins.github import GitHubPlugin
from jirasync.plugins.jira_workflow import (
    start_create_pull_requests_workflow,
    start_issue_workflow,
    start_review_pull_requests_workflow,
)
from jirasync.plugins.redmine import RedminePlugin
from jirasync.utils.config import Config
from jirasync.utils.utils import (
    configure_interval,
    echo_error,
    formatting,
    get_yaml_data,
)
from jirasync.wrappers.jirawrapper import MyJiraWrapper

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def cli():
    """This CLI tool used to integrate GitHub and Redmine with Jira.
    For Github it will sync and track GitHub issues, pr's, pr_reviews
     with Jira. It will auto create, update and close status in Jira.
    """
    pass


def show_team_history(config, interval):
    """This helper method for only showing the github data on console
    based on interval
    """
    try:
        config_data = get_yaml_data(config.config_file)
        teams = config_data["teams"]
    except Exception:
        echo_error("ERROR: config.yaml not configured correctly! ")
        echo_error("Please look at config_sample.yaml file")
    for team in teams:
        print ("For Team ==> {}".format(team))
        users = teams[team]["Users"]
        for user in users:
            print ("For User ==> {}".format(users[user]["github_username"]))
            git_hub_plugin = GitHubPlugin(
                users[user]["github_username"],
                teams[team]["email_id"],
                interval,
                teams[team]["git_urls"],
                teams[team]["github_token"],
            )
            assigned_issue_list = (
                git_hub_plugin.get_github_issues_assigned_list()
            )
            time.sleep(3)
            pr_list = git_hub_plugin.get_opened_pull_requests()
            pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
            time.sleep(3)
            pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
            pr_review_list_open = (
                git_hub_plugin.get_pull_requests_review_in_progress()
            )
            time.sleep(3)
            formatting("Github Issues Assigned", assigned_issue_list)
            formatting("PR Raised this week", pr_list)
            formatting("PR Raised and now Merged Status", pr_closed_list)
            formatting("PR Reviewed Closed Status", pr_review_list_closed)
            formatting("PR Reviewed Open Status", pr_review_list_open)


def start_syncing(config, interval):
    """This helper method for syncing github data with Jira based on
    interval
    """
    try:
        config_data = get_yaml_data(config.config_file)
        teams = config_data["teams"]
    except Exception:
        echo_error("ERROR: config.yaml not configured correctly! ")
        echo_error("Please look at config_sample.yaml file")
    for team in teams:
        print ("For Team ==> {}".format(team))
        users = teams[team]["Users"]
        for user in users:
            print ("For User ==> {}".format(users[user]["github_username"]))
            git_hub_plugin = GitHubPlugin(
                users[user]["github_username"],
                teams[team]["email_id"],
                interval,
                teams[team]["git_urls"],
                teams[team]["github_token"],
            )

            assigned_issue_list = (
                git_hub_plugin.get_github_issues_assigned_list()
            )
            time.sleep(4)
            pr_list = git_hub_plugin.get_opened_pull_requests()
            pr_closed_list = git_hub_plugin.get_pull_requests_merged_closed()
            time.sleep(4)
            pr_review_list_closed = git_hub_plugin.get_pull_requests_reviewed()
            pr_review_list_open = (
                git_hub_plugin.get_pull_requests_review_in_progress()
            )
            time.sleep(4)
            jira = MyJiraWrapper(config.config_file, config.config_file)

            start_issue_workflow(
                github_issues=assigned_issue_list,
                jira=jira,
                assignee=users[user]["jira_username"],
            )
            start_create_pull_requests_workflow(
                github_issues=pr_list,
                jira=jira,
                assignee=users[user]["jira_username"],
            )
            start_create_pull_requests_workflow(
                github_issues=pr_closed_list,
                jira=jira,
                assignee=users[user]["jira_username"],
            )
            start_review_pull_requests_workflow(
                github_issues=pr_review_list_closed,
                jira=jira,
                assignee=users[user]["jira_username"],
            )
            start_review_pull_requests_workflow(
                github_issues=pr_review_list_open,
                jira=jira,
                assignee=users[user]["jira_username"],
            )


@cli.command()
@click.option(
    "--sync", default=False, is_flag=True, help="Perform the writes to Jira"
)
@click.option(
    "--interval", default="week", help="Pass interval e.g. week, day"
)
@pass_config
def github(config, sync, interval):
    """Reads issues from github for users defined on `config.yaml` and sync
    with Jira. By default runs in a `check only` mode (no write is performed)
    to write to jira add `--sync` to the command line.

    Expects Github and Jira config on `config.yaml` and users information on
    `config.yaml`. See `config_sample.yaml` for example.
    """
    if interval not in ["week", "day"]:
        echo_error("Please pass correct interval. e.g. 'week', 'day'")
        exit(1)
    else:
        interval = configure_interval(interval)
    if not sync:
        echo_error(
            "Running on check-only mode, to write to Jira add `--sync` "
            "to the command line"
        )
        show_team_history(config, interval)
    else:
        start_syncing(config, interval)


@cli.command()
@click.option(
    "--sync", default=False, is_flag=True, help="Perform the writes to Jira"
)
@pass_config
def redmine(config, sync):
    """Reads issues from redmine for users defined on `config.yaml` and sync
    with Jira. By default runs in a `check only` mode (no write is performed)
    to write to jira add `--sync` to the command line.

    Expects Redmine and Jira config on `config.yaml` and users information on
    `config.yaml`. See `config_sample.yaml` for example.
    """
    if not sync:
        echo_error(
            "Running on check-only mode, to write to Jira add `--sync` "
            "to the command line"
        )
    config_data = get_yaml_data(config.config_file)
    teams = config_data["teams"]
    redmine_plugin = RedminePlugin(
        config_data["redmine_url"],
        config_data["redmine_username"],
        config_data["redmine_password"],
        config_data["redmine_task_prefix"],
        sync=sync,
        jira=MyJiraWrapper(config.config_file, config.config_file),
    )
    for team in teams:
        click.echo("For Team ==> {}".format(team))
        users = teams[team]["Users"]
        for user in users:
            redmine_userid = users[user].get("redmine_userid")
            jira_username = users[user].get("jira_username")
            if not redmine_userid:
                click.echo(
                    "User {0} has no redmine configuration.".format(user)
                )
                continue
            click.echo("For User ==> {0}:{1}".format(user, redmine_userid))
            redmine_plugin.process_issues(redmine_userid, jira_username)


@cli.command()
@click.pass_context
@click.option(
    "--commands", default=None, help="Pass command names "
                                     "e.g. --commands github,redmine"
)
@click.option(
    "--sync", default=False, is_flag=True, help="Perform the writes to Jira"
)
def run(ctx, commands, sync):
    """Run multiple commands within single command
    e.g. jirasync run --command github, redmine """
    current_commands = ('github', 'redmine')
    if commands is None:
        echo_error(
            "Please pass --command option e.g. --command github, redmine"
        )
        exit()
    for command in commands.strip().split(','):
        if command in current_commands:
            ctx.invoke(globals()[command], sync=sync)
        else:
            echo_error("{} command is not supported, \nCurrently supported "
                       "commands are {}". format(command,
                                                 ','.join(current_commands)))


@cli.command()
@pass_config
@click.pass_context
def service_run(ctx, config):
    """Run as a service/daemon based on `service` in `config.yaml`"""
    config_data = get_yaml_data(config.config_file)["service"]
    sleep_time = config_data.get("sleep_time", 120)
    while True:
        for command in config_data["commands"]:
            ctx.invoke(globals()[command["name"]], **command.get("kwargs", {}))
        click.echo()
        click.echo("Next run in {0} seconds...".format(sleep_time))
        time.sleep(sleep_time)


if __name__ == "__main__":  # pragma: no cover
    cli()
