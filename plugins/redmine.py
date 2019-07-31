from redminelib import Redmine
from utils.utils import echo, echo_error, echo_success, echo_skip


class RedminePlugin(object):
    def __init__(
        self,
        redmine_url,
        redmine_username,
        redmine_password,
        redmine_task_prefix="redmine",
        sync=False,
        jira=None
    ):
        self.redmine = Redmine(
            redmine_url,
            username=redmine_username,
            password=redmine_password
        )
        self.redmine_task_prefix = redmine_task_prefix
        self.sync = sync
        self.jira = jira

    def get_issues(self, redmine_userid):
        user = self.redmine.user.get(redmine_userid)
        return list(
            # use (status_id='open|closed') to filter out issues
            self.redmine.issue.filter(assigned_to_id=user.id, status_id='*')
        )

    def do_sync(self, issue, jira_username):
        if not self.jira:
            echo_error("Jira Wrapper is not Available")
            return
        # build the unique issue_text prefix
        issue_text = '{prefix}#{issue.project}#{issue.id}#'.format(
            prefix=self.redmine_task_prefix,
            issue=issue
        )

        # check if it already exists
        search_query = (
            'project = {} '
            'AND status != Done '
            'AND summary ~ \\"{}\\"'
        ).format(
            self.jira.project_id,
            issue_text.replace('#', '\u0023')
        )
        echo(
            "Searching Jira for {0} using query [{1}]".format(
                issue_text, search_query
            )
        )
        tasks = self.jira.jira.search_issues(
            search_query
        )
        task_count = len(tasks)
        echo("Found {}: {}".format(task_count, tasks))
        if task_count > 1:
            echo_error("Duplicated task found for {0}".format(issue_text))
        elif task_count == 1:
            # update existing issue
            self.update_task(tasks[0], issue, issue_text, jira_username)
        else:
            # create a new assigned issue in backlog
            # if issue is not already closed
            self.create_task(issue, issue_text, jira_username)

    def update_task(self, task, issue, issue_text, jira_username):
        if task.fields.status.name.encode() == 'Done':
            echo_skip("No Need to Update! Task already Done on Jira!")
        else:
            if task.fields.assignee.key != jira_username:
                # Assignee has changed needs update the task
                self.jira.change_assignee(task.id.encode(), jira_username)
                echo_success(
                    'Assignee changed from {} to {}'.format(
                        task.fields.assignee.key,
                        jira_username
                    )
                )

            if 'close' in issue.status.name.lower() and self.sync:
                self.jira.change_status(task.id.encode(), 'Done')
                echo_success(
                    "Updated status of {0}/{1}[{issue.status}] "
                    "...{2}/browse/{3}".format(
                        task,
                        issue_text,
                        self.jira.jira_url,
                        task.key.encode(),
                        issue=issue
                    )
                )
            else:
                echo_skip(
                    'Skipping: {0}/{1}[{issue.status}] {msg}'.format(
                        task,
                        issue_text,
                        issue=issue,
                        msg=(
                            "`--sync` is disabled"
                            if not self.sync
                            else "no status update"
                        )
                    )
                )

    def create_task(self, issue, issue_text, jira_username):
        """ Creates a new task on Jira based on Redmine issue.

        Fields available on `issue` object:
            [u'assigned_to', u'attachments', u'author', u'changesets',
            u'children', u'closed_on', u'created_on', u'custom_fields',
            u'description', u'done_ratio', u'id', u'journals', u'priority',
            u'project', u'relations', u'status', u'subject', u'time_entries',
            u'tracker', u'updated_on', u'watchers']
        """
        if 'close' in issue.status.name.lower():
            echo_skip(
                'Issue {0} is closed on redmine, skipping'.format(issue.id)
            )
            return

        params = {
            'summary': "{} - {}".format(issue_text, issue.subject),
            'details': "{}".format(issue.description),
            'component': 'Automation',
            'labels': ['Automation', self.redmine_task_prefix],
            'sprint': 'backlog',
            'assignee': jira_username,  # FIXME
            'issuetype': 'Task',
        }

        if self.sync:
            created_issue = self.jira.create_issue(**params)
            echo_success(
                "Created Jira {}...{}/browse/{}".format(
                    issue_text,
                    self.jira.jira_url,
                    created_issue.key.encode()
                )
            )
        else:
            echo_skip(
                "{} to be created on Jira with {} ".format(issue_text, params)
            )

    def process_issues(self, redmine_userid, jira_username):
        issues = self.get_issues(redmine_userid)
        echo("# A total of {0} issues to process.".format(len(issues)))
        if not jira_username:
            jira_username = self.jira.userid.encode()
        for issue in issues:
            echo(
                "\n## Processing: {issue}:{issue.id} - status: {issue.status}"
                .format(issue=issue)
            )
            self.do_sync(issue, jira_username)
