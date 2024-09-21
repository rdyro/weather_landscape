# Minimalistic copy of `lds133`'s Weather Landscape

Visualizing Weather Forecasts Through Landscape Imagery 

Forked from [lds133](https://github.com/lds133) excellent project.

Visit [https://openweathermap.org/](https://openweathermap.org/) for an API Key
and export it as `OWM_KEY=...` in your environment

Installable via pip:
```bash
$ pip install .
$ # OR
$ pip install git+https://github.com/rdyro/weather_landscape
```

Example usage
```python
from weather_landscape import WeatherLandscape

# lon - longitude, lat - latitude as floating point numbers (negative for west and south)
w = WeatherLandscape(lon=52.237049, lat=21.017532, width=1024, height=128)
img = w.make_img() # get the PIL.Image.Image object directly

# or render and save to file
filename = "warsaw_weather_landscape.png"
w.make_and_save_img(filename) # make and save the image
```

### Legend

| Event image | Description |
|----------|------------|
|![example](weather_landscape/sprite/sun_00.png)| Sunrise | 
|![example](weather_landscape/sprite/moon_00.png)| Sunset |
|![example](weather_landscape/sprite/cloud_30.png)| Cloud cover |
|![example](weather_landscape/sprite/house_00.png)| Current time position|
|![example](weather_landscape/sprite/flower_00.png)| Midnight |
|![example](weather_landscape/sprite/flower_01.png)| Midday |
|![example](weather_landscape/sprite/palm_03.png)| South wind |
|![example](weather_landscape/sprite/east_03.png)| East wind |
|![example](weather_landscape/sprite/tree_03.png)| West wind |
|![example](weather_landscape/sprite/pine_02.png)| North wind |
