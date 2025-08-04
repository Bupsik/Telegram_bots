
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import nest_asyncio
import datetime

# Применяем патч для работы с вложенными циклами событий
nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Зойц-бот! Напиши /wassup, чтобы я спросил как дела. Можешь спросить сколько время - /timenow")

async def how_are_you(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как дела?")
    await update.message.reply_photo(photo=open('D:/Telegram_Bot/Balu_Hello.jpg', 'rb'))

async def time_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Получаем текущие дату и время   
    now = datetime.datetime.now()
    today = datetime.datetime.today()
    
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
       
async def main():
    application = Application.builder().token("7360719959:AAFOZDqBoa6KtOJpaSKZriVWN3s69mQ6Xis").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("wassup", how_are_you))
    application.add_handler(CommandHandler("timenow", time_now))
    
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
