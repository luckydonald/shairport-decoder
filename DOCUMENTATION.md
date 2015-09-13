

## ```shairportdecoder```
#### Class ```Processor```
Allows you to process shairport-sync's metadata pipe.
Will give you an ```shairportdecoder.decode.Info``` object.

##```shairportdecoder.remote```
#### Class AirplayRemote
Allows you to send play pause and other commands to the streaming client.
```python
example = AirplayRemote.from_token(token="1595DA80A46BF32B")
example.volume_down()
```