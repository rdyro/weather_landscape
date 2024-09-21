from weather_landscape import WeatherLandscape

# coordinates for Warsaw
w = WeatherLandscape(52.237049, 21.017532, width=1024, height=128)
fn = w.make_and_save_img()
print("Saved to", fn)
