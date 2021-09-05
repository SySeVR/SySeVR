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


import os
from subprocess import check_output
from shutil import rmtree

from py2neo.env import DIST_HOST
from py2neo.packages.httpstream import NetworkAddressError
from py2neo.server import download, dist_archive_name, GraphServer


__all__ = ["Warehouse", "Box"]


class Warehouse(object):
    """ Container for Neo4j :class:`.Box` installations.

    :arg home: Home directory for this warehouse (defaults to the path
               held in ``$NEOBOX_HOME`` if specified, otherwise ``$HOME/.neobox``)

    """

    __instances = {}

    def __new__(cls, home=None):
        if not home:
            home = os.getenv("NEOBOX_HOME") or os.path.expanduser("~/.neobox")
        key = home
        try:
            inst = cls.__instances[key]
        except KeyError:
            inst = super(Warehouse, cls).__new__(cls)
            inst.home = home
            cls.__instances[key] = inst
        return inst

    home = None

    def __repr__(self):
        return "<Warehouse home=%r>" % self.home

    def __hash__(self):
        return hash(self.home)

    def box(self, name):
        """ Fetch a named box. This box may or may not contain a Neo4j
        server installation.

        :arg name: Name of the box to fetch.
        :rtype: :class:`.Box`

        """
        return Box(self, name)

    def boxes(self):
        """ Fetch a list of all installed boxes.

        :rtype: generator

        """
        for name in os.listdir(os.path.join(self.home, "boxes")):
            yield Box(self, name)

    @property
    def _ports_path(self):
        return os.path.join(self.home, "ports")

    def ensure_downloaded(self, edition, version):
        dist_path = os.path.join(self.home, "dist")
        try:
            os.makedirs(dist_path)
        except FileExistsError:
            pass
        filename = os.path.join(dist_path, dist_archive_name(edition, version))
        if os.path.isfile(filename):
            return filename
        try:
            return download(edition, version, dist_path)
        except NetworkAddressError:
            raise RuntimeError("Not able to connect to %s" % DIST_HOST)

    @property
    def _ports(self):
        ports_path = self._ports_path
        try:
            os.makedirs(ports_path)
        except FileExistsError:
            pass
        ports = [port for port in os.listdir(ports_path)]
        return {os.path.basename(os.readlink(os.path.join(ports_path, port))): int(port)
                for port in ports}

    def _assign_port(self, name, port=None):
        if not port:
            ports = self._ports.values()
            if ports:
                port = max(ports) + 2
            else:
                port = 47470
        os.symlink(os.path.join("..", "boxes", name), os.path.join(self._ports_path, str(port)))
        return port

    def _remove_port(self, name):
        try:
            port = self._ports[name]
        except KeyError:
            pass
        else:
            os.remove(os.path.join(self._ports_path, str(port)))


class Box(object):
    """ Named container for a single Neo4j installation.

    :arg warehouse: The warehouse to which this box belongs.
    :arg name: The name of this box.

    """

    __instances = {}

    def __new__(cls, warehouse, name):
        key = (warehouse, name)
        try:
            inst = cls.__instances[key]
        except KeyError:
            inst = super(Box, cls).__new__(cls)
            inst.warehouse = warehouse
            inst.name = name
            cls.__instances[key] = inst
        return inst

    warehouse = None
    name = None

    def __repr__(self):
        return "<Box warehouse=%r name=%r>" % (self.warehouse.home, self.name)

    def __hash__(self):
        return hash(self.warehouse) ^ hash(self.name)

    @property
    def home(self):
        """ Base directory for this box. This directory may not exist.
        """
        return os.path.join(self.warehouse.home, "boxes", self.name)

    @property
    def server(self):
        """ The :class:`py2neo.server.GraphServer` installed in this box or
        :const:`None` if this box is empty.
        """
        if os.path.exists(self.home):
            return GraphServer(os.path.join(self.home, "neo4j"))
        else:
            return None

    def install(self, edition, version):
        """ Install a Neo4j server in this box.

        :arg edition: Neo4j edition (`'community'` or `'enterprise'`)
        :arg version: Neo4j version (e.g. `'2.1.5'`)
        :rtype: :class:`py2neo.server.GraphServer`

        """
        inst_path = self.home
        if self.server is not None:
            raise ValueError("A box named %r already exists" % self.name)
        filename = self.warehouse.ensure_downloaded(edition, version)
        os.makedirs(inst_path)
        # The Python tarfile module doesn't seem to recognise the Neo4j tar format :-(
        check_output("tar -x -C \"%s\" -f \"%s\"" % (inst_path, filename), shell=True)
        os.symlink(os.listdir(inst_path)[0], self.server.home)
        port = self.warehouse._assign_port(self.name)
        server = self.server
        server.update_server_properties(webserver_port=port, webserver_https_port=(port + 1))
        return server

    def remove(self, force=False):
        """ Remove any installed Neo4j server from this box. Running
        servers cannot be removed unless forced.

        :arg force: :const:`True` to remove server even if running.

        """
        if self.server.pid and not force:
            raise RuntimeError("Cannot remove a running server instance")
        self.warehouse._remove_port(self.name)
        rmtree(self.home, ignore_errors=(not force))

    def rename(self, new_name):
        """ Rename this box.

        :arg new_name: The new name for this box.

        """
        inst_path = self.home
        if not os.path.isdir(inst_path):
            raise ValueError("No box named %r exists" % self.name)
        new_box = self.warehouse.box(new_name)
        new_inst_path = new_box.home
        if os.path.isdir(new_inst_path):
            raise ValueError("A server instance named %r already exists" % new_name)
        port = self.warehouse._ports[self.name]
        self.warehouse._remove_port(self.name)
        os.rename(inst_path, new_inst_path)
        self.warehouse._assign_port(new_name, port)
        self.name = new_name
