from wrappers.jirawrapper import MyJiraWrapper
from utils.utils import (
    echo_skip,
    get_sprint
)


def create_new_issue_in_backlog(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode('utf-8')
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{} -{}".format(issue_text.encode('utf-8'), issue.title.encode('utf-8')),
                'details': "Source : {}\n{}".format(issue.data['html_url'].encode('utf-8'),
                                                    issue.data['body']),
                'component': 'Automation',
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': 'backlog',
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode('utf-8')))


def create_pull_request_in_current_sprint(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode('utf-8')
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{} -{}".format(issue_text.encode('utf-8'), issue.title.encode('utf-8')),
                'details': "Source : {}\n{}".format(issue.data['html_url'].encode('utf-8'),
                                                    issue.data['body']),
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': get_sprint(jira),
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode('utf-8')))


def create_pull_request_review_in_current_sprint(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode('utf-8')
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                'summary': "{}#{} -{}".format(issue_text.encode('utf-8'), assignee, issue.title.encode('utf-8')),
                'details': "Source : {}\n{}".format(issue.data['html_url'].encode('utf-8'),
                                                    issue.data['body']),
                'component': 'Automation',
                'component': 'Automation',
                'labels': ['Automation'],
                'sprint': get_sprint(jira),
                'assignee': assignee,  # FIXME
                'issuetype': 'Task',
            }
            created_issue = jira.create_issue(**params)
            echo_skip("Created Jira ............{}/browse/{}".format(jira.jira_url,
                                                                     created_issue.key.encode('utf-8')))


def update_existing_issue_in_current_sprint(task, issue, jira):
    if isinstance(jira, MyJiraWrapper):
        if task.fields.status.name.encode('utf-8') == 'Done':
            echo_skip("No Need of Update! Already Done!")
        else:
            if issue.data['state'].encode('utf-8') == 'closed':
                # jira.update_sprint(task.key.encode('utf-8')) this is failing need to find some better solution
                jira.change_status(task.id.encode('utf-8'), 'Done')
                echo_skip("Status Updated Jira .....{}/browse/{}".format(jira.jira_url, task.key.encode('utf-8')))
