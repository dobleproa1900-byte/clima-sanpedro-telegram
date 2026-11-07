import os
import sys
import requests
from datetime import datetime

# 1. Lectura de credenciales
api_key = os.environ.get("WEATHER_API_KEY")
token = os.environ.get("TELEGRAM_TOKEN")
chat_gerardo = os.environ.get("TELEGRAM_CHAT_ID_GERARDO")
chat_valeria = os.environ.get("TELEGRAM_CHAT_ID_VALERIA")

chat_ids = [cid for cid in [chat_gerardo, chat_valeria] if cid]

if not api_key or not token or not chat_ids:
    print("ERROR CRÍTICO: Falta la API Key, el Token del Bot o los Chat IDs.")
    sys.exit(1)

try:
    # 2. Consulta a WeatherAPI (pronóstico del día)
    print("Consultando clima detallado para San Pedro...")
    url_weather = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q=San Pedro,Buenos Aires,Argentina&days=1&lang=es"
    res = requests.get(url_weather, timeout=15)
    res.raise_for_status()
    data = res.json()

    # Datos actuales y pronóstico
    curr = data['current']
    day = data['forecast']['forecastday'][0]['day']
    astro = data['forecast']['forecastday'][0]['astro']

    temp = round(curr['temp_c'])
    st = round(curr['feelslike_c'])
    cond = curr['condition']['text'].strip().capitalize()
    max_temp = round(day['maxtemp_c'])
    min_temp = round(day['mintemp_c'])
    
    wind_kph = round(curr['wind_kph'])
    wind_dir = curr['wind_dir']
    humidity = curr['humidity']
    rain_chance = day.get('daily_chance_of_rain', 0)
    uv = curr.get('uv', 0)
    
    sunrise = astro.get('sunrise', '')
    sunset = astro.get('sunset', '')

    # 3. Armado del mensaje enriquecido
    mensaje = (
        f"🌤️ *Reporte Meteorológico — San Pedro*\n\n"
        f"🌡️ *Temperatura:* {temp}°C _(ST: {st}°C)_\n"
        f"📊 *Mín / Máx:* {min_temp}°C / {max_temp}°C\n"
        f"📝 *Estado:* {cond}\n\n"
        f"💨 *Viento:* {wind_kph} km/h ({wind_dir})\n"
        f"💧 *Humedad:* {humidity}%\n"
        f"🌧️ *Prob. de lluvia:* {rain_chance}%\n"
        f"☀️ *Índice UV:* {uv}\n\n"
        f"🌅 *Salida del sol:* {sunrise}\n"
        f"🌇 *Puesta del sol:* {sunset}"
    )

    # 4. Envío a Telegram
    url_telegram = f"https://api.telegram.org/bot{token}/sendMessage"
    for cid in chat_ids:
        print(f"Enviando reporte detallado al Chat ID: {cid}...")
        payload = {
            "chat_id": cid,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        res_tg = requests.post(url_telegram, json=payload, timeout=15)
        res_tg.raise_for_status()

    print("¡Reporte detallado enviado con éxito!")

except Exception as e:
    print(f"ERROR EN EJECUCIÓN: {e}")
    sys.exit(1)
