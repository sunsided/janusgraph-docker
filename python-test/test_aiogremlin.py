"""
Talking to JanusGraph from Python.
https://github.com/davebshow/aiogremlin
"""

import asyncio
from aiogremlin import DriverRemoteConnection, Graph


loop = asyncio.get_event_loop()

async def go(loop):
    remote_connection = await DriverRemoteConnection.open('ws://localhost:8182/gremlin', 'g')
    g = Graph().traversal().withRemote(remote_connection)
    vertices = await g.V().toList()
    await remote_connection.close()
    return vertices

vertices = loop.run_until_complete(go(loop))
print(vertices)
