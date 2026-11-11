import random
import statistics

from sensor import HUM_KEY, HUM_RANGE, MEAN, TEMP_KEY, TEMP_RANGE, WIND_DIRECTIONS, WIND_KEY, read_sensors

SAMPLES = 5000


def _samples():
    rng = random.Random(23747)
    return [read_sensors(rng) for _ in range(SAMPLES)]


def test_lecturas_en_rango_y_con_tipo_correcto():
    for reading in _samples():
        assert TEMP_RANGE[0] <= reading[TEMP_KEY] <= TEMP_RANGE[1]
        assert round(reading[TEMP_KEY], 2) == reading[TEMP_KEY]
        assert isinstance(reading[HUM_KEY], int)
        assert HUM_RANGE[0] <= reading[HUM_KEY] <= HUM_RANGE[1]
        assert reading[WIND_KEY] in WIND_DIRECTIONS


def test_distribucion_centrada_en_55():
    readings = _samples()
    assert abs(statistics.mean(r[TEMP_KEY] for r in readings) - MEAN) < 1
    assert abs(statistics.mean(r[HUM_KEY] for r in readings) - MEAN) < 1


def test_salen_todas_las_direcciones():
    assert {r[WIND_KEY] for r in _samples()} == set(WIND_DIRECTIONS)
