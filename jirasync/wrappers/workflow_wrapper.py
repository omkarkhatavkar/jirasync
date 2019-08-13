# coding: utf-8
from jirasync.utils import echo_skip, get_sprint
from jirasync.wrappers.jirawrapper import MyJiraWrapper


def create_new_issue_in_backlog(issue, jira, issue_text, assignee=None):
    if assignee is None:
        assignee = jira.userid.encode("utf-8")
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                "summary": "{} -{}".format(
                    issue_text.encode("utf-8"), issue.title.encode("utf-8")
                ),
                "details": "Source : {}\n{}".format(
                    issue.data["html_url"].encode("utf-8"), issue.data["body"]
                ),
                "component": "Automation",
                "component": "Automation",
                "labels": ["Automation"],
                "sprint": "backlog",
                "assignee": assignee,  # FIXME
                "issuetype": "Task",
            }
            created_issue = jira.create_issue(**params)
            echo_skip(
                "Created Jira ............{}/browse/{}".format(
                    jira.jira_url, created_issue.key.encode("utf-8")
                )
            )


def create_pull_request_in_current_sprint(
    issue, jira, issue_text, assignee=None
):
    if assignee is None:
        assignee = jira.userid.encode("utf-8")
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                "summary": "{} -{}".format(
                    issue_text.encode("utf-8"), issue.title.encode("utf-8")
                ),
                "details": "Source : {}\n{}".format(
                    issue.data["html_url"].encode("utf-8"), issue.data["body"]
                ),
                "component": "Automation",
                "labels": ["Automation"],
                "sprint": get_sprint(jira),
                "assignee": assignee,  # FIXME
                "issuetype": "Task",
            }
            created_issue = jira.create_issue(**params)
            echo_skip(
                "Created Jira ............{}/browse/{}".format(
                    jira.jira_url, created_issue.key.encode("utf-8")
                )
            )


def create_pull_request_review_in_current_sprint(
    issue, jira, issue_text, assignee=None
):
    if assignee is None:
        assignee = jira.userid.encode("utf-8")
    if isinstance(jira, MyJiraWrapper):
        if issue_text is not None:
            params = {
                "summary": "{}#{} -{}".format(
                    issue_text.encode("utf-8"),
                    assignee,
                    issue.title.encode("utf-8"),
                ),
                "details": "Source : {}\n{}".format(
                    issue.data["html_url"].encode("utf-8"), issue.data["body"]
                ),
                "component": "Automation",
                "component": "Automation",
                "labels": ["Automation"],
                "sprint": get_sprint(jira),
                "assignee": assignee,  # FIXME
                "issuetype": "Task",
            }
            created_issue = jira.create_issue(**params)
            echo_skip(
                "Created Jira ............{}/browse/{}".format(
                    jira.jira_url, created_issue.key.encode("utf-8")
                )
            )


def update_existing_issue_in_current_sprint(task, issue, jira, issue_text,
                                            assignee=None):
    if isinstance(jira, MyJiraWrapper):
        # check correct assignment
        if 'pr_create' in task.fields.summary:
            if task.fields.assignee is None:
                jira.change_assignee(task.id.encode(), assignee)

        elif task.fields.status.name.encode("utf-8") == "Done":
            echo_skip("No Need of Update! Already Done!")
        else:
            # change the title id it was update in source (e.g. github)
            if issue.title.encode("utf-8") not in task.fields.summary.encode(
                "utf-8"
            ):
                new_summary = "{} -{}".format(
                    issue_text, issue.title.encode("utf-8")
                )
                jira.change_title(task.id.encode(), new_summary)
                echo_skip(
                    "Title Updated Jira .....{}/browse/{}".format(
                        jira.jira_url, task.key.encode("utf-8")
                    )
                )
            elif issue.data["state"].encode("utf-8") == "closed":
                # jira.update_sprint(task.key.encode('utf-8')) this is failing
                # need to find some better solution
                jira.change_status(task.id.encode("utf-8"), "Done")
                echo_skip(
                    "Status Updated Jira .....{}/browse/{}".format(
                        jira.jira_url, task.key.encode("utf-8")
                    )
                )
