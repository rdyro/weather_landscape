from __future__ import annotations

from typing import Callable
from PIL import Image
from datetime import datetime, timezone, timedelta

from .sprites import Sprites
from .openweathermap import OpenWeatherMap, WeatherInfo
from suntime import Sun


def mybeizelfnc(t, d0, d1, d2, d3):
  return (1 - t) * (
    (1 - t) * ((1 - t) * d0 + t * d1) + t * ((1 - t) * d1 + t * d2)
  ) + t * ((1 - t) * ((1 - t) * d1 + t * d2) + t * ((1 - t) * d2 + t * d3))

def mybezier(x, xa, ya, xb, yb):
  xc = (xb + xa) / 2.0
  d = xb - xa
  t = float(x - xa) / float(d)
  y = mybeizelfnc(t, ya, ya, yb, yb)
  return int(y)


def _get_time_after(time_fn: Callable[[datetime], datetime], t: datetime) -> datetime:
  # get first sunrise after t
  t = t.astimezone(timezone.utc)
  t_target = time_fn(t)
  return t_target if (t_target - t).total_seconds() > 0 else time_fn(t + timedelta(days=1))

def get_suntimes(t: datetime, lat: float, lon: float, how_many_days: int = 5
                 ) -> dict[str, list[datetime]]:
  sun = Sun(lat, lon)
  day0 = datetime(year=t.year, month=t.month, day=t.day, tzinfo=timezone.utc)
  dt_day = timedelta(days=1)
  sunrises, sunsets = [], []
  for i in range(-1, max(how_many_days, 1)):
    sunrises.append(sun.get_sunrise_time(day0 + i * dt_day))
    sunsets.append(sun.get_sunset_time(day0 + i * dt_day))
  return {"sunrises": sunrises, "sunsets": sunsets}

#get_sunrise = lambda t, lat, lon: _get_time_after(Sun(lat, lon).get_sunrise_time, t)
#get_sunset = lambda t, lat, lon: _get_time_after(Sun(lat, lon).get_sunset_time, t)

def _is_stationary_point(f_prev2: WeatherInfo | None, f_prev: WeatherInfo | None, 
                         f: WeatherInfo | None) -> bool:
  if f_prev2 is None or f_prev is None or f is None:
    return False
  elif f_prev.temp >= f_prev2.temp and f_prev.temp >= f.temp:
    print(f"Maximum!")
    return True
  elif f_prev.temp <= f_prev2.temp and f_prev.temp <= f.temp:
    print(f"Minimum!")
    return True
  else:
    return False

