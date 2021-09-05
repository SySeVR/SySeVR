#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014, Simon Harrison
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


from shapely.geometry import MultiPolygon, Point


def parse_lat_long(coords):
    # WKT standard is: POINT (x y)
    # WSG 84: http://spatialreference.org/ref/epsg/4326/
    lat, lon = coords
    point = Point(float(lat), float(lon))
    return point


def parse_poly(lines):
    """ Parse an Osmosis/Google polygon filter file.

    :Params:
        lines : open file pointer

    :Returns:
        shapely.geometry.MultiPolygon object.

    .. note::
        http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

    """
    in_ring = False
    coords = []

    for index, line in enumerate(lines):
        if index == 0:
            # ignore meta/garbage.
            continue
        elif index == 1:
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True
        elif in_ring and line.strip() == 'END':
            in_ring = False
        elif in_ring:
            ring.append(map(float, line.split()))
        elif not in_ring and line.strip() == 'END':
            break
        elif not in_ring and line.startswith('!'):
            coords[-1][1].append([])
            ring = coords[-1][1][-1]
            in_ring = True
        elif not in_ring:
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True

    return MultiPolygon(coords)
