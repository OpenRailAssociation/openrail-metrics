"""Tests for git operations module."""

from openrail_metrics.git_ops import sanitize_repo_name


def test_sanitize_repo_name():
    assert sanitize_repo_name("https://github.com/org/repo.git") == "github_com_org_repo"
    assert sanitize_repo_name("https://gitlab.com/user/project.git") == "gitlab_com_user_project"
    assert sanitize_repo_name("git@github.com:org/repo.git") == "git_github_com_org_repo"
