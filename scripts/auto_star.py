#!/usr/bin/env python3
"""Automatically star all repositories in a GitHub organization.

Intended to run on a schedule (for example, once per day in GitHub Actions).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterable

API_BASE = "https://api.github.com"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def github_request(method: str, url: str, token: str, params: dict | None = None) -> tuple[int, str]:
    if params:
        query = urllib.parse.urlencode(params)
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{query}"

    req = urllib.request.Request(
        url=url,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AutoStar-Script",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


def iter_org_repos(org: str, token: str) -> Iterable[dict]:
    page = 1
    while True:
        status, body = github_request(
            "GET",
            f"{API_BASE}/orgs/{org}/repos",
            token,
            params={"per_page": 100, "page": page, "type": "public", "sort": "full_name"},
        )
        if status != 200:
            print(f"Failed to list repos for org '{org}': HTTP {status} {body}", file=sys.stderr)
            sys.exit(1)

        repos = json.loads(body)
        if not repos:
            break

        for repo in repos:
            yield repo

        page += 1


def is_starred(owner: str, repo: str, token: str) -> bool:
    status, body = github_request("GET", f"{API_BASE}/user/starred/{owner}/{repo}", token)
    if status == 204:
        return True
    if status == 404:
        return False

    print(f"Failed to check star status for {owner}/{repo}: HTTP {status} {body}", file=sys.stderr)
    sys.exit(1)


def star_repo(owner: str, repo: str, token: str) -> bool:
    status, _ = github_request("PUT", f"{API_BASE}/user/starred/{owner}/{repo}", token)
    return status in (204, 304)


def main() -> None:
    token = require_env("GITHUB_TOKEN")
    org = os.getenv("TARGET_ORG", "ZJU-LLM-Safety")
    sleep_seconds = float(os.getenv("REQUEST_SLEEP_SECONDS", "0.2"))

    total = 0
    newly_starred = 0

    for repo in iter_org_repos(org, token):
        owner = repo["owner"]["login"]
        name = repo["name"]
        full_name = repo["full_name"]
        total += 1

        if is_starred(owner, name, token):
            print(f"Already starred: {full_name}")
            continue

        ok = star_repo(owner, name, token)
        if not ok:
            print(f"Failed to star: {full_name}", file=sys.stderr)
            sys.exit(1)

        newly_starred += 1
        print(f"Starred: {full_name}")
        time.sleep(sleep_seconds)

    print(f"Done. Checked {total} repos in '{org}', newly starred {newly_starred} repos.")


if __name__ == "__main__":
    main()
