# MIT License

# Copyright (c) 2021 Northern.tech

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import json

from shutil import rmtree
from collections import OrderedDict
from typing import Union

from glrp.pretty import pretty


def find(name, recursive=True, directories=False, files=True, extension=None):
    assert files or directories
    assert os.path.isdir(name)
    for root, subdirs, subfiles in os.walk(name):
        if directories:
            for dir in subdirs:
                if not extension or (extension and dir.endswith(extension)):
                    yield os.path.join(root, dir) + "/"
        if files:
            for file in subfiles:
                if not extension or (extension and file.endswith(extension)):
                    yield os.path.join(root, file)
        if not recursive:
            return  # End iteration after looking through first (top) level


def rm(path: str, missing_ok=False):
    if not missing_ok:
        assert os.path.exists(path)
    if missing_ok and not os.path.exists(path):
        return False
    if os.path.isdir(path):
        rmtree(path)
    else:  # Assume path is a file
        os.remove(path)  # Will raise exception if missing
    return True


def mkdir(path: str, exist_ok=True):
    os.makedirs(path, exist_ok=exist_ok)


def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def save_file(path, data):
    if "/" in path:
        mkdir("/".join(path.split("/")[0:-1]))
    with open(path, "w") as f:
        f.write(data)


def read_json(path) -> Union[OrderedDict, None]:
    try:
        with open(path, "r") as f:
            return json.loads(f.read(), object_pairs_hook=OrderedDict)
    except FileNotFoundError:
        return None
    except NotADirectoryError:
        return None
    except json.decoder.JSONDecodeError as ex:
        print("Error reading json file '{}': {}".format(path, ex))
        sys.exit(1)


def write_json(path, data):
    data = pretty(data) + "\n"
    return save_file(path, data)
