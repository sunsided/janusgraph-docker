#!/usr/bin/env python3
"""
Talking to JanusGraph from Python.
http://tinkerpop.apache.org/docs/current/reference/#gremlin-python
"""

from gremlin_python.driver.client import Client
from gremlin_python.driver.request import RequestMessage
from gremlin_python.driver.serializer import GraphSONMessageSerializer


TRAVERSAL_SOURCE = 'g'


serializer = GraphSONMessageSerializer()
# workaround to avoid exception on any opProcessor other than `standard` or `traversal`:
serializer.cypher = serializer.standard

client = Client('ws://localhost:8182/gremlin', TRAVERSAL_SOURCE, message_serializer=serializer)

cypherQuery = "MATCH (n:airport) RETURN n.desc"
message = RequestMessage('cypher', 'eval', {'gremlin': cypherQuery})
results = client.submit(message).all().result()

print(results)
