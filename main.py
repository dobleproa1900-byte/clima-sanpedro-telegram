import os
import sys
import requests

# 1. Lectura de credenciales con los nombres exactos de tus GitHub Secrets
api_key = os.environ.get("WEATHER_API_KEY")
token = os.environ.get("TELEGRAM_TOKEN")
chat_gerardo = os.environ.get("TELEGRAM_CHAT_ID_GERARDO")
chat_valeria = os.environ.get("TELEGRAM_CHAT_ID_VALERIA")

# Filtrar solo los chat IDs que contengan valor
chat_ids = [cid for cid in [chat_gerardo, chat_valeria] if cid]

print("--- DIAGNÓSTICO DE CREDENCIALES ---")
print(f"WEATHER_API_KEY: {'OK' if api_key else 'FALTA'}")
print(f"TELEGRAM_BOT_TOKEN: {'OK' if token else 'FALTA'}")
print(f"Destinatarios encontrados: {len(chat_ids)}")

if not api_key or not token or not chat_ids:
    print("ERROR CRÍTICO: Falta la API Key, el Token del Bot o los Chat IDs.")
    sys.exit(1)

try:
    # 2. Consulta a WeatherAPI para San Pedro
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

    # 3. Envío a cada destinatario (Gerardo y Valeria)
    url_telegram = f"https://api.telegram.org/bot{token}/sendMessage"
    for cid in chat_ids:
        print(f"Enviando reporte al Chat ID: {cid}...")
        payload = {
            "chat_id": cid,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        res_tg = requests.post(url_telegram, json=payload, timeout=15)
        res_tg.raise_for_status()

    print("¡Reporte enviado con éxito a todos los destinatarios!")

except Exception as e:
    print(f"ERROR EN EJECUCIÓN: {e}")
    sys.exit(1)
