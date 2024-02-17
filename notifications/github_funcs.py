import os
from datetime import datetime
from typing import Optional

import requests
from requests import Response

from notifications.models import Notification, Comment

NOTIFICATIONS_URL = "https://api.github.com/notifications"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_notifications(token: str) -> Response:
    return requests.get(
        NOTIFICATIONS_URL,
        headers=get_headers(token),
    )


def check_token(token: str) -> bool:
    return get_notifications(token).status_code == 200


class AuthenticationError(Exception):
    pass


def get_notifications_json(token: str) -> dict:
    response = get_notifications(token)
    if response.status_code == 401:
        raise AuthenticationError("Please refresh token")
    return response.json()


def build_notification_from_json(n: dict, token: str) -> Notification:
    latest_comment_url = n["subject"]["latest_comment_url"] or n["subject"]["url"]
    latest_comment = get_latest_comment(latest_comment_url, token)
    manual_url = (
        n["subject"]["url"]
        .replace("api.", "")
        .replace("repos/", "")
        .replace("pulls", "pull")
    )
    return Notification(
        id=n["id"],
        repo=n["repository"]["full_name"],
        title=n["subject"]["title"],
        reason=n["reason"],
        url=manual_url,
        latest_comment=latest_comment,
        updated_at=datetime.strptime(n["updated_at"], "%Y-%m-%dT%H:%M:%SZ"),
    )


def get_latest_comment(latest_comment_url, token) -> Optional[Comment]:
    latest_url_response = requests.get(
        latest_comment_url,
        headers=get_headers(token),
    )
    if latest_url_response.status_code != 200:
        return None
    else:
        latest_url = latest_url_response.json()
        latest_url = Comment(
            latest_url["id"],
            latest_url["body"],
            latest_url["user"]["login"],
            latest_url["html_url"],
        )
    return latest_url


def get_all_user_notifications(token: str) -> list[Notification]:

    notifications = get_notifications_json(token)
    return [build_notification_from_json(n, token) for n in notifications]


def get_unread_user_notifications(token: str) -> list[Notification]:
    notifications = get_notifications_json(token)
    return [build_notification_from_json(n, token) for n in notifications if n.unread]


if __name__ == "__main__":
    print(get_all_user_notifications(os.environ.get("GH_NOTIFICATIONS_TOKEN")))


# EXAMPLE RESPONSE:
"""
[
  {
    "id": "1",
    "repository": {
      "id": 1296269,
      "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
      "name": "Hello-World",
      "full_name": "octocat/Hello-World",
      "owner": {
        "login": "octocat",
        "id": 1,
        "node_id": "MDQ6VXNlcjE=",
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "gravatar_id": "",
        "url": "https://api.github.com/users/octocat",
        "html_url": "https://github.com/octocat",
        "followers_url": "https://api.github.com/users/octocat/followers",
        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
        "organizations_url": "https://api.github.com/users/octocat/orgs",
        "repos_url": "https://api.github.com/users/octocat/repos",
        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
        "received_events_url": "https://api.github.com/users/octocat/received_events",
        "type": "User",
        "site_admin": false
      },
      "private": false,
      "html_url": "https://github.com/octocat/Hello-World",
      "description": "This your first repo!",
      "fork": false,
      "url": "https://api.github.com/repos/octocat/Hello-World",
      "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
      "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
      "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
      "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
      "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
      "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
      "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
      "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
      "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
      "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
      "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
      "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
      "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
      "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
      "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
      "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
      "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
      "git_url": "git:github.com/octocat/Hello-World.git",
      "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
      "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
      "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
      "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
      "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
      "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
      "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
      "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
      "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
      "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
      "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
      "ssh_url": "git@github.com:octocat/Hello-World.git",
      "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
      "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
      "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
      "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
      "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
      "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
      "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
      "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks"
    },
    "subject": {
      "title": "Greetings",
      "url": "https://api.github.com/repos/octokit/octokit.rb/issues/123",
      "latest_comment_url": "https://api.github.com/repos/octokit/octokit.rb/issues/comments/123",
      "type": "Issue"
    },
    "reason": "subscribed",
    "unread": true,
    "updated_at": "2014-11-07T22:01:45Z",
    "last_read_at": "2014-11-07T22:01:45Z",
    "url": "https://api.github.com/notifications/threads/1",
    "subscription_url": "https://api.github.com/notifications/threads/1/subscription"
  }
]
"""
