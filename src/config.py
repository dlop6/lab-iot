"""config compartida de kafka y cli. el password solo se lee del entorno."""
import argparse
import os

from codec import CODECS

TOPIC = os.getenv("KAFKA_TOPIC", "23747")
SENSOR_KEY = "sensor1"


def kafka_config() -> dict:
    password = os.getenv("KAFKA_PASSWORD")
    if not password:
        raise SystemExit("falta la variable de entorno KAFKA_PASSWORD")
    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "161.35.11.141:9092"),
        "security.protocol": "SASL_PLAINTEXT",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": os.getenv("KAFKA_USERNAME", "estudiante"),
        "sasl.password": password,
    }


def parse_mode(description: str) -> str:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--mode", choices=CODECS, default="json",
                        help="json (fases 3.2/3.3) o bytes (fase 3.4, payload de 3 bytes)")
    return parser.parse_args().mode
