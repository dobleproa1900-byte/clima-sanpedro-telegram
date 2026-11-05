import os
import sys
import requests

# 1. Lectura de credenciales desde GitHub Secrets
api_key = os.environ.get("WEATHER_API_KEY")
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

print("--- DIAGNÓSTICO DE CREDENCIALES ---")
print(f"WEATHER_API_KEY: {'OK' if api_key else 'FALTA'}")
print(f"TELEGRAM_TOKEN: {'OK' if token else 'FALTA'}")
print(f"TELEGRAM_CHAT_ID: {'OK' if chat_id else 'FALTA'}")

if not api_key or not token or not chat_id:
    print("ERROR CRÍTICO: Falta una o más variables en GitHub Secrets.")
    sys.exit(1)

try:
    # 2. Consulta a WeatherAPI
    print("Consultando clima para San Pedro...")
    url_weather = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q=San Pedro,Buenos Aires,Argentina&days=1&lang=es"
    res = requests.get(url_weather, timeout=15)
    res.raise_for_status()
    data = res.json()

    temp = data['current']['temp_c']
    cond = data['current']['condition']['text']
    max_temp = data['forecast']['forecastday'][0]['day']['maxtemp_c']
    min_temp = data['forecast']['forecastday'][0]['day']['mintemp_c']

    mensaje = (
        f"🌤️ *Clima en San Pedro*\n\n"
        f"🌡️ Actual: *{temp}°C*\n"
        f"📝 Estado: {cond.capitalize()}\n"
        f"📊 Mín/Máx: *{min_temp}°C* / *{max_temp}°C*"
    )

    # 3. Envío a Telegram
    print("Enviando reporte a Telegram...")
    url_telegram = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    res_tg = requests.post(url_telegram, json=payload, timeout=15)
    res_tg.raise_for_status()
    print("¡Reporte enviado con éxito a Telegram!")

except Exception as e:
    print(f"ERROR EN EJECUCIÓN: {e}")
    sys.exit(1)
