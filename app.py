from flask import Flask, render_template, request
import requests

app = Flask(__name__)

weather_key = 'mHzlqIQWilrvAlyllHytcR2qtLZfpAY1'
maps_key = '66d70ae1-fcc8-4224-a428-ee3d9958aebf'


def location_key(lat: float, lon: float):
    '''Получает ключ локации по координатам'''
    try:
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Неккоректные значения широты и долготы")
        api_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
        response = requests.get(api_url, params={"apikey": weather_key,
                                                 "q": f"{lat},{lon}",
                                                 "language": "ru",
                                                 "details": "true"})
        response.raise_for_status()
        data = response.json()
        if "Key" not in data:
            raise ValueError("Ключ локации не найден, проверьте корректность координат")
        return data['Key']
    except ValueError as e:
        raise ValueError(e)
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(e)


def get_weather_by_coords(lat: float, lon: float):
    '''Возвращает информацию о погоде по координатам'''
    try:
        loc_key = location_key(lat, lon)
        response = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{loc_key}",
                                params={"apikey": weather_key,
                                        "language": "ru",
                                        "details": "true",
                                        "metric": "true"})
        response.raise_for_status()
        data = response.json()
        temperature = (data['DailyForecasts'][0]['Temperature']['Minimum']['Value'] +
                       data['DailyForecasts'][0]['Temperature']['Maximum']['Value']) / 2
        humidity = (data['DailyForecasts'][0]['Day']['RelativeHumidity']['Average'] +
                    data['DailyForecasts'][0]['Night']['RelativeHumidity']['Average']) / 2
        wind_speed = (data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value'] +
                      data['DailyForecasts'][0]['Night']['Wind']['Speed']['Value']) / 2
        rain_probability = (data['DailyForecasts'][0]['Day']['RainProbability'] +
                            data['DailyForecasts'][0]['Night']['RainProbability']) / 2
        return {"temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "wind_speed": round(wind_speed, 2),
                "rain_probability": round(rain_probability, 2)}

    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(f"Произошла ошибка HTTP: {e}")
    except Exception as e:
        raise Exception(e)


def check_bad_weather(weather: dict) -> bool:
    if weather['temperature'] < 0 or weather['temperature'] > 35:
        return True
    if weather['wind_speed'] > 50:
        return True
    if weather['rain_probability'] > 70:
        return True
    return False


def send_maps_request(data: str):
    '''Отправляет запрос в Яндекс.Карты'''
    api_url = 'https://geocode-maps.yandex.ru/1.x/'
    r = requests.get(api_url,
                     params=dict(format='json',
                                 apikey=maps_key,
                                 geocode=data))
    if r.status_code == 200:
        return r.json()['response']
    elif r.status_code == 403:
        raise Exception('Такого адреса|координат нет.')
    else:
        raise Exception('Что-то пошло не так.')


def get_coords_by_address(address: str):
    '''Получает координаты по названию города'''
    coords = send_maps_request(address)['GeoObjectCollection']['featureMember']

    if not coords:
        raise Exception(f'Координаты города {address} отсуствуют.')

    coords = coords[0]['GeoObject']['Point']['pos']
    lon, lat = coords.split(' ')
    return float(lat), float(lon)


@app.route('/', methods=["GET", "POST"])
def main():
    try:
        if request.method == 'GET':
            return render_template("form.html")
        if request.method == "POST":
            start_city = request.form.get('start_city', '')
            end_city = request.form.get('end_city', '')
            if start_city == '' or end_city == '':
                raise ValueError("Все поля обязательны для ввода")
            start_lat, start_lon = get_coords_by_address(start_city)
            end_lat, end_lon = get_coords_by_address(end_city)

            start_weather = get_weather_by_coords(float(start_lat), float(start_lon))
            end_weather = get_weather_by_coords(float(end_lat), float(end_lon))

            if check_bad_weather(start_weather) or check_bad_weather(end_weather):
                result = "Ой-ой, погода плохая!"
            else:
                result = "Погода супер!"

            return render_template("form.html", result=result,
                                   start_city=start_city,
                                   start_temperature=start_weather['temperature'],
                                   start_humidity=start_weather['humidity'],
                                   start_wind_speed=start_weather['wind_speed'],
                                   start_rain_probability=start_weather['rain_probability'],
                                   end_city=end_city,
                                   end_temperature=end_weather['temperature'],
                                   end_humidity=end_weather['humidity'],
                                   end_wind_speed=end_weather['wind_speed'],
                                   end_rain_probability=end_weather['rain_probability'],
                                   )
    except ValueError as e:
        return render_template("error.html", error=e)
    except Exception as e:
        return render_template("error.html", error=e)


if __name__ == '__main__':
    app.run()
