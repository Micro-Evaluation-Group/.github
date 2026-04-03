"""
Updates the profile README.md with dynamic content from GitHub API and RSS feeds.

Replaces content between marker comments:
  <!-- ACTIVITY:START --> ... <!-- ACTIVITY:END -->
  <!-- BLOG:START --> ... <!-- BLOG:END -->
"""

import os
import re
from datetime import datetime, timezone

import requests

ORG_NAME = os.environ.get("ORG_NAME", "Micro-Evaluation-Group")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
BLOG_RSS_URL = os.environ.get("BLOG_RSS_URL", "")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "profile", "README.md")
MAX_ACTIVITY_ITEMS = 8
MAX_BLOG_ITEMS = 5


def github_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_recent_activity():
    """Fetch recent public events for the org."""
    url = f"https://api.github.com/orgs/{ORG_NAME}/events?per_page=30"
    resp = requests.get(url, headers=github_headers(), timeout=15)
    if resp.status_code != 200:
        return None
    return resp.json()


def format_activity(events):
    """Format GitHub events into markdown list items."""
    lines = []
    seen = set()

    for event in events:
        if len(lines) >= MAX_ACTIVITY_ITEMS:
            break

        repo = event.get("repo", {}).get("name", "")
        event_type = event.get("type", "")
        created = event.get("created_at", "")

        if created:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = dt.strftime("%b %d")
        else:
            date_str = ""

        line = None
        dedup_key = None

        if event_type == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            count = len(commits)
            dedup_key = f"push-{repo}"
            line = f"🔨 Pushed **{count} commit{'s' if count != 1 else ''}** to [{repo}](https://github.com/{repo})"

        elif event_type == "CreateEvent":
            ref_type = event.get("payload", {}).get("ref_type", "")
            ref = event.get("payload", {}).get("ref", "")
            dedup_key = f"create-{repo}-{ref}"
            if ref_type == "repository":
                line = f"🆕 Created new repository [{repo}](https://github.com/{repo})"
            elif ref_type == "branch":
                line = f"🌿 Created branch `{ref}` in [{repo}](https://github.com/{repo})"

        elif event_type == "ReleaseEvent":
            tag = event.get("payload", {}).get("release", {}).get("tag_name", "")
            dedup_key = f"release-{repo}-{tag}"
            line = f"🚀 Released **{tag}** of [{repo}](https://github.com/{repo})"

        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "")
            number = event.get("payload", {}).get("issue", {}).get("number", "")
            dedup_key = f"issue-{repo}-{number}"
            if action == "opened":
                line = f"📋 Opened issue #{number} in [{repo}](https://github.com/{repo})"

        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "")
            number = event.get("payload", {}).get("pull_request", {}).get("number", "")
            dedup_key = f"pr-{repo}-{number}"
            if action == "opened":
                line = f"🔃 Opened PR #{number} in [{repo}](https://github.com/{repo})"
            elif action == "closed" and event.get("payload", {}).get("pull_request", {}).get("merged"):
                line = f"✅ Merged PR #{number} in [{repo}](https://github.com/{repo})"

        if line and dedup_key and dedup_key not in seen:
            seen.add(dedup_key)
            lines.append(f"- {line} — *{date_str}*" if date_str else f"- {line}")

    return lines


def fetch_blog_posts():
    """Fetch latest blog posts from RSS feed."""
    if not BLOG_RSS_URL:
        return None

    try:
        import feedparser
        feed = feedparser.parse(BLOG_RSS_URL)
        lines = []
        for entry in feed.entries[:MAX_BLOG_ITEMS]:
            title = entry.get("title", "Untitled")
            link = entry.get("link", "#")
            published = entry.get("published_parsed")
            if published:
                dt = datetime(*published[:6], tzinfo=timezone.utc)
                date_str = dt.strftime("%b %d, %Y")
                lines.append(f"- [{title}]({link}) — *{date_str}*")
            else:
                lines.append(f"- [{title}]({link})")
        return lines
    except Exception:
        return None


def replace_section(content, start_marker, end_marker, new_lines):
    """Replace content between marker comments."""
    pattern = re.compile(
        rf"({re.escape(start_marker)}\n).*?(\n{re.escape(end_marker)})",
        re.DOTALL,
    )
    replacement = rf"\1{chr(10).join(new_lines)}\2"
    return pattern.sub(replacement, content)


def main():
    with open(README_PATH, "r") as f:
        content = f.read()

    # Update activity section
    events = fetch_recent_activity()
    if events:
        activity_lines = format_activity(events)
        if activity_lines:
            now = datetime.now(timezone.utc).strftime("%b %d, %Y at %H:%M UTC")
            activity_lines.append(f"\n<sub>Last updated: {now}</sub>")
            content = replace_section(
                content, "<!-- ACTIVITY:START -->", "<!-- ACTIVITY:END -->", activity_lines
            )

    # Update blog section
    blog_lines = fetch_blog_posts()
    if blog_lines:
        content = replace_section(
            content, "<!-- BLOG:START -->", "<!-- BLOG:END -->", blog_lines
        )

    with open(README_PATH, "w") as f:
        f.write(content)

    print("README updated successfully.")


if __name__ == "__main__":
    main()
