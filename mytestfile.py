import pytest
import dsm
import os
from github import Github

DIRECTORY = "archive"
myfilename = "awesome-python.zip"


def test_check_rate_limits(capsys):
    query = "stars:>=5000 fork:true language:python"
    g = Github(os.getenv("API_TOKEN", "..."))
    repositories = g.search_repositories(query=query)
    dsm.check_rate_limit(g)
    output = capsys.readouterr().out.rstrip()
    assert output == "You have 30/30 API calls remaining"


def test_check_if_file():
    result = dsm.check_if_file(myfilename)
    assert result == True


def check_cwd():
    current_path = os.getcwd()
    return current_path


def mock_getcwd():
    return "archive"


def test_get_current_directory(monkeypatch):
    monkeypatch.setattr(os, "getcwd", mock_getcwd)
    assert check_cwd() == "archive"
