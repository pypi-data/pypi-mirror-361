from mcp.server.fastmcp import FastMCP  # ✅ DO NOT import mcp root
from jira import JIRA
from typing import List
import os

mcp = FastMCP("Jira MCP Server")

def get_jira_client():
    return JIRA(
        server=os.environ["JIRA_URL"],
        basic_auth=(os.environ["JIRA_USER"], os.environ["JIRA_TOKEN"])
    )

@mcp.tool(title="List Jira Projects")
def list_projects() -> List[str]:
    jira = get_jira_client()
    return [project.name for project in jira.projects()]

@mcp.tool(title="Get Issues for Project")
def get_issues(project_key: str) -> List[str]:
    jira = get_jira_client()
    issues = jira.search_issues(f'project={project_key}', maxResults=10)
    return [f"{issue.key}: {issue.fields.summary}" for issue in issues]

@mcp.tool(title="Get Issue Details")
def get_issue_details(issue_key: str) -> str:
    jira = get_jira_client()
    issue = jira.issue(issue_key)
    return f"{issue.key} - {issue.fields.summary}\nStatus: {issue.fields.status.name}"

@mcp.tool(title="Create Issue in Project")
def create_issue(project_key: str, summary: str, description: str) -> str:
    jira = get_jira_client()
    new_issue = jira.create_issue(
        project=project_key,
        summary=summary,
        description=description,
        issuetype={"name": "Task"}
    )
    return f"Issue {new_issue.key} created."

def run_server():
    mcp.run()  # ✅ This will work now
