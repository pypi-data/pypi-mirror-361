
# Robot Avro Serializer

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![Robot Framework](https://img.shields.io/badge/robot--framework-compatible-brightgreen.svg)](https://robotframework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Robot Avro Serializer** is a custom [Robot Framework](https://robotframework.org/) library written in Python to serialize JSON messages into binary Avro format using user-defined schemas.

---

## Features

- ✅ Load Avro schema from `.avsc` files
- 🔄 Serialize JSON objects into Avro binary
- 📦 Return binary as hexadecimal string
- 🤖 Seamless integration with Robot Framework

---

## Installation

```bash
pip install robotframework AvroSerializer
```

---

## Usage Example

**Robot Test:**

```robot
*** Settings ***
Library    AvroSerializer

*** Variables ***
${SCHEMA_FILE}    example_schema.avsc
${JSON_MSG}       {"name": "Ana", "age": 30, "email": "ana@email.com"}

*** Test Cases ***
Serialize JSON To Avro
    Load Avro Schema From File    ${SCHEMA_FILE}
    ${hex}=    Serialize And Return Hex    ${JSON_MSG}
    Log    Serialized Avro Hex: ${hex}
```

**example_schema.avsc**

```json
{
  "type": "record",
  "name": "User",
  "fields": [
    { "name": "name", "type": "string" },
    { "name": "age", "type": "int" },
    { "name": "email", "type": ["null", "string"], "default": null }
  ]
}
```

---

## Development

```bash
git clone https://github.com/darioajr/AvroSerializer.git
cd AvroSerializer
pip install .
```

---

## License

This project is licensed under the Apache-2.0 License.
