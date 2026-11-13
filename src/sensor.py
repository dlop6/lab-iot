"""simulacion de los sensores de la estacion meteorologica."""
import random

TEMP_KEY = "temperatura"
HUM_KEY = "humedad"
WIND_KEY = "direccion_viento"

TEMP_RANGE = (0.0, 110.0)
HUM_RANGE = (0, 100)
WIND_DIRECTIONS = ("N", "NO", "O", "SO", "S", "SE", "E", "NE")

# normal centrada en 55, con sigma 15 casi todo cae dentro del rango
MEAN = 55
STD_DEV = 15

_rng = random.Random()


def _clamp(value, low, high):
    return max(low, min(high, value))


def read_sensors(rng: random.Random = _rng) -> dict:
    return {
        TEMP_KEY: round(_clamp(rng.gauss(MEAN, STD_DEV), *TEMP_RANGE), 2),
        HUM_KEY: int(_clamp(round(rng.gauss(MEAN, STD_DEV)), *HUM_RANGE)),
        WIND_KEY: rng.choice(WIND_DIRECTIONS),
    }
