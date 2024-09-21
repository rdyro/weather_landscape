from io import BytesIO
from PIL import Image, ImageDraw
import math

from flask import Flask, send_file, request

from weather_landscape import WeatherLandscape


app = Flask(__name__)

@app.route('/image')
def generate_image():
    width = request.args.get('width', default=512, type=int)
    height = request.args.get('height', default=128, type=int)
    lat = request.args.get('lat', default=math.nan, type=float)
    lon = request.args.get('lon', default=math.nan, type=float)
    temperature_unit = request.args.get('temperature_unit', default="C", type=str)
    assert math.isfinite(lat) and math.isfinite(lon), "Please provide lat and lon"
    assert -90.0 <= lat <= 90.0, "Latitude must be between -90 and 90"
    assert -180.0 <= lon <= 180.0, "Longitude must be between -180 and 180"
    assert temperature_unit in ["C", "F"], "Temperature unit must be 'C' or 'F'"
    w = WeatherLandscape(lat=lat, lon=lon, width=width, height=height, 
                         temperature_unit=temperature_unit)
    img = w.make_img()
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
