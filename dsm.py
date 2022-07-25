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


FileContent = str
Encoding = str
NewLine = str


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

def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).
    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF).
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline

def viewfile(codeblock, console):
    """ Fix this so it displays any type of file """
    snippet = Syntax(codeblock.read(), "python")
    console.print(snippet)
    codeblock.close()
       
def createfile(clipboard, filename, is_public):
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
            with open(filename, "w",encoding=encoding, newline=newline) as n:
                n.write(src_contents)
                n.close()
                pushgist(filename, is_public)
            
def runblack(filename, is_public):
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
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="DevOps Snippets Manager -- Import all your code snippets",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--myfile", metavar="FILE",type=argparse.FileType('r', encoding='UTF-8'), help='A block of code you would like to create a new file from')
    parser.add_argument("-v", "--viewfile",action="store_true", help='A block of code you would like to view from the clipboard')
    parser.add_argument("-c", "--clipboard",action="store_true", help='A block of code you would like to turn into a file from the clipboard')
    parser.add_argument("-p", "--is_public",action="store_true", default=False, help='Chose if gist is public or private. Default is private')
    parser.add_argument("-f", "--filename", help="The name of the file you want to save")
    parser.add_argument("-n", "--createfile", help="The name of the file you want to save")
    parser.add_argument("-b", "--black", action="store_true", help="The name of the file you want to format with black")
    parser.add_argument("-g", "--pushgist",action="store_true", help='A block of code you would like to push to github gists')
    return parser.parse_args()


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

    


# --------------------------------------------------
if __name__ == '__main__':
    main()

