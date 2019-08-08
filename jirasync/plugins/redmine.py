# coding: utf-8
"""Redmine Integration Plugin"""

from copy import copy

from redminelib import Redmine

from jirasync.utils import echo, echo_error, echo_skip, echo_success


class RedminePlugin(object):
    """A Redmine integration plugin class."""

    def __init__(
        self,
        redmine_url,
        redmine_username,
        redmine_password,
        redmine_task_prefix="redmine",
        sync=False,
        jira=None,
    ):
        """Creates a new instance for RedminePlugin

        Arguments:
            redmine_url {str} -- URL for the Redmine server root path
            redmine_username {str} -- The user to authenticate to redmine
            redmine_password {str} -- The password to authenticate to redmine

        Keyword Arguments:
            redmine_task_prefix {str} -- A prefix to be added as the first part
                of created task summary. ex: redmine#x#y (default: {"redmine"})
            sync {bool} -- Sync or only check results (default: {False})
            jira {JiraWrapper} -- Instance of a JiraWrapper (default: {None})
        """
        self.redmine = Redmine(
            redmine_url, username=redmine_username, password=redmine_password
        )
        self.redmine_task_prefix = redmine_task_prefix
        self.sync = sync
        self.jira = jira

    def make_summary(self, issue):
        """Concatenate data to build a unique summary for Jira task

        Arguments:
            issue_text {str} -- Unique text to prefix the task summary
            issue {Issue} -- Issue instance
        """
        return "{0} - {issue.subject}".format(
            self.make_issue_text(issue), issue=issue
        )

    def make_issue_text(self, issue):
        """Concatenate a unique summary to prefix Jira task summary

        Arguments:
            issue {Issue} -- Issue instance

        Returns:
            str -- The summary built of issue data and prefix
        """
        return "{prefix}#{issue.project}#{issue.id}#".format(
            prefix=self.redmine_task_prefix, issue=issue
        )

    def get_issues(self, redmine_userid):
        """Read all the issues assigned to certain user on Redmine server

        Arguments:
            redmine_userid {int} -- The numeric ID for a redmine user.

        Returns:
            list -- A list of all the issues assigned to user
        """
        user = self.redmine.user.get(redmine_userid)
        return list(
            # use (status_id='open|closed') to filter out issues
            self.redmine.issue.filter(assigned_to_id=user.id, status_id="*")
        )

    def do_sync(self, issue, jira_username):
        """Perform the sync, invoked only when self.sync == True

        Arguments:
            issue {Issue} -- Issue object returned by get_issues
            jira_username {str} -- Username on Jira server
        """
        if not self.jira:
            echo_error("Jira Wrapper is not Available")
            return
        # build the unique issue_text prefix
        issue_text = self.make_issue_text(issue)
        # check if it already exists
        tasks = self.jira.search_existing_task(issue_text=issue_text)
        task_count = len(tasks)
        echo("Found {}: {} existing tasks".format(task_count, tasks))
        if task_count > 1:
            echo_error("Duplicated task found for {0}".format(issue_text))
        elif task_count == 1:
            # update existing issue
            self.update_task(tasks[0], issue, jira_username)
        else:
            # create a new assigned issue in backlog
            # if issue is not already closed
            self.create_task(issue, jira_username)

    def update_task(self, task, issue, jira_username):
        """Updates a Jira Task when it already exists

        Arguments:
            task {JiraTask} -- Instance of a JiraWrapper Task
            issue {Issue} -- Instance of Issue returned by get_issues
            jira_username {str} -- Username on Jira server
        """

        # Check if task is already done or reopened
        if task.fields.status.name.encode() == "Done":
            if "close" not in issue.status.name.lower() and self.sync:
                # Task has been reopened on redmine, start transition workflow
                self.jira.change_status(task.id.encode(), "Reopen")
                echo_success(
                    "Reopened {0}/{1}[{issue.status}] "
                    "on {2}".format(
                        task,
                        task.fields.summary,
                        task.permalink(),
                        issue=issue,
                    )
                )
            else:
                echo_skip("No Need to Update! Task already Done!")
                return

        # Check if there are other changes on Redmine to be updated on Jira
        current_assignee = copy(task.fields.assignee.key)
        current_summary = task.fields.summary.replace(
            "{} - ".format(self.make_issue_text(issue)), ""
        )
        changed_fields = {}
        if current_assignee != jira_username:
            changed_fields["assignee"] = jira_username
        if current_summary != issue.subject:
            changed_fields["summary"] = self.make_summary(issue)

        if changed_fields:
            echo_success(
                "Updating Task {} setting {}".format(task, changed_fields)
            )
            task.update(**changed_fields)

        # status cannot be changed by calling task.update
        # must call the `transition` workflow.
        if "close" in issue.status.name.lower() and self.sync:
            self.jira.change_status(task.id.encode(), "Done")
            echo_success(
                "Closed {0}/{1}[{issue.status}] "
                "on {2}".format(
                    task, task.fields.summary, task.permalink(), issue=issue
                )
            )
        else:
            echo_skip(
                "Skipping: {0}/{1}[{issue.status}] {msg} "
                "on {2}".format(
                    task,
                    task.fields.summary,
                    task.permalink(),
                    issue=issue,
                    msg=(
                        "`--sync` is disabled"
                        if not self.sync
                        else "no status update"
                    ),
                )
            )

    def create_task(self, issue, jira_username):
        """Creates a new Jira Task based on Redmine issue.

        Arguments:
            issue {Issue} -- Issue instance returned by get_issues
            jira_username {str} -- Username on Jira

        Fields available on `issue` object:
            [u'assigned_to', u'attachments', u'author', u'changesets',
            u'children', u'closed_on', u'created_on', u'custom_fields',
            u'description', u'done_ratio', u'id', u'journals', u'priority',
            u'project', u'relations', u'status', u'subject', u'time_entries',
            u'tracker', u'updated_on', u'watchers']
        """
        if "close" in issue.status.name.lower():
            echo_skip(
                "Issue {0} is closed on redmine, skipping".format(issue.id)
            )
            return

        params = {
            "summary": self.make_summary(issue),
            "details": "Source: {}\n{}".format(
                "{}/issues/{}".format(self.redmine.url, issue.id),
                issue.description,
            ),
            "component": "Automation",
            "labels": ["Automation", self.redmine_task_prefix],
            "sprint": "backlog",
            "assignee": jira_username,  # FIXME
            "issuetype": "Task",
        }

        if self.sync:
            created_task = self.jira.create_issue(**params)
            echo_success(
                "Created Jira {} on {}".format(
                    created_task.fields.summary, created_task.permalink()
                )
            )
        else:
            echo_skip(
                "{} to be created on Jira with {} ".format(
                    self.make_issue_text(issue), params
                )
            )

    def process_issues(self, redmine_userid, jira_username):
        """Main Entry point to process the issues

        Arguments:
            redmine_userid {int} -- Redmine User numeric id
            jira_username {str} -- Username on Jira
        """
        issues = self.get_issues(redmine_userid)
        echo("# A total of {0} issues to process.".format(len(issues)))
        if not jira_username:
            jira_username = self.jira.userid.encode()
        for issue in issues:
            echo(
                "\n## Processing: {issue}:{issue.id} -"
                " status: {issue.status}".format(issue=issue)
            )
            self.do_sync(issue, jira_username)
