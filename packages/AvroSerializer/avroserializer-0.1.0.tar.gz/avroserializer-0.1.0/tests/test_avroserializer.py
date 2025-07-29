import pytest
import json
import avro.schema
from robotavroserializer.avroserializer import AvroSerializer

@pytest.fixture
def sample_schema(tmp_path):
    schema = {
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": "int"}
        ]
    }
    # Salva o schema em um arquivo temporário
    schema_path = tmp_path / "user.avsc"
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f)
    return str(schema_path)

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}

def test_avro_serializer_roundtrip(sample_schema, sample_data):
    serializer = AvroSerializer()
    serializer.load_avro_schema_from_file(sample_schema)
    avro_bytes = serializer.serialize_avro_message(json.dumps(sample_data))
    assert avro_bytes is not None
    assert isinstance(avro_bytes, bytes)