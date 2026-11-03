import os
import requests
from datetime import datetime

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

DESTINATARIOS_TELEGRAM = [
    os.environ.get("TELEGRAM_CHAT_ID_GERARDO"),
    os.environ.get("TELEGRAM_CHAT_ID_VALERIA")
]

SAN_PEDRO_COORDS = "-33.6744,-59.6631"

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

WIND_DIRECTIONS = {
    "N": "Norte", "S": "Sur", "E": "Este", "W": "Oeste",
    "NE": "Noreste", "NW": "Noroeste", "SE": "Sureste", "SW": "Suroeste",
    "ENE": "Este-Noreste", "ESE": "Este-Sureste", "NNE": "Norte-Noreste", "NNW": "Norte-Noroeste",
    "SSE": "Sur-Sureste", "SSW": "Sur-Suroeste", "WNW": "Oeste-Noroeste", "WSW": "Oeste-Suroeste"
}

def clasificar_uv(uv):
    if uv <= 2: return "Bajo"
    elif uv <= 5: return "Moderado"
    elif uv <= 7: return "Alto"
    elif uv <= 10: return "Muy alto"
    else: return "Extremo"

def formato_hora_24(hora_str):
    try:
        return datetime.strptime(hora_str, "%I:%M %p").strftime("%H:%M hs")
    except Exception:
        return hora_str

def obtener_pronostico():
    if not WEATHER_API_KEY:
        print("Error: WEATHER_API_KEY no encontrada")
        return None

    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={SAN_PEDRO_COORDS}&days=1&lang=es"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Error al consultar WeatherAPI: {response.status_code}")
            return None

        res_json = response.json()
        current = res_json["current"]
        forecastday = res_json["forecast"]["forecastday"][0]
        day = forecastday["day"]
        astro = forecastday["astro"]
        hours = forecastday["hour"]

        # Formatear Fecha
        fecha_obj = datetime.strptime(forecastday["date"], "%Y-%m-%d")
        fecha_formateada = f"{DIAS[fecha_obj.weekday()]} {fecha_obj.day} de {MESES[fecha_obj.month - 1]} de {fecha_obj.year}"

        # Formatear Datos Generales
        condicion = current["condition"]["text"].capitalize()
        temp_actual = current["temp_c"]
        sensacion = current["feelslike_c"]
        temp_max = day["maxtemp_c"]
        temp_min = day["mintemp_c"]
        precip_prob = day["daily_chance_of_rain"]
        precip_mm = day["totalprecip_mm"]
        viento_vel = current["wind_kph"]
        viento_dir_raw = current["wind_dir"]
        viento_dir = WIND_DIRECTIONS.get(viento_dir_raw, viento_dir_raw)
        rafagas = current["gust_kph"]
        humedad = current["humidity"]
        uv_val = day.get("uv", current.get("uv", 0))
        uv_cat = clasificar_uv(uv_val)
        presion = int(current["pressure_mb"])

        # Tramos (Mañana: 09 hs, Tarde: 15 hs, Noche: 21 hs)
        temp_manana = hours[9]["temp_c"]
        temp_tarde = hours[15]["temp_c"]
        temp_noche = hours[21]["temp_c"]

        # Sol
        amanecer = formato_hora_24(astro["sunrise"])
        atardecer = formato_hora_24(astro["sunset"])

        mensaje = (
            f"📍 *San Pedro, Buenos Aires*\n"
            f"📅 {fecha_formateada}\n"
            f"☁️ {condicion}\n\n"
            f"🌡️ Temperatura: {temp_actual:.1f}°C (Sensación: {sensacion:.1f}°C)\n"
            f"🔺 Máx: {temp_max:.1f}°C | 🔻 Mín: {temp_min:.1f}°C\n"
            f"🌧️ Precipitaciones: {precip_prob}% ({precip_mm:.1f}mm)\n"
            f"💨 Viento: {viento_vel:.1f} km/h ({viento_dir}) | Ráfagas: {rafagas:.1f} km/h\n"
            f"💧 Humedad: {humedad}%\n"
            f"☀️ Índice UV: {uv_val} ({uv_cat})\n"
            f"⏲️ Presión: {presion} hPa\n\n"
            f"📊 Pronóstico por tramos:\n"
            f"- Mañana: \n {temp_manana:.1f}°C\n"
            f"- Tarde: \n {temp_tarde:.1f}°C\n"
            f"- Noche: \n {temp_noche:.1f}°C\n\n"
            f"🌅 Amanecer: {amanecer} | 🌇 Atardecer: {atardecer}"
        )
        return mensaje
    except Exception as e:
        print(f"Error procesando reporte: {e}")
        return None

def enviar_telegram(mensaje, chat_id):
    if not chat_id or not TELEGRAM_BOT_TOKEN:
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