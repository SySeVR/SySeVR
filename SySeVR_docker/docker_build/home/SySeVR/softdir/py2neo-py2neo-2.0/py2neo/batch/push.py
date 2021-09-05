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


from py2neo.core import LabelSet, Node, Path, PropertySet, Rel
from py2neo.batch.core import Batch, Job, Target


__all__ = ["PushPropertyJob", "PushPropertiesJob", "PushNodeLabelsJob", "PushBatch"]


class PushPropertyJob(Job):

    def __init__(self, entity, key, value):
        Job.__init__(self, "PUT", Target(entity, "properties", key), value)


class PushPropertiesJob(Job):

    def __init__(self, entity, properties):
        Job.__init__(self, "PUT", Target(entity, "properties"), PropertySet(properties))


class PushNodeLabelsJob(Job):

    def __init__(self, node, labels):
        Job.__init__(self, "PUT", Target(node, "labels"), list(LabelSet(labels)))


class PushBatch(Batch):
    """ A batch of push jobs.
    """

    def __init__(self, graph):
        Batch.__init__(self, graph)

    def append(self, entity):
        """ Append an entity to the list to be pushed.

        :param entity: An entity such as a :class:`py2neo.Node`.

        """
        if isinstance(entity, Node):
            self.jobs.append(PushPropertiesJob(entity, entity.properties))
            if entity.graph.supports_node_labels:
                self.jobs.append(PushNodeLabelsJob(entity, entity.labels))
        elif isinstance(entity, Rel):
            self.jobs.append(PushPropertiesJob(entity, entity.properties))
        elif isinstance(entity, Path):
            for relationship in entity.relationships:
                self.jobs.append(PushPropertiesJob(relationship, relationship.properties))
        else:
            raise TypeError("Cannot pull object of type %s" % entity.__class__.__name__)

    def push(self):
        """ Push details from all entities in this batch to their
        remote counterparts.
        """
        self.graph.batch.run(self)
