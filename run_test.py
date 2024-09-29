from weather_landscape import WeatherLandscape

# coordinates for Warsaw
#w = WeatherLandscape(52.237049, 21.017532, width=512, height=128, temperature_unit="C")
w = WeatherLandscape(52.38, -2.03, width=512, height=128, temperature_unit="C")
fn = w.make_and_save_img("weather_landscape_example.png")
print("Saved to", fn)
