# JanusGraph: Lessons learned

Docker deployment of [JanusGraph](http://janusgraph.org/). To run,

```
docker-compose up --build
```

Note that a version of [Docker Compose](https://github.com/docker/compose) with support for version `3` schemas is required, e.g. `1.15.0`.

Afterwards, you can connect to the local Gremlin shell using

```
docker exec -it janusgraph_janus_1 ./bin/gremlin.sh
```

The `python-test` subdirectories contains some simplistic Python scripts to test communication with JanusGraph.

Sources for the `Dockerfile` and their surroundings were basically taken straight from Titan setups:

* [efaurie/docker-titan-cassandra](https://github.com/efaurie/docker-titan-cassandra)
* [elubow/titan-gremlin](https://github.com/elubow/titan-gremlin)

For multiple graphs in Titan (and likely also JanusGraph), follow these links:

* [How many graphs can i create in one Titan DB?](https://stackoverflow.com/a/40545537/195651)
* [Serving multiple Titan graphs over Gremlin Server (TinkerPop 3)](https://medium.com/@jbmusso/serving-multiple-titan-graphs-over-gremlin-server-tinkerpop-3-d3c971d07964)
* [One graph in one Titan instance](https://jaceklaskowski.gitbooks.io/titan-scala/content/one_graph_in_one_titan_instance.html)

## Cassandra and Elasticsearch

As per [compatibility matrix](http://docs.janusgraph.org/latest/version-compat.html), the supported Cassandra version is 2.1 and the supported Elasticsearch version is 1.5.

## Shell

In the Gremin REPL examples like this one:

```
$  bin/gremlin.sh
         \,,,/
         (o o)
-----oOOo-(3)-oOOo-----
plugin activated: tinkerpop.server
plugin activated: tinkerpop.hadoop
plugin activated: tinkerpop.utilities
plugin activated: aurelius.titan
plugin activated: tinkerpop.tinkergraph
gremlin> :remote connect tinkerpop.server conf/remote.yaml
==>Connected - localhost/127.0.0.1:8182
gremlin> :> graph.addVertex("name", "stephen")
==>v[256]
gremlin> :> g.V().values('name')
==>stephen
```

The token `:>` is not part of the _shell_, but an actual _command_. It is required to run the command on the remote server.

That makes the commands:

```
:remote connect tinkerpop.server conf/remote.yaml
:> graph.addVertex("name", "stephen")
:> g.V().values('name')
```

Entering invalid commands in the shell results in an exception on the server.

The `g` mapping (available at the server) is registered in `scripts/empty-sample.groovy`.

## Channelizers

You [have to choose the Channelizer](http://docs.janusgraph.org/latest/server.html#_websocket_versus_rest) to work with, either `HttpChannelizer` or `WebSocketChannelizer`.

Using the `HttpChannelizer` 

```
channelizer: org.apache.tinkerpop.gremlin.server.channel.HttpChannelizer
```

allows for HTTP access to JanusGraph using e.g.

```bash
curl "http://localhost:8182/?gremlin=100-1"
```

However, this seems to prevent the Gremlin REPL shell from talking to the server:

```
Jul 17, 2017 10:52:00 PM java.util.prefs.FileSystemPreferences$1 run
INFO: Created user preferences directory.

         \,,,/
         (o o)
-----oOOo-(3)-oOOo-----
plugin activated: aurelius.titan
plugin activated: tinkerpop.server
plugin activated: tinkerpop.utilities
plugin activated: tinkerpop.hadoop
plugin activated: tinkerpop.tinkergraph
gremlin> :remote connect tinkerpop.server conf/remote.yaml
22:52:14 WARN  org.apache.tinkerpop.gremlin.driver.handler.WebSocketClientHandler  - Exception caught during WebSocket processing - closing connection
io.netty.handler.codec.http.websocketx.WebSocketHandshakeException: Invalid handshake response getStatus: 400 Bad Request
	at io.netty.handler.codec.http.websocketx.WebSocketClientHandshaker13.verify(WebSocketClientHandshaker13.java:182)
	at io.netty.handler.codec.http.websocketx.WebSocketClientHandshaker.finishHandshake(WebSocketClientHandshaker.java:202)
	at org.apache.tinkerpop.gremlin.driver.handler.WebSocketClientHandler.channelRead0(WebSocketClientHandler.java:73)
	at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:105)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:103)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
	at io.netty.handler.codec.ByteToMessageDecoder.channelInactive(ByteToMessageDecoder.java:241)
	at io.netty.handler.codec.http.HttpClientCodec$Decoder.channelInactive(HttpClientCodec.java:212)
	at io.netty.channel.CombinedChannelDuplexHandler.channelInactive(CombinedChannelDuplexHandler.java:132)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelInactive(AbstractChannelHandlerContext.java:208)
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelInactive(AbstractChannelHandlerContext.java:194)
	at io.netty.channel.DefaultChannelPipeline.fireChannelInactive(DefaultChannelPipeline.java:828)
	at io.netty.channel.AbstractChannel$AbstractUnsafe$5.run(AbstractChannel.java:576)
	at io.netty.util.concurrent.SingleThreadEventExecutor.runAllTasks(SingleThreadEventExecutor.java:380)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:357)
	at io.netty.util.concurrent.SingleThreadEventExecutor$2.run(SingleThreadEventExecutor.java:116)
	at java.lang.Thread.run(Thread.java:748)
22:52:14 ERROR org.apache.tinkerpop.gremlin.driver.Handler$GremlinResponseHandler  - Could not process the response - correct the problem and restart the driver.

```

The REPL shell does seem to work with the `WebSocketChannelizer` though:

```
channelizer: org.apache.tinkerpop.gremlin.server.channel.WebSocketChannelizer
```

## Serializers

The exception `Gremlin Server is not configured with a serializer for the requested mime type [application/vnd.gremlin-v2.0+json] - using org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerV1d0 by default` occurs when the `GraphSONMessageSerializerGremlinV2d0` was not added to the serializers list of serializers.

Running with the configuration of

```
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GryoMessageSerializerV1d0, config: { useMapperFromGraph: graph }}
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GryoMessageSerializerV1d0, config: { serializeResultToString: true }}
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerGremlinV1d0, config: { useMapperFromGraph: graph }}
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerGremlinV2d0, config: { useMapperFromGraph: graph }}
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerV1d0, config: { useMapperFromGraph: graph }}
  - { className: org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerV2d0, config: { useMapperFromGraph: graph }}
```

results in these startup outputs:

```
janus_1  | 40470 [main] INFO  org.apache.tinkerpop.gremlin.server.AbstractChannelizer  - Configured application/vnd.gremlin-v1.0+gryo with org.apache.tinkerpop.gremlin.driver.ser.GryoMessageSerializerV1d0
janus_1  | 40470 [main] INFO  org.apache.tinkerpop.gremlin.server.AbstractChannelizer  - Configured application/vnd.gremlin-v1.0+gryo-stringd with org.apache.tinkerpop.gremlin.driver.ser.GryoMessageSerializerV1d0
janus_1  | 40476 [main] INFO  org.apache.tinkerpop.gremlin.server.AbstractChannelizer  - Configured application/vnd.gremlin-v1.0+json with org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerGremlinV1d0
janus_1  | 40496 [main] INFO  org.apache.tinkerpop.gremlin.server.AbstractChannelizer  - Configured application/vnd.gremlin-v2.0+json with org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerGremlinV2d0
janus_1  | 40497 [main] INFO  org.apache.tinkerpop.gremlin.server.AbstractChannelizer  - Configured application/json with org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerV1d0
```

Here's the full exception rendering:

```
janus_1  | 1481034 [gremlin-server-worker-1] WARN  org.apache.tinkerpop.gremlin.server.handler.WsGremlinBinaryRequestDecoder  - Gremlin Server is not configured with a serializer for the requested mime type [application/vnd.gremlin-v2.0+json] - using org.apache.tinkerpop.gremlin.driver.ser.GraphSONMessageSerializerV1d0 by default
janus_1  | 1481034 [gremlin-server-worker-1] WARN  org.apache.tinkerpop.gremlin.driver.ser.AbstractGraphSONMessageSerializerV1d0  - Request [PooledUnsafeDirectByteBuf(ridx: 226, widx: 226, cap: 260)] could not be deserialized by org.apache.tinkerpop.gremlin.driver.ser.AbstractGraphSONMessageSerializerV1d0.
janus_1  | 1481034 [gremlin-server-worker-1] WARN  org.apache.tinkerpop.gremlin.server.handler.OpSelectorHandler  - Invalid OpProcessor requested [null]
janus_1  | org.apache.tinkerpop.gremlin.server.op.OpProcessorException: Invalid OpProcessor requested [null]
janus_1  | 	at org.apache.tinkerpop.gremlin.server.handler.OpSelectorHandler.decode(OpSelectorHandler.java:93)
janus_1  | 	at org.apache.tinkerpop.gremlin.server.handler.OpSelectorHandler.decode(OpSelectorHandler.java:50)
janus_1  | 	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:89)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:103)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:103)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:103)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:103)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.http.websocketx.WebSocketServerProtocolHandler$1.channelRead(WebSocketServerProtocolHandler.java:146)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:244)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:308)
janus_1  | 	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:294)
janus_1  | 	at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:846)
janus_1  | 	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:131)
janus_1  | 	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:511)
janus_1  | 	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:468)
janus_1  | 	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:382)
janus_1  | 	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:354)
janus_1  | 	at io.netty.util.concurrent.SingleThreadEventExecutor$2.run(SingleThreadEventExecutor.java:111)
janus_1  | 	at java.lang.Thread.run(Thread.java:748)
```


