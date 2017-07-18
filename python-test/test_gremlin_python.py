"""
Talking to JanusGraph from Python.
http://tinkerpop.apache.org/docs/current/reference/#gremlin-python
"""

from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

vertices = g.V().toList()
print(vertices)
