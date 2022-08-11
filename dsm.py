#!/usr/bin/env python3
""" DevOps Snippets Manager
    python3 dsm.py --viewfile --myfile clipboard.py
    python3 dsm.py --clipboard --createfile clipboard.py
    python3 dsm.py --clipboard --is_public --createfile main.tf
    python3 dsm.py --black --is_public --filename snippets/argparse/generic.py
    python3 dsm.py --clipboard --is_public --createfile testfile.py
"""

import argparse
from fileinput import filename
import os
from xmlrpc.client import ResponseError
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
import pyperclip as pc
from black import NothingChanged, WriteBack, format_str, FileMode
import black
import sys
import io
import tokenize
import requests
from pprint import pprint
import json
from github import Github
import asyncio
from datetime import datetime
import backoff
import github
from os.path import exists
from time import sleep
from random import random
from threading import Thread
import multiprocessing
import time

DIRECTORY = "archive"
start_time = datetime.now().timestamp()
FileContent = str
Encoding = str
NewLine = str
list_of_requests = []

from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)


def check_rate_limit(g):
    """ Checks rate limit so that when I'm downloading python code I know where I'm at with rate limit """
    rate_limit = g.get_rate_limit()
    rate = rate_limit.search
    if rate.remaining == 0:
        print(f'You have 0/{rate.limit} API calls remaining. Reset time: {rate.reset}')
    else:
        print(f'You have {rate.remaining}/{rate.limit} API calls remaining')


def check_if_file(myfilename):
    """ Checks to see if the file is already downloaded so we can skip it. """
    file_exists = exists(DIRECTORY + "/" + myfilename)
    if file_exists:
        print(
            "************************************* File Exists ******************************************************************")
        return True
    else:
        print(
            "************************************* File Does Not Exists ******************************************************************")
        return False


def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).
    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF). Necessary for Black
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline


def save_repos(repo):
    """ Trying to break this out so its under control """
    print(f'{repo.clone_url}, {repo.stargazers_count} stars')
    if repo.stargazers_count > 500:
        archive_link = repo.get_archive_link("zipball", repo.default_branch)
        response = requests.get(archive_link, headers={"Authorization": f"token {os.getenv('API_TOKEN', '...')}"})
        open(DIRECTORY + "/" + repo.name + ".zip", 'wb').write(response.content)
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                print(file_content)


@backoff.on_exception(backoff.expo, github.GithubException)
def search_github():
    """
    query = '+'.join(keywords) + '+language:python+in:readme+in:description'
    repositories = g.search_repositories(query=query)
    The backoff decorator works sometimes. It needs to be able to accept multiple exceptions.
    """
    name = multiprocessing.current_process().name
    print("Starting %s \n" % name)
    time.sleep(0)
    keywords = 'python'
    # query = '+'.join(keywords) + '+language:python+in:readme+in:description+stars:>=500'
    # query = '+stars:>=500+fork:true+language:python'
    query = 'stars:>=500 fork:true language:python'
    g = Github(os.getenv('API_TOKEN', '...'))
    repositories = g.search_repositories(query=query)
    # Add try except block with this exception looking for an empty repo - github.GithubException.GithubException
    for repo in repositories:
        check_rate_limit(g)
        time.sleep(0)
        filename = repo.name + ".zip"
        print(f'Here is the current filename {filename}')
        if check_if_file(filename):
            continue
        else:
            save_repos(repo)


def viewfile(codeblock, console):
    """ Fix this so it displays any type of file """
    snippet = Syntax(codeblock.read(), "python")
    console.print(snippet)
    codeblock.close()


def createfile(clipboard, filename, is_public):
    """ This needs to be tested and expanded """
    snippet = pc.paste()
    if filename.endswith('.py'):
        try:
            bytes_snippet = bytes(snippet, 'UTF-8')
            src_contents, encoding, newline = decode_bytes(bytes_snippet)
            new_contents = black.format_file_contents(src_contents, fast=True, mode=FileMode())
            with open(filename, "w", encoding=encoding, newline=newline) as f:
                f.write(new_contents)
                f.close()
                pushgist(filename, is_public)
        except NothingChanged:
            print("The file has not changed")
    else:
        bytes_snippet = bytes(snippet, 'UTF-8')
        src_contents, encoding, newline = decode_bytes(bytes_snippet)
        with open(filename, "w", encoding=encoding, newline=newline) as n:
            n.write(src_contents)
            n.close()
            pushgist(filename, is_public)


def runblack(filename, is_public):
    """ Works most of the time if its a python file that uses proper indentation """
    with open(filename, "rb") as buf:
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        new_contents = black.format_file_contents(src_contents, fast=True, mode=FileMode())
        with open(filename, "w", encoding=encoding, newline=newline) as f:
            f.write(new_contents)
            f.close()
            pushgist(filename, is_public)
    except NothingChanged:
        print("The file has not changed")


def pushgist(filename, is_public):
    """ This works most of the time but would be nice to use API_TOKEN as an argument so we can target different
    github accounts"""
    token = os.getenv('API_TOKEN', '...')
    onlyfilename = os.path.basename(filename)
    query_url = "https://api.github.com/gists"
    new_filename = filename
    content = open(filename, 'r').read()
    gist_dict = {'public': is_public, 'files': {onlyfilename: {'content': content}}}
    headers = {'Authorization': f'token {token}'}
    r = requests.post(query_url, headers=headers, data=json.dumps(gist_dict))
    pprint(r.json())


# --------------------------------------------------
def get_args():
    """Get command-line arguments. Playing around with multiprocessor. Need to get back to it. """

    parser = argparse.ArgumentParser(
        description="DevOps Snippets Manager -- Import all your code snippets",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--myfile", metavar="FILE", type=argparse.FileType('r', encoding='UTF-8'),
                        help='A block of code you would like to create a new file from')
    parser.add_argument("-v", "--viewfile", action="store_true",
                        help='A block of code you would like to view from the clipboard')
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help='A block of code you would like to turn into a file from the clipboard')
    parser.add_argument("-p", "--is_public", action="store_true", default=False,
                        help='Chose if gist is public or private. Default is private')
    parser.add_argument("-f", "--filename", help="The name of the file you want to save")
    parser.add_argument("-n", "--createfile", help="The name of the file you want to save")
    parser.add_argument("-b", "--black", action="store_true", help="The name of the file you want to format with black")
    parser.add_argument("-g", "--pushgist", action="store_true",
                        help='A block of code you would like to push to github gists')
    return parser.parse_args()


def foo():
    name = multiprocessing.current_process().name
    print("Starting %s \n" % name)
    time.sleep(3)
    print("Exiting %s \n" % name)


# --------------------------------------------------
def main():
    """Start Here"""
    console = Console()
    args = get_args()
    if args.viewfile and args.myfile:
        viewfile(args.myfile, console)
    elif args.clipboard and args.createfile:
        createfile(args.clipboard, args.createfile, args.is_public)
    elif args.black and args.filename:
        runblack(args.filename, args.is_public)
    elif args.pushgist and args.filename:
        pushgist(args.filename, args.is_public)
    # search_github()
    # print('Starting background task...')
    # daemon = Thread(target=search_github, daemon=True, name='GithubSearch')
    # daemon.start()
    background_process = multiprocessing.Process \
        (name='github_search', \
         target=search_github).start()


# --------------------------------------------------
if __name__ == '__main__':
    main()
