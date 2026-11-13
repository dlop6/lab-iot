"""codificacion de lecturas: json normal o payload restringido a 3 bytes."""
import json
from typing import Callable, NamedTuple

from sensor import HUM_KEY, HUM_RANGE, TEMP_KEY, TEMP_RANGE, WIND_DIRECTIONS, WIND_KEY

# layout de 24 bits: [temp*100: 14][humedad: 7][viento: 3]
PAYLOAD_SIZE = 3
TEMP_SCALE = 100
HUM_BITS = 7
WIND_BITS = 3


def _validate(reading: dict) -> dict:
    try:
        valid = (
            TEMP_RANGE[0] <= reading[TEMP_KEY] <= TEMP_RANGE[1]
            and HUM_RANGE[0] <= reading[HUM_KEY] <= HUM_RANGE[1]
            and reading[WIND_KEY] in WIND_DIRECTIONS
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"lectura incompleta: {reading!r}") from exc
    if not valid:
        raise ValueError(f"lectura fuera de rango: {reading!r}")
    return reading


def encode_json(reading: dict) -> bytes:
    return json.dumps(_validate(reading)).encode("utf-8")


def decode_json(payload: bytes) -> dict:
    # json.JSONDecodeError y UnicodeDecodeError ya son ValueError
    return _validate(json.loads(payload.decode("utf-8")))


def encode_bytes(reading: dict) -> bytes:
    _validate(reading)
    temp = round(reading[TEMP_KEY] * TEMP_SCALE)
    wind = WIND_DIRECTIONS.index(reading[WIND_KEY])
    packed = (temp << (HUM_BITS + WIND_BITS)) | (reading[HUM_KEY] << WIND_BITS) | wind
    return packed.to_bytes(PAYLOAD_SIZE, "big")


def decode_bytes(payload: bytes) -> dict:
    if len(payload) != PAYLOAD_SIZE:
        raise ValueError(f"payload de {len(payload)} bytes, se esperaban {PAYLOAD_SIZE}")
    packed = int.from_bytes(payload, "big")
    return _validate({
        TEMP_KEY: (packed >> (HUM_BITS + WIND_BITS)) / TEMP_SCALE,
        HUM_KEY: (packed >> WIND_BITS) & ((1 << HUM_BITS) - 1),
        WIND_KEY: WIND_DIRECTIONS[packed & ((1 << WIND_BITS) - 1)],
    })


class Codec(NamedTuple):
    encode: Callable[[dict], bytes]
    decode: Callable[[bytes], dict]


CODECS = {
    "json": Codec(encode_json, decode_json),
    "bytes": Codec(encode_bytes, decode_bytes),
}
