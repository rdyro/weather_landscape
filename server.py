from io import BytesIO
from PIL import Image, ImageDraw
import math

from flask import Flask, send_file, request

from weather_landscape import WeatherLandscape


app = Flask(__name__)

@app.route('/image')
def generate_image():
    width = int(request.args.get('width', default=512, type=int))
    height = int(request.args.get('height', default=128, type=int))
    lat = int(request.args.get('lat', default=math.nan, type=float))
    lon = int(request.args.get('lon', default=math.nan, type=float))
    assert math.isfinite(lat) and math.isfinite(lon), "Please provide lat and lon"
    lat, lon = math.fmod(lat, 90), math.fmod(lon, 180)
    w = WeatherLandscape(lat=lat, lon=lon, width=width, height=height)
    img = w.make_img()
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
