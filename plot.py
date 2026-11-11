"""grafica en vivo de la telemetria."""
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from sensor import HUM_KEY, HUM_RANGE, TEMP_KEY, TEMP_RANGE, WIND_DIRECTIONS, WIND_KEY


class LivePlot:
    def __init__(self, title: str):
        self._fig, self._axes = plt.subplots(3, 1, sharex=True, figsize=(11, 8))
        self._fig.suptitle(title)
        self._times, self._temps, self._hums, self._winds = [], [], [], []
        plt.ion()
        plt.show()

    def is_open(self) -> bool:
        return plt.fignum_exists(self._fig.number)

    def add(self, when: datetime, reading: dict):
        self._times.append(when)
        self._temps.append(reading[TEMP_KEY])
        self._hums.append(reading[HUM_KEY])
        self._winds.append(WIND_DIRECTIONS.index(reading[WIND_KEY]))

    def render(self):
        ax_temp, ax_hum, ax_wind = self._axes
        self._draw(ax_temp, self._temps, "temperatura (°C)", TEMP_RANGE, "tab:red")
        self._draw(ax_hum, self._hums, "humedad (%)", HUM_RANGE, "tab:blue")
        self._draw(ax_wind, self._winds, "viento", (-0.5, len(WIND_DIRECTIONS) - 0.5), "tab:green", style="o")
        ax_wind.set_yticks(range(len(WIND_DIRECTIONS)), WIND_DIRECTIONS)
        ax_wind.set_xlabel(f"hora de recepcion  |  {len(self._times)} lecturas")
        ax_wind.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self._fig.autofmt_xdate()

    def wait(self, seconds: float):
        plt.pause(seconds)

    def _draw(self, ax, values, label, ylim, color, style="o-"):
        ax.cla()
        ax.plot(self._times, values, style, color=color, markersize=4)
        ax.set_ylabel(label)
        ax.set_ylim(*ylim)
        ax.grid(alpha=0.3)
