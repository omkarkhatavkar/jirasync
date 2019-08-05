from utils.utils import (
    echo_error
)
from wrappers.workflow_wrapper import (
    create_new_issue_in_backlog,
    update_existing_issue_in_current_sprint,
    create_pull_request_in_current_sprint
)


def start_issue_workflow(github_issues, jira, assignee=None):
    # create issue if those are not created
    for issue in github_issues:
        issue_text = str('issue#'+issue.project+'#'+issue.id)
        tasks = jira.search_existing_task(issue_text=issue_text)
        if len(tasks) > 1:
            print("Not a Valid Result! Found more than 1 tasks for"
                  " github {}".format(issue_text))
        elif len(tasks) == 1:  # Issue Already Exist, Check Assignee and Status
            echo_error("Updating Issue task for .....{}".format(issue.data['html_url']))
            update_existing_issue_in_current_sprint(tasks[0], issue, jira=jira)
        elif len(tasks) == 0:  # Create new issue in backlog.
            echo_error("Creating Issue task for.....{}".format(issue.data['html_url']))
            create_new_issue_in_backlog(
                issue,
                jira=jira,
                issue_text=issue_text,
                assignee=assignee
            )
        else:
            print("Nothing Happened")


def start_create_pull_requests_workflow(github_issues, jira, assignee=None):
    # Create PR task if those are not created
    for issue in github_issues:
        pr_text = "pr_create#{issue.project}#{issue.id}".format(issue=issue)
        tasks = jira.search_existing_task(issue_text=pr_text)
        if len(tasks) > 1:
            print("Not a Valid Result! Found more than 1 tasks for"
                  " github {}".format(pr_text))
        elif len(tasks) == 1:  # Issue Already Exist, Check Assignee and Status
            echo_error("Updating PR task for .....{}".format(issue.data['html_url']))
            update_existing_issue_in_current_sprint(tasks[0], issue, jira=jira)
        elif len(tasks) == 0:  # Create new issue in backlog.
            echo_error("Creating PR task for.....{}".format(issue.data['html_url']))
            create_pull_request_in_current_sprint(
                issue,
                jira=jira,
                issue_text=pr_text,
                assignee=assignee
            )
        else:
            print("Nothing Happened")


def start_review_pull_requests_workflow(github_issues, jira, assignee=None):
    # Create PR task if those are not created
    for issue in github_issues:
        pr_review_text = str('pr_review#' + issue.project + '#' + issue.id + '#' + assignee)
        tasks = jira.search_existing_task(issue_text=pr_review_text)
        if len(tasks) > 1:
            print("Not a Valid Result! Found more than 1 tasks for"
                  " github {}".format(pr_review_text))
        elif len(tasks) == 1:  # Issue Already Exist, Check Assignee and Status
            echo_error("Updating PR review task for .....{}".format(issue.data['html_url']))
            update_existing_issue_in_current_sprint(tasks[0], issue, jira=jira)
        elif len(tasks) == 0:  # Create new issue in backlog.
            echo_error("Creating PR review task for .....{}".format(issue.data['html_url']))
            create_pull_request_in_current_sprint(
                issue,
                jira=jira,
                issue_text=pr_review_text,
                assignee=assignee
            )
        else:
            print("Nothing Happened")
