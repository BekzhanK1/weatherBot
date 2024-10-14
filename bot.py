import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import os
from dotenv import load_dotenv
from translation import weather_descriptions

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

ASK_CITY = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор и просит пользователя ввести название города."""
    await update.message.reply_text("Привет! Я ваш погодный бот. Пожалуйста, введите название города, чтобы узнать погоду.")
    return ASK_CITY

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает погоду для указанного города и возвращает её пользователю."""
    city_name = update.message.text
    weather = fetch_weather(city_name)
    
    if weather:
        await update.message.reply_text(f"Погода в {city_name}:\n{weather}\n\nВведите другой город или напишите /cancel для завершения.")
    else:
        await update.message.reply_text(f"Извините, я не смог получить погоду для {city_name}. Пожалуйста, попробуйте снова или напишите /cancel для завершения.")
    
    return ASK_CITY

def fetch_weather(city_name: str) -> str:
    """Получает информацию о погоде с API OpenWeatherMap."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return None

        weather_desc = data["weather"][0]["description"]
        weather_desc = weather_descriptions.get(weather_desc, weather_desc)
        temp = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        
        return f"Описание: {weather_desc}\nТемпература: {temp}°C\nВлажность: {humidity}%\nДавление: {pressure} hPa"
    except Exception as e:
        return None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет и завершает разговор."""
    await update.message.reply_text("Разговор отменен. Вы можете снова узнать погоду, используя /start.")
    return ConversationHandler.END

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    print("Бот запущен!")
    main()
