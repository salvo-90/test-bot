import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Ciao! Sono il bot meteo.\n\n"
        "Scrivimi il nome di una città e ti dirò il meteo attuale! 🌤️"
    )

async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "it"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        nome_citta = data["name"]
        paese = data["sys"]["country"]
        descrizione = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        umidita = data["main"]["humidity"]
        vento = data["wind"]["speed"]
        
        messaggio = (
            f"🌍 *{nome_citta}, {paese}*\n\n"
            f"🌤️ {descrizione}\n"
            f"🌡️ Temperatura: *{temp:.1f}°C*\n"
            f"🔽 Min: {temp_min:.1f}°C  🔼 Max: {temp_max:.1f}°C\n"
            f"💧 Umidità: {umidita}%\n"
            f"💨 Vento: {vento} m/s"
        )
        await update.message.reply_text(messaggio, parse_mode="Markdown")
    
    elif response.status_code == 404:
        await update.message.reply_text(f"❌ Città '{city}' non trovata. Controlla il nome e riprova.")
    
    else:
        await update.message.reply_text("⚠️ Errore nel recuperare il meteo. Riprova più tardi.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, meteo))
    print("Bot avviato...")
    app.run_polling()
