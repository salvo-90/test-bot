import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

def get_meteo(city: str) -> str:
    # Step 1: geocoding - converti nome città in coordinate
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "it"}
    geo_resp = requests.get(geo_url, params=geo_params)
    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        return f"❌ Città '{city}' non trovata. Controlla il nome e riprova."

    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    nome_citta = result["name"]
    paese = result.get("country", "")

    # Step 2: meteo dalle coordinate
    meteo_url = "https://api.open-meteo.com/v1/forecast"
    meteo_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 1
    }
    meteo_resp = requests.get(meteo_url, params=meteo_params)
    meteo_data = meteo_resp.json()

    current = meteo_data["current"]
    daily = meteo_data["daily"]

    temp = current["temperature_2m"]
    percepita = current["apparent_temperature"]
    umidita = current["relative_humidity_2m"]
    vento = current["wind_speed_10m"]
    temp_min = daily["temperature_2m_min"][0]
    temp_max = daily["temperature_2m_max"][0]
    wmo = current["weather_code"]

    # Descrizione dal codice WMO
    wmo_desc = {
        0: "☀️ Cielo sereno",
        1: "🌤️ Prevalentemente sereno",
        2: "⛅ Parzialmente nuvoloso",
        3: "☁️ Nuvoloso",
        45: "🌫️ Nebbia",
        48: "🌫️ Nebbia con brina",
        51: "🌦️ Pioggerella leggera",
        53: "🌦️ Pioggerella moderata",
        55: "🌧️ Pioggerella intensa",
        61: "🌧️ Pioggia leggera",
        63: "🌧️ Pioggia moderata",
        65: "🌧️ Pioggia intensa",
        71: "🌨️ Neve leggera",
        73: "🌨️ Neve moderata",
        75: "❄️ Neve intensa",
        80: "🌦️ Rovesci leggeri",
        81: "🌧️ Rovesci moderati",
        82: "⛈️ Rovesci intensi",
        95: "⛈️ Temporale",
        96: "⛈️ Temporale con grandine",
        99: "⛈️ Temporale con grandine intensa",
    }
    descrizione = wmo_desc.get(wmo, "🌡️ Condizioni variabili")

    return (
        f"🌍 *{nome_citta}, {paese}*\n\n"
        f"{descrizione}\n"
        f"🌡️ Temperatura: *{temp}°C* (percepita {percepita}°C)\n"
        f"🔽 Min: {temp_min}°C  🔼 Max: {temp_max}°C\n"
        f"💧 Umidità: {umidita}%\n"
        f"💨 Vento: {vento} km/h"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Ciao! Sono il bot meteo.\n\n"
        "Scrivimi il nome di una città e ti dirò il meteo attuale! 🌤️"
    )

async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    risposta = get_meteo(city)
    await update.message.reply_text(risposta, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, meteo))
    print("Bot avviato...")
    app.run_polling()
