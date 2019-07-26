from redminelib import Redmine
from utils.utils import echo, echo_error, echo_success


class RedminePlugin(object):
    def __init__(
        self,
        redmine_url,
        redmine_username,
        redmine_password,
        redmine_task_prefix=None,
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

        open_issues = list(
            self.redmine.issue.filter(assigned_to_id=user.id, status_id='open')
        )
        closed_issues = list(
            self.redmine.issue.filter(
                assigned_to_id=user.id,
                status_id='closed'
            )
        )
        all_issues = open_issues + closed_issues

        return {
            'open': open_issues,
            'closed': closed_issues,
            'all': all_issues
        }

    def do_sync(self, issue, jira_username):
        """
        [u'assigned_to',
        u'attachments',
        u'author',
        u'changesets',
        u'children',
        u'closed_on',
        u'created_on',
        u'custom_fields',
        u'description',
        u'done_ratio',
        u'id',
        u'journals',
        u'priority',
        u'project',
        u'relations',
        u'status',
        u'subject',
        u'time_entries',
        u'tracker',
        u'updated_on',
        u'watchers']
        """
        if not self.jira:
            echo_error("Jira Wrapper is not Available")
            return
        # build the unique issue_text prefix
        issue_text = '{prefix}#{issue.project}#{issue.id}'.format(
            prefix=self.redmine_task_prefix,
            issue=issue
        )
        echo("Searching Jira for {0}".format(issue_text))
        # check if it already exists
        tasks = self.jira.search_task_by_summary(text=issue_text)
        task_count = len(tasks)
        if task_count > 1:
            echo_error("Duplicated task found for {0}".format(issue_text))
        elif task_count == 1:
            # update existing issue
            self.update_task(tasks[0], issue, jira_username)
        else:
            # create a new assigned issue in backlog
            self.create_task(issue, issue_text, jira_username)

    def update_task(self, task, issue, jira_username):
        echo('Updating existing task {0}'.format(task))
        if self.sync:
            # FIXME: Implement the update
            pass

    def create_task(self, issue, issue_text, jira_username):
        echo("Creating a new task on Jira for {0}".format(issue_text))
        params = {
            'summary': "{}#{} -{}".format(
                issue_text,
                jira_username,
                issue.subject
            ),
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
                "Created Jira ............{}/browse/{}".format(
                    self.jira.jira_url,
                    created_issue.key.encode()
                )
            )

    def process_issues(self, redmine_userid, jira_username):
        issues = self.get_issues(redmine_userid)
        if not jira_username:
            jira_username = self.jira.userid.encode()
        for issue in issues['all']:
            echo(
                "Processing: {issue}:{issue.id} - status: {issue.status}"
                .format(issue=issue)
            )
            self.do_sync(issue, jira_username)
