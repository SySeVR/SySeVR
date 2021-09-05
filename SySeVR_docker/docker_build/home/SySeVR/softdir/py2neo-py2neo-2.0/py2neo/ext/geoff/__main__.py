#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2014, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import codecs
import os
import sys

from py2neo.core import ServiceRoot
from py2neo.packages.httpstream.packages.urimagic import URI

from py2neo.ext.geoff import GeoffLoader


HELP = """\
Usage: {script} load «geoff-data»
       {script} load -f «geoff-file»
       {script} load -x «xml-data»
       {script} load -x -f «xml-file»

Load data into Neo4j from Geoff (or XML) data, optionally read from a file.

Environment:
  NEO4J_URI - base URI of Neo4j database, e.g. http://localhost:7474

Report bugs to nigel@py2neo.org
"""


def _help(script):
    sys.stderr.write(HELP.format(script=os.path.basename(script)))
    sys.stderr.write("\n")


def main():
    try:
        script, format_, args = sys.argv[0], sys.argv[1], sys.argv[2:]
    except IndexError:
        _help(sys.argv[0])
        sys.exit(1)

    uri = URI(os.getenv("NEO4J_URI", ServiceRoot.DEFAULT_URI)).resolve("/")
    service_root = ServiceRoot(uri.string)

    loader = GeoffLoader(service_root.graph)
    load = loader.load
    results = []

    try:
        while args:
            arg = args.pop(0)
            if arg.startswith("-"):
                if arg in ("-f", "--file"):
                    filename = args.pop(0)
                    with codecs.open(filename, encoding="utf-8") as f:
                        data = f.read()
                    results = load(data)
                elif arg in ("-x", "--xml"):
                    load = loader.load_xml
                else:
                    raise ValueError("Unknown option %s" % arg)
            else:
                results = load(arg)
            try:
                for result in results:
                    max_key_len = max(map(len, result.keys()))
                    for key in sorted(result):
                        reference = result.get_ref(key)
                        print("%s %s" % (key.ljust(max_key_len), reference))
            except TypeError:
                pass
    except Exception as error:
        sys.stderr.write(error.args[0])
        sys.stderr.write("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
