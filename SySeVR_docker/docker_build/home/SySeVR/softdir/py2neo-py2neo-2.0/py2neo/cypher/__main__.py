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


import json
import os
import sys

from py2neo.core import Relationship, Node, Path
from py2neo.cypher.error import CypherError, CypherTransactionError
from py2neo.util import compact


HELP = """\
Usage: {script} [«options»] «statement» [ [«options»] «statement» ... ]

Execute a Cypher statement against a Neo4j database.

Formatting Options:
  -c --csv    write output as comma separated values
  -h --human  write output as human-readable text
  -j --json   write output as JSON (See http://json.org)
  -t --tsv    write output as tab separated values

Parameter Options:
  -f «parameter-file»
  -p «name» «value»

Environment:
  NEO4J_URI - base URI of Neo4j database, e.g. http://localhost:7474

Report bugs to nigel@py2neo.org
"""


def _help(script):
    sys.stderr.write(HELP.format(script=os.path.basename(script)))
    sys.stderr.write("\n")


class CypherCommandLine(object):

    def __init__(self, graph):
        self.parameters = {}
        self.parameter_filename = None
        self.graph = graph
        self.tx = None

    def begin(self):
        self.tx = self.graph.cypher.begin()

    def set_parameter(self, key, value):
        try:
            self.parameters[key] = json.loads(value)
        except ValueError:
            self.parameters[key] = value

    def set_parameter_filename(self, filename):
        self.parameter_filename = filename

    def execute(self, statement):
        import codecs
        if self.parameter_filename:
            columns = None
            with codecs.open(self.parameter_filename, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if columns is None:
                        columns = line.split(",")
                    elif line:
                        values = json.loads("[" + line + "]")
                        p = dict(self.parameters)
                        p.update(zip(columns, values))
                        self.tx.execute(statement, p)
        else:
            self.tx.execute(statement, self.parameters)
        return self.tx.flush()

    def commit(self):
        self.tx.commit()


def dehydrate(value):
    if isinstance(value, list):
        out = list(map(dehydrate, value))
    elif isinstance(value, Node):
        out = {
            "self": value.ref,
            "properties": value.properties,
            "labels": list(value.labels),
        }
    elif isinstance(value, Relationship):
        out = {
            "self": value.ref,
            "properties": value.properties,
            "start": value.start_node.ref,
            "type": value.type,
            "end": value.end_node.ref,
        }
    elif isinstance(value, Path):
        out = [dehydrate(relationship) for relationship in value.relationships]
    else:
        out = value
    return out


def main():
    import os
    import sys
    from py2neo.core import ServiceRoot
    from py2neo.packages.httpstream.packages.urimagic import URI
    script, args = sys.argv[0], sys.argv[1:]
    if not args:
        _help(script)
        sys.exit(0)
    uri = URI(os.getenv("NEO4J_URI", ServiceRoot.DEFAULT_URI)).resolve("/")
    service_root = ServiceRoot(uri.string)
    out = sys.stdout
    output_format = None
    command_line = CypherCommandLine(service_root.graph)
    command_line.begin()
    while args:
        arg = args.pop(0)
        if arg.startswith("-"):
            if arg in ("-p", "--parameter"):
                key = args.pop(0)
                value = args.pop(0)
                command_line.set_parameter(key, value)
            elif arg in ("-f",):
                command_line.set_parameter_filename(args.pop(0))
            elif arg in ("-h", "--human"):
                output_format = None
            elif arg in ("-j", "--json"):
                output_format = "json"
            elif arg in ("-c", "--csv"):
                output_format = "csv"
            elif arg in ("-t", "--tsv"):
                output_format = "tsv"
            else:
                raise ValueError("Unrecognised option %s" % arg)
        else:
            try:
                results = command_line.execute(arg)
            except CypherError as error:
                sys.stderr.write("%s: %s\n\n" % (error.__class__.__name__, error.args[0]))
            else:
                for result in results:
                    if output_format == "json":
                        records = [compact(dict(zip(result.columns, map(dehydrate, record))))
                                   for record in result]
                        out.write(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=2))
                        out.write("\n")
                    elif output_format in ("csv", "tsv"):
                        separator = "," if output_format == "csv" else "\t"
                        out.write(separator.join(json.dumps(column, separators=",:",
                                                            ensure_ascii=False)
                                                 for column in result.columns))
                        out.write("\n")
                        for record in result:
                            out.write(separator.join(json.dumps(dehydrate(value),
                                                                separators=",:",
                                                                ensure_ascii=False,
                                                                sort_keys=True)
                                                     for value in record))
                            out.write("\n")
                    else:
                        out.write(repr(result))
                    out.write("\n")
    try:
        command_line.commit()
    except CypherTransactionError as error:
        sys.stderr.write(error.args[0])
        sys.stderr.write("\n")


if __name__ == "__main__":
    main()
