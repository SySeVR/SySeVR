from __future__ import print_function

import sys
sys.path.insert(1, '../py2neo/')

import argparse
import os

from py2neo.core import Graph
from py2neo.ext.spatial import Spatial
    

NEO_URL = "http://localhost:{port}/db/data/"
DEFAULT_DB = NEO_URL.format(port=7474)
DATA_HOME = 'examples/data'


parser = argparse.ArgumentParser(
    description='Load the example data into map layers')

parser.add_argument(
    'data', type=str, help='the name of the data file to load')


parser.add_argument(
    '--layer', dest='layer_name', action='store',
    help="""The layer to add the data to. 
    This will be created if it does not already exist.""")

parser.add_argument(
    '--port', dest='port_address', action='store',
    help='The port Neo is running on')


def load(server_url, geometry_name, wkt_string, layer_name):
    graph = Graph(server_url)
    spatial = Spatial(graph)
    spatial.create_layer(layer_name)
    spatial.create_geometry(geometry_name, wkt_string, layer_name)
    print('done')


if __name__ == '__main__':
    args = parser.parse_args()

    data_file = args.data
    if data_file.endswith('wkt'):
        print('Just provide the name of the file - extension not required')

    geometry_name = data_file
    data_file += '.wkt'
    layer_name = args.layer_name
    neo_port = args.port_address

    server_url = NEO_URL.format(port=neo_port) if neo_port else DEFAULT_DB

    working_directory = os.path.dirname(os.path.realpath(__file__))
    ext_root = working_directory.strip('scripts')
    data_uri = os.path.join(ext_root, DATA_HOME, data_file)

    with open(data_uri, 'r') as fh:
        wkt_string = fh.read()

    load(
        server_url=server_url, geometry_name=geometry_name,
        wkt_string=wkt_string, layer_name=layer_name
    )
