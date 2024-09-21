# Minimalistic copy of `lds133`'s Weather Landscape

<p align="center">
<img src="media/warsaw_weather_landscape.png" style="width:50%;max-width:512px">
</p>

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

### Dynamically Serving the Weather Landscape

Run the [Flask](https://github.com/pallets/flask) server
```bash
$ env OMW_KEY={your key} python3 server.py
```

Visit the URL 
- `http://{server address}/image?lat={latitude}&lon={longitude}&width={width}&height={height}&temperature_unit={unit}`

for example

- `http://localhost:8000/image?lat=52.24&lon=21.02&width=512&height=128&temperature_unit=C`


### Legend

| Event image | Description |
|----------|------------|
|![example](media/sun_00.png)| Sunrise | 
|![example](media/moon_00.png)| Sunset |
|![example](media/cloud_30.png)| Cloud cover |
|![example](media/house_00.png)| Current time position|
|![example](media/flower_00.png)| Midnight |
|![example](media/flower_01.png)| Midday |
|![example](media/palm_03.png)| South wind |
|![example](media/east_03.png)| East wind |
|![example](media/tree_03.png)| West wind |
|![example](media/pine_02.png)| North wind |
