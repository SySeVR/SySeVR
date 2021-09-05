from py2neo.ext.spatial.util import parse_lat_long
from py2neo.ext.spatial.plugin import NAME_PROPERTY


class TestBase(object):
    @staticmethod
    def _layer_exists(graph, layer_name):
        results = graph.cypher.execute(
            "MATCH (r { name:'spatial_root' }), (r)-[:LAYER]->(n) RETURN n")

        for record in results:
            node = record[0]
            if node.properties['layer'] == layer_name:
                return True
        return False

    @staticmethod
    def _geometry_exists(graph, geometry_name, layer_name):
        # assert a geometry exists in the *application* graph
        resp = graph.find(
            label=layer_name, property_key=NAME_PROPERTY,
            property_value=geometry_name)
        results = [r for r in resp]

        return len(results) == 1

    @staticmethod
    def load(api, data, layer):
        api.create_layer(layer)
        for location in data:
            shape = parse_lat_long(location.coords)
            api.create_geometry(location.name, shape.wkt, layer)

    @staticmethod
    def get_geometry_node(api, geometry_name):
        query = """MATCH (application_node {_py2neo_geometry_name:\
{geometry_name}}),
(application_node)<-[:LOCATES]-(geometry_node)
RETURN geometry_node"""
        params = {
            'geometry_name': geometry_name,
        }

        result = api.graph.cypher.execute(query, params)
        record = result[0]
        geometry_node = record[0]
        return geometry_node

    @staticmethod
    def get_application_node(api, geometry_name):
        query = """MATCH (application_node {_py2neo_geometry_name:\
{geometry_name}}) RETURN application_node"""
        params = {
            'geometry_name': geometry_name,
        }

        result = api.graph.cypher.execute(query, params)
        record = result[0]
        application_node = record[0]
        return application_node
