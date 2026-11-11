import pytest

from codec import CODECS, PAYLOAD_SIZE, decode_bytes, decode_json, encode_bytes
from sensor import HUM_KEY, TEMP_KEY, WIND_DIRECTIONS, WIND_KEY, read_sensors


def _reading(temp, hum, wind):
    return {TEMP_KEY: temp, HUM_KEY: hum, WIND_KEY: wind}


@pytest.mark.parametrize("mode", CODECS)
@pytest.mark.parametrize("wind", WIND_DIRECTIONS)
@pytest.mark.parametrize("temp,hum", [(0.0, 0), (110.0, 100), (56.32, 51), (0.01, 1), (109.99, 99)])
def test_roundtrip_extremos(mode, temp, hum, wind):
    codec = CODECS[mode]
    reading = _reading(temp, hum, wind)
    assert codec.decode(codec.encode(reading)) == reading


@pytest.mark.parametrize("mode", CODECS)
def test_roundtrip_lecturas_simuladas(mode):
    codec = CODECS[mode]
    for _ in range(1000):
        reading = read_sensors()
        assert codec.decode(codec.encode(reading)) == reading


def test_payload_restringido_es_de_3_bytes():
    for _ in range(1000):
        assert len(encode_bytes(read_sensors())) == PAYLOAD_SIZE


@pytest.mark.parametrize("mode", CODECS)
@pytest.mark.parametrize("bad", [
    _reading(110.01, 50, "N"),
    _reading(-0.01, 50, "N"),
    _reading(50.0, 101, "N"),
    _reading(50.0, 50, "NNE"),
    {TEMP_KEY: 50.0, HUM_KEY: 50},
])
def test_encode_rechaza_lecturas_invalidas(mode, bad):
    with pytest.raises(ValueError):
        CODECS[mode].encode(bad)


@pytest.mark.parametrize("payload", [b"", b"ab", b"abcd", CODECS["json"].encode(_reading(1.0, 1, "N"))])
def test_decode_bytes_rechaza_tamano_incorrecto(payload):
    with pytest.raises(ValueError):
        decode_bytes(payload)


def test_decode_bytes_rechaza_valores_fuera_de_rango():
    # todos los bits en 1: temp = 16383 -> 163.83 grados
    with pytest.raises(ValueError):
        decode_bytes(b"\xff\xff\xff")


@pytest.mark.parametrize("payload", [b"\x00\x01\x02", b"123", b"[]", b"no es json"])
def test_decode_json_rechaza_payload_no_valido(payload):
    with pytest.raises(ValueError):
        decode_json(payload)
