from wrappers.jirawrapper import MyJiraWrapper
from utils.utils import (
    echo_skip,
)


def create_new_issue_in_backlog(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode()
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{}#{} -{}".format(issue_text, assignee, issue.title),
                'details': "{}".format(issue.data['body']),
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': 'backlog',
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode()))


def create_pull_request_in_current_sprint(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode()
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{}#{} -{}".format(issue_text, assignee, issue.title),
                'details': "{}".format(issue.data['body']),
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': jira.current_sprint_name.encode(),
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode()))


def create_pull_request_review_in_current_sprint(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode()
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{}#{} -{}".format(issue_text, assignee, issue.title),
                'details': "{}".format(issue.data['body']),
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': jira.current_sprint_name.encode(),
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode()))


def update_existing_issue_in_current_sprint(task, issue, jira):
    if isinstance(jira, MyJiraWrapper):
        if task.fields.status.name.encode() == 'Done':
            echo_skip("No Need of Update! Already Done!")
        else:
            if issue.data['state'].encode() == 'closed':
                # jira.update_sprint(task.key.encode()) this is failing need to find some better solution
                jira.change_status(task.id.encode(), 'Done')
                echo_skip("Status Updated Jira .....{}/browse/{}".format(jira.jira_url, task.key.encode()))
