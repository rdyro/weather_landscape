import os
import tempfile
from PIL import Image
from pathlib import Path

from .openweathermap import OpenWeatherMap
from .sprites import Sprites
from .draw_weather import DrawWeather


class WeatherLandscape:
  OWM_KEY = os.environ.get("OWM_KEY", None)
  SPRITES_DIR = Path(__file__).parent /  "sprite"
  DRAWOFFSET = 14  # for font size 10 under the temperature line

  def __init__(self, lat: float, lon: float, width=512, height=128):
    assert self.OWM_KEY != None, ("Set OWM_KEY variable to your OpenWeather API" 
                                  "key")
    self.width, self.height = width, height
    self.lat, self.long = lat, lon

  def make_img(self) -> Image.Image:
    owm = OpenWeatherMap(self.OWM_KEY, latitude=self.lat, longitude=self.long)
    img = Image.new("1", (self.width, self.height), 1) # 1-bit pixels, black and white, white background
    spr = Sprites(self.SPRITES_DIR, img)
    art = DrawWeather(img, spr)
    art.Draw(self.DRAWOFFSET, owm)
    return img

  def make_and_save_img(self) -> str:
    img, tmp = self.make_img(), tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name
