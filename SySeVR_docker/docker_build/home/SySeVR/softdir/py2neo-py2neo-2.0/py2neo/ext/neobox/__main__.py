#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


from __future__ import print_function

import os
import sys

from py2neo.ext.neobox.core import Warehouse
from py2neo.util import ustr


HELP = """\
Usage: {script} list
       {script} install «name» «edition» «version»
       {script} remove «name» [force]
       {script} rename «name» «new_name»
       {script} start «name»
       {script} stop «name»
       {script} open «name»
       {script} drop «name» [force]

Manager for multiple Neo4j server installations (boxes), each running on
its own unique port.

Commands:
  list     List all installed boxes
  install  Install Neo4j into a box
  remove   Remove a box
  rename   Rename a box
  start    Start a database server
  stop     Stop a database server
  open     Open the browser for a running server
  drop     Drop a database store

Environment:
  NEOBOX_HOME - base directory for installed boxes

Report bugs to nigel@py2neo.org
"""


def _help(script):
    print(HELP.format(script=os.path.basename(script)))


def _list(*args):
    warehouse = Warehouse()
    for box in warehouse.boxes():
        print(box.name)


def main():
    script, args = sys.argv[0], sys.argv[1:]
    try:
        if args:
            command, args = args[0], args[1:]
            if command == "help":
                _help(script)
            elif command == "list":
                _list(*args)
            else:
                warehouse = Warehouse()
                name, args = args[0], args[1:]
                box = warehouse.box(name)
                if command == "install":
                    edition, version = args
                    box.install(edition, version)
                    webserver_port = warehouse._ports[name]
                    webserver_https_port = webserver_port + 1
                    print("Created server instance %r configured on ports %s and %s" % (
                        name, webserver_port, webserver_https_port))
                elif command == "remove" and not args:
                    box.remove()
                elif command == "remove" and args[0] == "force":
                    box.remove(force=True)
                elif command == "rename":
                    new_name, = args
                    box.rename(new_name)
                elif command == "start":
                    ps = box.server.start()
                    print(ps.service_root.uri)
                elif command == "stop":
                    box.server.stop()
                elif command == "open":
                    if box.server:
                        box.server.graph.open_browser()
                    else:
                        raise RuntimeError("Server %r is not running" % name)
                elif command == "drop" and not args:
                    box.server.store.drop()
                elif command == "drop" and args[0] == "force":
                    box.server.store.drop(force=True)
                elif command == "load":
                    path, args = args[0], args[1:]
                    if not args:
                        box.server.store.load(path)
                    elif args[0] == "force":
                        box.server.store.load(path, force=True)
                    else:
                        raise ValueError("Bad command or arguments")
                elif command == "save":
                    path, args = args[0], args[1:]
                    if not args:
                        box.server.store.save(path)
                    elif args[0] == "force":
                        box.server.store.save(path, force=True)
                    else:
                        raise ValueError("Bad command or arguments")
                else:
                    raise ValueError("Bad command or arguments")
        else:
            _help(script)
    except Exception as error:
        sys.stderr.write(ustr(error))
        sys.stderr.write("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
