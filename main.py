import os
import requests

# Variables de entorno (se configuran en GitHub Secrets)
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Lista de destinatarios
DESTINATARIOS_TELEGRAM = [
    os.environ.get("TELEGRAM_CHAT_ID_GERARDO"),
    os.environ.get("TELEGRAM_CHAT_ID_VALERIA")
]

# Coordenadas de San Pedro, Buenos Aires
SAN_PEDRO_COORDS = "-33.6744,-59.6631"

def obtener_pronostico():
    if not WEATHER_API_KEY:
        print("Error: No se encontró WEATHER_API_KEY")
        return None

    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={SAN_PEDRO_COORDS}&days=1&lang=es"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Error al consultar WeatherAPI. Código HTTP: {response.status_code}")
            return None

        data = response.json()["forecast"]["forecastday"][0]["day"]
        condicion = data["condition"]["text"].capitalize()
        temp_max = data["maxtemp_c"]
        temp_min = data["mintemp_c"]
        lluvia_prob = data["daily_chance_of_rain"]
        viento_max = data["maxwind_kph"]
        humedad = data["avghumidity"]

        mensaje = (
            f"🌤️ *PRONÓSTICO DIARIO - SAN PEDRO*\n\n"
            f"• *Estado:* {condicion}\n"
            f"• *T. Máxima:* {temp_max:.1f}°C\n"
            f"• *T. Mínima:* {temp_min:.1f}°C\n"
            f"• *Prob. Lluvia:* {lluvia_prob}%\n"
            f"• *Viento Máx:* {viento_max:.1f} km/h\n"
            f"• *Humedad Promed:* {humedad}%\n\n"
            f"🤖 _Despacho automático de clima_"
        )
        return mensaje
    except Exception as e:
        print(f"Error al procesar el clima: {e}")
        return None

def enviar_telegram(mensaje, chat_id):
    if not chat_id:
        print("Chat ID no encontrado, saltando envío...")
        return
    if not TELEGRAM_BOT_TOKEN:
        print("Error: No se encontró TELEGRAM_BOT_TOKEN")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"Enviado con éxito a Telegram (Chat ID: {chat_id})")
        else:
            print(f"Fallo al enviar a {chat_id}: {res.text}")
    except Exception as e:
        print(f"Error al enviar mensaje por Telegram: {e}")

def main():
    mensaje = obtener_pronostico()
    if mensaje:
        for chat_id in DESTINATARIOS_TELEGRAM:
            if chat_id:
                enviar_telegram(mensaje, chat_id)

if __name__ == "__main__":
    main()