class DrawWeather:
  XSTART = 32
  XSTEP = 44
  XFLAT = 10

  DEFAULT_DEGREE_PER_PIXEL = 0.5

  def __init__(self, canvas: Image, sprites: Sprites):
    self.img = canvas
    self.sprite = sprites
    (self.IMAGE_WIDTH, self.IMAGE_HEIGHT) = self.img.size
    # correction from the original 296x128 image
    self.YSTEP = round((self.IMAGE_HEIGHT / self.IMAGE_WIDTH) * (128 / 296) * 200)
    self.DEFAULT_DEGREE_PER_PIXEL = self.IMAGE_HEIGHT / 200
    self.TEMP_CANVAS_FRACTION = 1 / 3
    self.CLOUD_CANVAS_FRACTION = 1 / 3
    self.SUNMOON_CANVAS_FRACTION = 1 / 3

  def TimeDiffToPixels(self, dt):
    ds = dt.total_seconds()
    secondsperpixel = (
      WeatherInfo.FORECAST_PERIOD_HOURS * 60 * 60
    ) / DrawWeather.XSTEP
    return int(ds / secondsperpixel)

  def DegToPix(self, t, yoffset, temprange):
    min_temprange = 5 # minimal temperature range for drawing
    sprite_height = 20 # pixels
    canvas_height = (self.IMAGE_HEIGHT - yoffset - sprite_height) * self.TEMP_CANVAS_FRACTION
    degreeperpixel = max(temprange, min_temprange) / canvas_height
    n = (t - self.tmin) / degreeperpixel
    y = round((self.IMAGE_HEIGHT - yoffset) - n)
    return y

  # todo: add thunderstorm
  # todo: add fog
  # todo: add snow

  def Draw(self, yoffset, owm: OpenWeatherMap):
    height, width= self.IMAGE_HEIGHT, self.IMAGE_WIDTH
    canvas_height = max(self.IMAGE_HEIGHT - yoffset, 0)
    temp_canvas_height = round(canvas_height * self.TEMP_CANVAS_FRACTION)
    cloud_canvas_height = round(canvas_height * self.CLOUD_CANVAS_FRACTION)

    nforecast = (width - self.XSTART) / self.XSTEP
    maxtime = datetime.now(timezone.utc) + timedelta(
      hours=WeatherInfo.FORECAST_PERIOD_HOURS * nforecast
    )

    (self.tmax, self.tmin) = owm.get_temp_range(maxtime)
    temprange = self.tmax - self.tmin

    xpos = 0
    tline = [0] * (width + self.XSTEP + 1)
    f = owm.get_current()
    assert f is not None, "No current weather data"
    oldtemp = f.temp
    oldy = self.DegToPix(oldtemp, yoffset, temprange)
    for i in range(self.XSTART):
      tline[i] = oldy
    cloud_sprite_height = 13
    yclouds = round(self.IMAGE_HEIGHT - yoffset - temp_canvas_height - cloud_sprite_height / 2)
    ysunmoon = round(self.IMAGE_HEIGHT - yoffset - temp_canvas_height - cloud_canvas_height)

    self.sprite.Draw("house", xpos, 0, oldy)
    self.sprite.DrawInt(oldtemp, xpos + 8, oldy + 10)
    self.sprite.DrawCloud(f.clouds, xpos, yclouds, self.XSTART, yclouds)
    self.sprite.DrawRain(f.rain, xpos, yclouds, self.XSTART, tline)
    self.sprite.DrawSnow(f.snow, xpos, yclouds, self.XSTART, tline)

    t = datetime.now(timezone.utc)
    dt = timedelta(hours=WeatherInfo.FORECAST_PERIOD_HOURS)
    tf = t

    xpos = int(self.XSTART)
    nforecast = int(nforecast)

    n = int((self.XSTEP - self.XFLAT) / 2)
    for i in range(nforecast + 1):
      f = owm.get_at(tf)
      if f == None:
        continue
      #f.Print()
      newtemp = f.temp
      newy = self.DegToPix(newtemp, yoffset, temprange)
      for i in range(n):
        tline[xpos + i] = mybezier(xpos + i, xpos, oldy, xpos + n, newy)

      for i in range(self.XFLAT):
        tline[int(xpos + i + n)] = newy

      xpos += n + self.XFLAT

      n = self.XSTEP - self.XFLAT
      oldtemp = newtemp
      oldy = newy
      tf += dt

    tf = t
    xpos = self.XSTART
    suntimes = get_suntimes(t, owm.latitude, owm.longitude)
    for i in range(nforecast + 1):
      f = owm.get_at(tf)
      if f == None:
        continue
      for t_sunrise in suntimes["sunrises"]:
        if (tf <= t_sunrise) and (tf + dt > t_sunrise):
          dx = self.TimeDiffToPixels(t_sunrise - tf) - self.XSTEP / 2
          self.sprite.Draw("sun", 0, xpos + dx, ysunmoon)

      for t_sunset in suntimes["sunsets"]:
        if (tf <= t_sunset) and (tf + dt > t_sunset):
          dx = self.TimeDiffToPixels(t_sunset - tf) - self.XSTEP / 2
          self.sprite.Draw("moon", 0, xpos + dx, ysunmoon)
      xpos += self.XSTEP
      tf += dt

    tf = t
    xpos = self.XSTART
    n = int((self.XSTEP - self.XFLAT) / 2)
    for i in range(nforecast + 1):
      f = owm.get_at(tf)
      if f == None:
        continue
      self.sprite.DrawInt(f.temp, xpos + n, tline[xpos + n] + 10)

      t0 = f.t - dt / 2
      t1 = f.t + dt / 2

      # FLOWERS: black - midnight, white - midday
      dt_onehour = timedelta(hours=1)
      dx_onehour = self.XSTEP / WeatherInfo.FORECAST_PERIOD_HOURS
      t_iter = t0 + dt_onehour
      if owm.timezone_offset_sec is not None:
        tt = t_iter + timedelta(seconds=owm.timezone_offset_sec) # local time from UTC offset
      else:
        tt = t_iter.astimezone(datetime.now().astimezone().tzinfo) # computer local time
      xx = xpos
      round_hour = round(tt.hour + tt.minute / 60 + tt.second / 3600)
      while t_iter <= t1:
        ix = round(xx)
        if ix >= len(tline):
          break
        # tie-breaking sec
        if round_hour == 12:
          self.sprite.Draw("flower", 1, ix, tline[ix])
        elif round_hour == 0:
          self.sprite.Draw("flower", 0, ix, tline[ix])
        elif round_hour in (3, 6, 9, 15, 18, 21):
          self.sprite.DrawWind(f.windspeed, f.winddeg, ix, tline)
        round_hour = (round_hour + 1) % 24
        tt += dt_onehour
        t_iter += dt_onehour
        xx += dx_onehour

      self.sprite.DrawCloud(f.clouds, xpos, yclouds, self.XSTEP, self.YSTEP / 2)
      self.sprite.DrawRain(f.rain, xpos, yclouds, self.XSTEP, tline)
      self.sprite.DrawSnow(f.snow, xpos, yclouds, self.XSTEP, tline)

      xpos += self.XSTEP
      tf += dt

    for x in range(width):
      if tline[x] < height:
        self.sprite.Dot(x, tline[x], Sprites.BLACK)
      else:
        print("out of range: %i - %i(max %i)" % (x, tline[x], height))
