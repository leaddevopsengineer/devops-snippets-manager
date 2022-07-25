import os
import subprocess
from pathlib import Path
import json

home = str(Path.home())
path = home + "/notebook/code"

try:
    os.chdir(path)
    print("Current working directory: {0}".format(os.getcwd()))
except FileNotFoundError:
    print("Directory: {0} does not exist".format(path))
except NotADirectoryError:
    print("{0} is not a directory".format(path))
except PermissionError:
    print("You do not have permissions to change to {0}".format(path))

try:
    subprocess.call(["code", "-n", "convert.py"])
except subprocess.CalledProcessError as e:
    print(e.output)
    if e.output.startswith("error: {"):
        error = json.loads(e.output[2:])
        print(error["code"])
        print(error["message"])


def testme():
    print("This is a test")
