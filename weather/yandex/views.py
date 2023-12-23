import requests
from django.shortcuts import render
from weather.settings import YANDEX_API_KEY


def get_weather(request):
    city_name = request.GET.get('city')
    weather_data = {}

    # Проверка наличия данных о погоде в кеше
    if city_name in request.session:
        weather_data = request.session[city_name]
    else:
        # Запрос данных о погоде от Yandex API
        yandex_api_url = f"https://api.weather.yandex.ru/v2/forecast?city={city_name}"
        headers = {
            "X-Yandex-API-Key": YANDEX_API_KEY
        }
        response = requests.get(yandex_api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Извлечение нужных данных о погоде из JSON-ответа
            weather_data['temperature'] = data['fact']['temp']
            weather_data['pressure'] = data['fact']['pressure_mm']
            weather_data['wind_speed'] = data['fact']['wind_speed']
            # Сохранение данных о погоде в кеше
            request.session[city_name] = weather_data

    return render(request, 'yandex/weather.html', {
        'city': city_name,
        'weather_data': weather_data
    })