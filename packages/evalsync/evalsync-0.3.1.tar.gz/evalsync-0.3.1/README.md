# EvalSync

## Development

### Generate Protobuf Proto

```py
protoc --proto_path=../proto --python_out=src/evalsync/proto ../proto/sync.proto
```

### Submit to PyPI

```py
rye publish
```
