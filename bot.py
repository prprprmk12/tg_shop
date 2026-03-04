import logging
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "8563046569:AAEkrRrEx6sy0tVi1R6C2lnEs9djThWHeDY"
WEBAPP_URL = "https://tgshop1.streamlit.app/" # например, https://xyz.streamlit.app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Кнопка открытия Mini App
    kb = [[KeyboardButton(text="🚀 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        "Привет! Нажми на кнопку ниже, чтобы зайти в магазин:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем данные из Mini App (из функции tg.sendData)
    raw_data = update.effective_message.web_app_data.data
    order = json.loads(raw_data)
    
    msg = (
        f"💰 **Оплата прошла успешно!**\n\n"
        f"📦 **Товары:** {order['items']}\n"
        f"💵 **Сумма:** {order['total']:,} ₽\n\n"
        f"Менеджер скоро свяжется с вами."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_payment))
    
    print("Бот запущен...")
    app.run_polling()
