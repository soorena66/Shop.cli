from flask import Flask, render_template, request
from Meteo_models import Weather
import requests
import datetime

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if not city:
            return render_template('index.html', error='Please enter city name.')

        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url).json()

            if not geo_res.get('results'):
                return render_template('index.html', error='city not found!')

            location = geo_res['results'][0]
            lat = location['latitude']
            lon = location['longitude']
            city_name = location.get('name', city)

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,surface_pressure,weather_code"
            weather_res = requests.get(weather_url).json()

            current = weather_res.get('current', {})
            temp = current.get('temperature_2m')
            humidity = current.get('relative_humidity_2m')
            pressure = current.get('surface_pressure')
            
            weather_code = current.get('weather_code', 0)
            
            description = get_weather_description(weather_code)
            icon = get_weather_icon(weather_code)

            date = datetime.datetime.now()

            Weather.create(
                temp=temp if temp is not None else 0.0,
                pressure=int(pressure) if pressure is not None else 0,
                humidity=int(humidity) if humidity is not None else 0,
                description=description,
                date=date,
                icon=icon,
                city=city_name
            )

            res = {
                'name': city_name,
                'main': {
                    'temp': temp,
                    'pressure': pressure,
                    'humidity': humidity
                },
                'weather': [
                    {'description': description, 'icon': icon}
                ]
            }

            return render_template('index.html', res=res)

        except Exception as e:
            error = 'city not found!'
            return render_template('index.html', error=error)

    return render_template('index.html')


def get_weather_description(code):
    mapping = {
        0: 'clear sky',
        1: 'mainly clear',
        2: 'partly cloudy',
        3: 'overcast',
        45: 'foggy',
        48: 'depositing rime fog',
        51: 'light drizzle',
        53: 'moderate drizzle',
        55: 'dense drizzle',
        61: 'slight rain',
        62: 'moderate rain',
        63: 'heavy rain',
        71: 'slight snow fall',
        73: 'moderate snow fall',
        75: 'heavy snow fall',
        95: 'thunderstorm'
    }
    return mapping.get(code, 'clear sky')


def get_weather_icon(code):
    if code in [0, 1]:
        return '01d'
    elif code in [2]:
        return '02d'
    elif code in [3]:
        return '04d'
    elif code in [51, 53, 55, 61, 62, 63]:
        return '10d'
    elif code in [71, 73, 75]:
        return '13d'
    elif code in [95]:
        return '11d'
    return '01d'


if __name__ == "__main__":
    app.run(debug=True)
