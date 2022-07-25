from bs4 import BeautifulSoup
from markdown import markdown
import re


def markdown(markdown_string):

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r"<pre>(.*?)</pre>", " ", html)
    html = re.sub(r"<code>(.*?)</code>", " ", html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(text=True))

    return text
