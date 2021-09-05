from collections import namedtuple

import pytest

from py2neo.core import Graph
from py2neo.ext.spatial import Spatial


DEFAULT_DB = "http://localhost:7474/db/data/"
DEFAULT_INDEX_NAME = "uk"

Location = namedtuple('location', ['name', 'coords'])


def pytest_report_header(config):
    return "py2neo Spatial spatial run"


def pytest_configure(config):
    db = Graph(DEFAULT_DB)
    rels = next(db.match(), None)
    if rels:
        print(
            'Test Runner will only operate on an empty graph.    '
            'Either clear the DB with `neotool clear` or provide '
            'a differnt DB URI ')

        pytest.exit(1)


def pytest_unconfigure(config):
    """ Final tear-down behaviour of spatial environment
    """
    db = Graph(DEFAULT_DB)
    db.delete_all()


@pytest.fixture
def graph(request):
    graph = Graph(DEFAULT_DB)
    graph.delete_all()
    return graph


@pytest.fixture
def spatial(graph):
    graph.delete_all()
    spatial = Spatial(graph)
    return spatial


@pytest.fixture
def cornwall_wkt(spatial):
    wkt = 'MULTIPOLYGON (((-4.653215 50.93101, -4.551301 50.92998, \
-4.454097 50.93213, -4.457686 50.9153, -4.412353 50.86911, \
-4.429763 50.86168, -4.439549 50.83183, -4.434862 50.81649, \
-4.470567 50.78999, -4.448156 50.78679, -4.434568 50.77381, \
-4.393076 50.77908, -4.377372 50.77292, -4.376274 50.74182, \
-4.358784 50.7198, -4.364254 50.69954, -4.350039 50.6951, \
-4.329549 50.64244, -4.298627 50.63652, -4.301117 50.58395, \
-4.27298 50.58853, -4.256588 50.55062, -4.241137 50.54372, \
-4.229059 50.53212, -4.210176 50.53673, -4.201431 50.53201, \
-4.19751 50.50473, -4.186901 50.51053, -4.179725 50.50811, \
-4.179235 50.49958, -4.200784 50.49068, -4.218941 50.49638, \
-4.212711 50.46859, -4.192195 50.43175, -4.208627 50.3939, \
-4.193646 50.384, -4.188921 50.3624, -4.170176 50.3629, \
-4.168255 50.35779, -4.146631 50.35872, -4.161255 50.3353, \
-4.186274 50.3328, -4.185941 50.31562, -6.539587 49.41615, \
-6.852528 50.0848, -4.653215 50.93101)))'
    return wkt


@pytest.fixture
def devon_wkt(spatial):
    wkt = 'MULTIPOLYGON (((-4.57258 51.21081, -3.709391 51.28549, \
-3.714396 51.17725, -3.826997 51.16611, -3.824625 51.14312, \
-3.714637 51.09008, -3.590172 51.06422, -3.601886 51.01714, \
-3.53522 51.01458, -3.52539 51.03427, -3.485692 51.0438, \
-3.418414 51.0406, -3.373674 51.02581, -3.371135 50.98824, \
-3.330665 50.99251, -3.251704 50.95208, -3.161643 50.95646, \
-3.167259 50.91705, -3.145023 50.90165, -3.048254 50.91769, \
-3.023396 50.86521, -2.970158 50.86526, -2.945143 50.82505, \
-2.882086 50.80924, -2.881604 50.7839, -2.938419 50.76735, \
-2.925018 50.75306, -2.899942 50.54885, -3.309185 50.4384, \
-3.66197 50.11104, -4.23405 50.23057, -4.135132 50.35044, \
-4.088939 50.35211, -4.045379 50.38772, -4.074844 50.39201, \
-4.118101 50.42869, -4.187803 50.41428, -4.217159 50.45355, \
-4.245246 50.453, -4.220124 50.52137, -4.27798 50.52921, \
-4.272792 50.5507, -4.316531 50.57323, -4.315263 50.62605, \
-4.341798 50.63572, -4.382257 50.73126, -4.462788 50.78225, \
-4.451816 50.84964, -4.431014 50.86446, -4.472728 50.92142, \
-4.752335 50.93162, -4.57258 51.21081)))'
    return wkt


