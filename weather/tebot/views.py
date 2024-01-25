import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from flask import Flask, render_template

TELEGRAM_BOT_TOKEN = ''
OPENWEATHERMAP_API_KEY = '2aa647e59ede7609c9e1e96c990f2b63'


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        city_name = request.POST.get('city')
        text = request.POST.get('text')
        if text == '/start':
            return render(request, 'tebot/webhook.html')
        elif text == '/help':
            return render(request, 'tebot/webhook.html')
        else:
            weather_data = get_weather_data(city_name)
            if weather_data:
                forecast = get_weather_forecast(city_name)
                return render(request, 'tebot/webhook.html', {'weather_data': weather_data, 'forecast': forecast})
            else:
                return render(request, 'tebot/webhook.html', {'weather_data': 'Не удалось получить данные о погоде.'})
    return render(request, 'tebot/webhook.html')

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=params)
    return response

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        return f"Погода в городе {city}:\nТемпература: {temperature}°C\nВлажность: {humidity}%\nОписание: {description}"
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Ошибка соединения: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Ошибка запроса: {err}"

def get_weather_forecast(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast_info = data['list']
        forecast = []
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        for info in forecast_info:
            # Получаем дату из прогноза
            dt_txt = info['dt_txt']
            date = datetime.datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S').date()
            # Если дата соответствует завтрашнему дню, добавляем прогноз в список
            if date == tomorrow:
                temperature = info['main']['temp']
                humidity = info['main']['humidity']
                description = info['weather'][0]['description']
                forecast.append({
                    'date': dt_txt,
                    'temperature': temperature,
                    'humidity': humidity,
                    'description': description
                })
        return forecast
    else:
        return None

app = Flask(__name__)

@app.route('/weather_forecast')
def weather_forecast():
    city = 'Москва'
    forecast = get_weather_forecast(city)
    if forecast:
        return render_template('tebot/webhook.html', forecast=forecast)
    else:
        error_message = "Прогноз погоды недоступен."
        return render_template('tebot/error.html', error_message=error_message)
