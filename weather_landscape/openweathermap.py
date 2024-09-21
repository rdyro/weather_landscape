from __future__ import annotations

import json
from urllib.request import urlopen
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
import logging
import zipfile

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s -  %(message)s")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class WeatherInfo:
  KTOC = 273.15

  Thunderstorm = 2
  Drizzle = 3
  Rain = 5
  Snow = 6
  Atmosphere = 7
  Clouds = 8

  FORECAST_PERIOD_HOURS = 3

  def __init__(self, fdata: dict[str, Any], temperature_unit: str ="C"):
    assert temperature_unit in ["C", "F"], "Only Celsius and Fahrenheit are supported"
    self.t = datetime.fromtimestamp(int(fdata["dt"]), tz=timezone.utc)
    self.id = int(fdata["weather"][0]["id"])
    self.clouds = fdata.get("clouds", {}).get("all", 0.0)
    self.rain = fdata.get("rain", {}).get("3h", 0.0)
    self.snow = fdata.get("snow", {}).get("3h", 0.0)
    self.windspeed = fdata.get("wind", {}).get("speed", 0.0)
    self.winddeg = fdata.get("wind", {}).get("deg", 0.0)
    self.temp = float(fdata["main"]["temp"]) - WeatherInfo.KTOC
    if temperature_unit == "F":
      self.temp = self.temp * 9 / 5 + 32

  def Print(self):
    print(f"{self.t} {self.id} {self.clouds:03d}% {self.rain:.2f} {self.snow:.2f} {self.temp:+.2f}"
          f" ({self.windspeed:.2f},{self.winddeg:03d})")

  @staticmethod
  def Check(fdata):
    return ("dt" in fdata) and ("weather" in fdata) and ("main" in fdata)

class OpenWeatherMap:
  OWMURL = "http://api.openweathermap.org/data/2.5/"

  def __init__(self, apikey: str, latitude: float, longitude: float, cache: bool = True, 
               temperature_unit: str = "C"):
    self.latitude, self.longitude = latitude, longitude
    reqstr = f"lat={latitude:.4f}&lon={longitude:.4f}&mode=json&APPID={apikey}"
    self.URL_FORECAST = self.OWMURL + "forecast?" + reqstr
    self.URL_CURR = self.OWMURL + "weather?" + reqstr
    self.f, self.timezone_offset_sec = [], None
    if cache:
      self.cache = zipfile.ZipFile(Path(__file__).parent / "cache.zip", mode="a", 
                                   compression=zipfile.ZIP_DEFLATED)
    else:
      self.cache = None
    self.temperature_unit = temperature_unit
    self._get_data()

  def _get_data(self):
    data, cache_key = {}, f"lat={self.latitude:.4f}__lon={self.longitude:.4f}.json"
    if self.cache is not None:
      try:  # try to read from cache
        data = json.loads(self.cache.read(cache_key).decode("utf-8"))
      except KeyError:
        pass
    if data.get("time", 0) < datetime.now(timezone.utc).timestamp() - 3600:
      current_data = json.loads(urlopen(self.URL_CURR).read())
      forecast_data = json.loads(urlopen(self.URL_FORECAST).read())
      data["time"] = datetime.now(timezone.utc).timestamp()
      data["current"], data["forecast"]= current_data, forecast_data
      if self.cache is not None:
        self.cache.writestr(cache_key, json.dumps(data)) 
      logger.log(logging.DEBUG, "Pulling new data")
    else:
      logger.log(logging.DEBUG, "Using cached data")
    return self.parse_json(data["current"], data["forecast"])

  def get_temp_range(self, maxtime):
    maxtime = maxtime.astimezone(timezone.utc)
    if len(self.f) == 0:
      return None
    temps = list(map(lambda x: x.temp, filter(lambda x: x.t <= maxtime, self.f)))
    return max(temps, default=-9998), min(temps, default=9999)

  def parse_json(self, data_curr: dict[str, Any], data_forecast: dict[str, Any]) -> bool:
    self.f.clear()
    self.timezone_offset_sec = data_curr.get("timezone", None)
    cdata = data_curr
    f = WeatherInfo(cdata, self.temperature_unit)
    self.f.append(f)
    if "list" not in data_forecast:
      return False
    for fdata in data_forecast["list"]:
      if not WeatherInfo.Check(fdata):
        continue
      self.f.append(WeatherInfo(fdata, self.temperature_unit))
    return True

  def get_current(self) -> WeatherInfo | None:
    return self.f[0] if len(self.f) > 0 else None

  def get_at(self, time) -> WeatherInfo | None:
    for f in self.f:
      if f.t > time:
        return f
    return None