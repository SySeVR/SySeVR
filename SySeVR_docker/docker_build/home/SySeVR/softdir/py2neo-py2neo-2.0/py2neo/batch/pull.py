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


from py2neo.core import Node, Path, Rel
from py2neo.batch.core import Batch, Job, Target


__all__ = ["PullPropertiesJob", "PullNodeLabelsJob", "PullRelationshipJob", "PullBatch"]


class PullPropertiesJob(Job):

    raw_result = True

    def __init__(self, entity):
        Job.__init__(self, "GET", Target(entity, "properties"))


class PullNodeLabelsJob(Job):

    raw_result = True

    def __init__(self, node):
        Job.__init__(self, "GET", Target(node, "labels"))


class PullRelationshipJob(Job):

    raw_result = True

    def __init__(self, relationship):
        Job.__init__(self, "GET", Target(relationship))


class PullBatch(Batch):
    """ A batch of pull jobs.
    """

    def __init__(self, graph):
        Batch.__init__(self, graph)

    def append(self, entity):
        """ Append an entity to the list to be pulled.

        :param entity: An entity such as a :class:`py2neo.Node`.

        """
        if isinstance(entity, Node):
            self.jobs.append(PullPropertiesJob(entity))
            if entity.graph.supports_node_labels:
                self.jobs.append(PullNodeLabelsJob(entity))
        elif isinstance(entity, Rel):
            self.jobs.append(PullRelationshipJob(entity))
        elif isinstance(entity, Path):
            for relationship in entity.relationships:
                self.jobs.append(PullRelationshipJob(relationship))
        else:
            raise TypeError("Cannot pull object of type %s" % entity.__class__.__name__)

    def pull(self):
        """ Pull details to all entities in this batch from their
        remote counterparts.
        """
        for i, result in enumerate(self.graph.batch.submit(self)):
            job = self.jobs[i]
            entity = job.target.entity
            if isinstance(job, PullPropertiesJob):
                entity.properties.replace(result.content)
            elif isinstance(job, PullNodeLabelsJob):
                entity.labels.replace(result.content)
            elif isinstance(job, PullRelationshipJob):
                entity.__class__.hydrate(result.content, entity)
