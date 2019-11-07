"""
Talking to JanusGraph from Python.
http://tinkerpop.apache.org/docs/current/reference/#gremlin-python
"""

from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import *


TRAVERSAL_SOURCE = 'g'

graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', TRAVERSAL_SOURCE))

path = g.V().has('code', 'HNL')\
            .repeat(out().simplePath())\
            .until(has('code', 'HOU'))\
            .path()\
            .by(valueMap('code', 'city'))\
            .limit(1)\
            .toList()

for i, vertex in enumerate(path[0]):
    code = vertex["code"][0]
    city = vertex["city"][0]
    print(f'Hop {i+1}: {code} - {city}')

