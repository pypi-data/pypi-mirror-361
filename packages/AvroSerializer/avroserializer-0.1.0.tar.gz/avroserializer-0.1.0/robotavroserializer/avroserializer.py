# robot_avro_serializer/avroserializer.py
from robot.api.deco import keyword, library
import avro.schema
import avro.io
import io
import json

@library
class AvroSerializer:
    def __init__(self, schema=None):
        self.schema = schema

    @keyword("Load Avro Schema From File")
    def load_avro_schema_from_file(self, schema_path):
        """Carrega o schema Avro de um arquivo .avsc"""
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = avro.schema.parse(f.read())

    @keyword("Serialize Avro Message")
    def serialize_avro_message(self, message_json: str) -> bytes:
        """Serializa uma mensagem JSON para Avro binário"""
        if not self.schema:
            raise ValueError("Schema Avro não carregado.")

        message_dict = json.loads(message_json)
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(message_dict, encoder)
        return bytes_writer.getvalue()

    @keyword("Serialize And Return Hex")
    def serialize_and_return_hex(self, message_json: str) -> str:
        """Serializa a mensagem e retorna como string hexadecimal"""
        binary_data = self.serialize_avro_message(message_json)
        return binary_data.hex()
