import pytest

from . import TestBase
from py2neo.ext.spatial.exceptions import LayerNotFoundError, InvalidWKTError


LAYER_NAME = "geometry_layer"


class TestLayers(TestBase):
    def test_create_layer(self, spatial):
        spatial.create_layer(LAYER_NAME)
        assert self._layer_exists(spatial.graph, LAYER_NAME)

    def test_layer_uniqueness(self, spatial):
        graph = spatial.graph

        def count(layer_name):
            count = 0
            results = graph.cypher.execute(
                "MATCH (r { name:'spatial_root' }), (r)-[:LAYER]->(n) \
RETURN n")

            for record in results:
                node = record[0]
                if node.properties['layer'] == layer_name:
                    count += 1
            return count

        assert count(LAYER_NAME) == 0

        spatial.create_layer(LAYER_NAME)
        assert count(LAYER_NAME) == 1

        spatial.create_layer(LAYER_NAME)
        assert count(LAYER_NAME) == 1

    def test_cannot_create_geometry_if_layer_does_not_exist(self, spatial):
        with pytest.raises(LayerNotFoundError):
            spatial.create_geometry(
                geometry_name="spatial", wkt_string='POINT (1,1)',
                layer_name="missing")

    def test_handle_bad_wkt(self, spatial):
        geometry_name = "shape"
        bad_geometry = 'isle of wight'

        spatial.create_layer(LAYER_NAME)

        with pytest.raises(InvalidWKTError):
            spatial.create_geometry(
                geometry_name=geometry_name, wkt_string=bad_geometry,
                layer_name=LAYER_NAME)

    def test_get_layer(self, spatial):
        spatial.create_layer("this")
        assert self._layer_exists(spatial.graph, "this")
        assert spatial.get_layer("this")

    def test_delete_layer(self, spatial, cornwall_wkt, devon_wkt):
        graph = spatial.graph
        spatial.create_layer("mylayer")
        spatial.create_geometry(
            geometry_name="shape_a", wkt_string=cornwall_wkt,
            layer_name="mylayer")
        spatial.create_geometry(
            geometry_name="shape_b", wkt_string=devon_wkt,
            layer_name="mylayer")

        assert self._geometry_exists(graph, "shape_a", "mylayer")
        assert self._geometry_exists(graph, "shape_b", "mylayer")

        spatial.delete_layer("mylayer")

        assert not self._geometry_exists(graph, "shape_a", "mylayer")
        assert not self._geometry_exists(graph, "shape_b", "mylayer")

        assert not self._layer_exists(graph, "mylayer")
