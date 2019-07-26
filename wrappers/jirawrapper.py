from jiraprompt.wrapper import (
    JiraWrapper,
    IssueFields,
)


class MyJiraWrapper(JiraWrapper):

    def create_issue(self, summary, details=None, component=None,
                     labels=None, assignee=None, sprint=None,
                     issuetype='Task'):
        """
        Create an issue (by default, a Story) in the agile sprint.

        Args:
          summary (str): issue title/summary
          details (str): detailed issue description
          component (str): component name
          labels (list of str): labels
          assignee (str): user id of assignee
          sprint (str): sprint name, sprint number, or 'backlog'
                Default is current sprint
          issueype (str): issue type, default is "Task",
                you likely won't change this.

        Returns:
          The newly created JIRA.Issue resource
        """

        if labels and not isinstance(labels, list):
            raise TypeError("labels must be a list")

        if not sprint:
            sprint_id = self.current_sprint_id
        elif sprint != 'backlog':
            _, sprint_id = self.find_sprint(sprint)

        f = IssueFields()
        comp_name_server_side, _ = self.find_component(component)
        f.summary(summary) \
            .description(details) \
            .component(comp_name_server_side) \
            .labels(labels) \
            .project(id=self.project_id) \
            .issuetype(issuetype)

        new_issue = self.jira.create_issue(**f.kwarg)

        if assignee:
            self.jira.assign_issue(new_issue.key, assignee)

        # FIXME: Uncomment after testing, this was disabled because of
        #        containerized Jira has no scrum plugin.
        # if sprint == "backlog":
        #     self.jira.move_to_backlog([new_issue.key])
        # else:
        #     self.jira.add_issues_to_sprint(sprint_id, [new_issue.key])

        return new_issue

    def change_status(self, issue_name, new_status_name):
        issue = self.jira.issue(issue_name)
        avail_statuses = self.get_avail_statuses(issue)
        new_status_id = self.get_avail_status_id(avail_statuses, new_status_name)
        self.jira.transition_issue(issue, new_status_id)

    def update_sprint(self, issue_name):
        issue = self.jira.issue(issue_name)
        current_sprint_id = self.current_sprint_id
        if None not in (current_sprint_id, issue.key):
            self.jira.add_issues_to_sprint(current_sprint_id, issue.key)