@pytest.fixture
def cornwall(spatial, cornwall_wkt):
    spatial.create_layer(DEFAULT_INDEX_NAME)
    spatial.create_geometry(
        geometry_name="cornwall", wkt_string=cornwall_wkt,
        layer_name=DEFAULT_INDEX_NAME
    )


@pytest.fixture
def devon(spatial, devon_wkt):
    spatial.create_layer(DEFAULT_INDEX_NAME)
    spatial.create_geometry(
        geometry_name="devon", wkt_string=devon_wkt,
        layer_name=DEFAULT_INDEX_NAME
    )


@pytest.fixture
def cornish_towns():
    falmouth = Location('falmouth', (50.152571, -5.06627))
    bodmin = Location('bodmin', (50.468630, -4.715114))
    penzance = Location('penzance', (50.118798, -5.537592))
    truro = Location('truro', (50.263195, -5.051041))
    locations = [falmouth, bodmin, penzance, truro]
    return locations


@pytest.fixture
def devonshire_towns():
    plymouth = Location('plymouth', (50.375456, -4.142656))
    exeter = Location('exeter', (50.718412, -3.533899))
    torquay = Location('torquay', (50.461921, -3.525315))
    tiverton = Location('tiverton', (50.902049, -3.491207))
    axminster = Location('axminster', (50.782727, -2.994937))
    locations = [plymouth, exeter, torquay, tiverton, axminster]
    return locations


@pytest.fixture
def english_towns():
    bristol = Location('bristol', (51.454513, -2.58791))
    manchester = Location('manchester', (53.479324, -2.248485))
    oxford = Location('oxford', (51.752021, -1.257726))
    newcastle = Location('newcastle', (54.978252, -1.61778))
    norwich = Location('norwich', (52.630886, 1.297355))
    locations = [bristol, manchester, oxford, newcastle, norwich]
    return locations


@pytest.fixture
def scottish_towns():
    aberdeen = Location('aberdeen', (57.149717, -2.094278))
    edinburgh = Location('edinburgh', (55.953252, -3.188267))
    locations = [aberdeen, edinburgh]
    return locations


@pytest.fixture
def towns(english_towns, scottish_towns):
    return english_towns + scottish_towns


@pytest.fixture
def london_features():
    big_ben = Location('big_ben', (51.500728, -0.124626))
    buckingham_palace = Location('buckingham_palace', (51.501364, -0.14189))
    hampton_court = Location('hampton_court', (51.403613, -0.337762))
    st_pauls = Location('st_pauls', (51.513845, -0.098351))

    features = [
        big_ben, buckingham_palace, hampton_court, st_pauls
    ]

    return features


@pytest.fixture
def uk_features():
    blackpool_tower = Location('blackpool_tower', (53.814620, -3.05586))
    lake_windermere = Location('lake_windermere', (54.369274, -2.912605))
    brighton_pier = Location('brighton_pier', (50.815218, -0.137026))
    cheddar_gorge = Location('cheddar_gorge', (51.286389, -2.760278))
    stonehenge = Location('stonehenge', (51.178882, -1.826215))
    windsor_castle = Location('windsor_castle', (51.483894, -0.604403))
    ben_nevis = Location('ben_nevis', (56.796854, -5.003541))

    features = [
        blackpool_tower, lake_windermere, brighton_pier, cheddar_gorge,
        stonehenge, ben_nevis, windsor_castle
    ]

    return features


@pytest.fixture
def hard_lat_long():
    # this lat-long rounds to oblivion when parsed by Shapely
    st_pauls = Location('st_pauls', (51.513845, -0.098351))
    return st_pauls
