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

"""
.. note::
   This module has been designed to work on Linux and may not operate
   correctly - or at all - on other platforms.

The ``store`` module provides a class for working with a Neo4j data store, typically contained
within the ``data/graph.db`` directory.
"""


import os
from shutil import copytree, rmtree


__all__ = ["GraphStore"]


class GraphStore(object):
    """ A physical database store on disk.
    """

    #: The full file path of this store.
    path = None

    @classmethod
    def for_server(cls, server):
        """ Return the store object for the given server.

        :arg server: A :class:`py2neo.server.GraphServer` object.
        :rtype: :class:`.GraphStore`

        """
        database_location = server.conf.get("neo4j-server", "org.neo4j.server.database.location")
        return GraphStore(os.path.join(server.home, database_location))

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "<GraphStore path=%r>" % self.path

    @property
    def locked(self):
        """ Returns :const:`True` if store is currently in use,
        :const:`False` otherwise.
        """
        return os.path.isfile(os.path.join(self.path, "lock"))

    def drop(self, force=False):
        """ Delete this store directory.

        :param force:

        """
        if force or not self.locked:
            rmtree(self.path, ignore_errors=force)
        else:
            raise RuntimeError("Refusing to drop database store while in use")

    def load(self, path, force=False):
        if force or not self.locked:
            if not os.path.isdir(path):
                raise ValueError("Load source %r is not a directory" % path)
            rmtree(self.path, ignore_errors=force)
            copytree(path, self.path)
        else:
            raise RuntimeError("Refusing to load database store while in use")

    def save(self, path, force=False):
        if force or not self.locked:
            copytree(self.path, path)
        else:
            raise RuntimeError("Refusing to save database store while in use")
