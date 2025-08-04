
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import nest_asyncio
from datetime import datetime, timedelta
import requests

# Применяем патч для работы с вложенными циклами событий
nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Зойц-бот! Напиши /wassup, чтобы я спросил как дела. Можешь спросить сколько время - /timenow !Если хочешь узнать погоду на завтра, нажми /pogoda")

async def how_are_you(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как дела?")
    await update.message.reply_photo(photo=open('D:/Telegram_Bot/Balu_Hello.jpg', 'rb'))

async def time_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Получаем текущие дату и время   
    now = datetime.now()
    today = datetime.today()
    
        # Форматируем вывод
    time_str = now.strftime("%H:%M:%S")
    date_str = today.strftime("%d.%m.%Y")
    weekday_str = now.strftime("%A")
    
    # Отправляем сообщение
    message = (
        f"📅 Дата: {date_str}\n"
        f"🕒 Время: {time_str}\n"
        f"📌 День недели: {weekday_str}"
        )
    
    await update.message.reply_text(message)


# Конфигурация для Яндекс.Погоды
YANDEX_API_URL = "https://api.weather.yandex.ru/v2/forecast"
YANDEX_API_KEY = "861e91e6-8736-4fc6-902c-84435c909dc2"  # Получите на https://yandex.ru/dev/weather/
MOSCOW_COORDS = {"lat": 55.7558, "lon": 37.6173}  # Координаты Москвы

async def pogoda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        forecast = get_yandex_forecast()
        
        message = (
            f"🌤️ <b>Прогноз погоды в Москве на завтра</b>\n (По данным Яндекс.Погода)\n\n"
            f"📅 <b>{forecast['date']}</b>\n"
            f"🌡 Температура: от {forecast['temp_min']}°C до {forecast['temp_max']}°C\n"
            f"💧 Влажность: {forecast['humidity']}%\n"
            f"🌬 Ветер: {forecast['wind_speed']} м/с, {forecast['wind_dir']}\n"
            f"☁ Облачность: {forecast['clouds']}\n"
            f"🌧 Осадки: {forecast['precipitation']}\n"
            f"📝 {forecast['description']}"
        )
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

def get_yandex_forecast():
    headers = {"X-Yandex-API-Key": YANDEX_API_KEY}
    params = {
        "lat": MOSCOW_COORDS["lat"],
        "lon": MOSCOW_COORDS["lon"],
        "lang": "ru_RU",
        "limit": 2  # Сегодня и завтра
    }
    
    response = requests.get(YANDEX_API_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}")
    
    data = response.json()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    
    day_forecast = data["forecasts"][1]
    day_part = day_forecast["parts"]["day"]
    
    return {
        'date': tomorrow,
        'temp_min': int(day_part["temp_min"]),
        'temp_max': int(day_part["temp_max"]),
        'humidity': int(day_part["humidity"]),
        'wind_speed': round(float(day_part["wind_speed"]), 1),
        'wind_dir': get_wind_direction(day_part["wind_dir"]),
        'clouds': get_clouds_description(day_part["cloudness"]),
        'precipitation': get_precipitation(day_forecast),
        'description': str(day_part["condition"]).capitalize()
    }

def get_wind_direction(degrees):
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    try:
        return directions[round(float(degrees) / 45) % 8]
    except:
        return ""
    
def get_clouds_description(cloudness):
    try:
        # Преобразуем в число, если это строка
        cloudness = float(cloudness) if isinstance(cloudness, str) else cloudness
        percentage = round(cloudness * 100)  # cloudness обычно от 0.0 до 1.0
        
        if percentage <= 10:
            return "Ясно"
        elif percentage <= 30:
            return "Малооблачно"
        elif percentage <= 70:
            return "Облачно"
        else:
            return "Пасмурно"
    except (TypeError, ValueError):
        return "Облачность неизвестна"

def get_precipitation(forecast):
    try:
        prec_type = forecast["parts"]["day"].get("prec_type", "")
        prec_strength = forecast["parts"]["day"].get("prec_strength", 0)
        
        # Преобразуем в число, если это строка
        if isinstance(prec_strength, str):
            prec_strength = float(prec_strength)
        
        prec_types = {
            "rain": "дождь",
            "snow": "снег",
            "sleet": "мокрый снег",
            "": "нет"
        }
        
        prec_intensity = {
            0: "",
            0.25: "слабый ",
            0.5: "умеренный ",
            0.75: "сильный ",
            1: "очень сильный "
        }.get(prec_strength, "")
        
        return f"{prec_intensity}{prec_types.get(prec_type, '')}" or "Нет осадков"
    except Exception:
        return "Нет данных об осадках"
       
async def main():
    with open('TG_API_key.txt', 'r') as file:
        API_key = file.read().strip() 
    application = Application.builder().token(API_key).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("wassup", how_are_you))
    application.add_handler(CommandHandler("timenow", time_now))
    application.add_handler(CommandHandler("pogoda", pogoda))
    
    # Создаем отдельную задачу для бота
    bot_task = asyncio.create_task(application.run_polling())
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await application.stop()
        await bot_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
       print("Бот остановлен")
