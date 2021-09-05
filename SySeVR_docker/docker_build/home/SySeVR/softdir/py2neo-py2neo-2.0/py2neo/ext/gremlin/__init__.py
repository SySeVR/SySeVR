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


from py2neo import ServerPlugin


__all__ = ["Gremlin"]


class Gremlin(ServerPlugin):
    """ Extension for Gremlin script execution. This requires the
    Gremlin server plugin.
    """

    def __init__(self, graph):
        super(Gremlin, self).__init__(graph, "GremlinPlugin")

    def execute(self, script):
        """ Execute a Gremlin script.
        """
        response = self.resources["execute_script"].post({"script": script})
        return self.graph.hydrate(response.content)
