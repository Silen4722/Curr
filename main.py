from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters
)
import re

TOKEN = "7652644354:AAFoamIjw_7YU8jH9ypBfklCOHQqG-gLlyE"

# Курсы обмена
UAH_TO_RUB = 1.7  # 1 гривна = 1.7 рубля
RUB_TO_UAH = 2.4  # 1 рубль = 2.4 гривны

def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("Гривны → Рубли", callback_data='uah_rub')],
        [InlineKeyboardButton("Рубли → Гривны", callback_data='rub_uah')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🔹 Выберите направление обмена или введите запрос:\n"
        "• <code>1000 рублей в гривны</code>\n"
        "• <code>500 гривен в рубли</code>",
        reply_markup=get_keyboard(),
        parse_mode="HTML"
    )

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'uah_rub':
        await query.edit_message_text(
            "Введите сумму в гривнах:",
            reply_markup=get_keyboard()
        )
        context.user_data['mode'] = 'uah_rub'
    elif query.data == 'rub_uah':
        await query.edit_message_text(
            "Введите сумму в рублях:",
            reply_markup=get_keyboard()
        )
        context.user_data['mode'] = 'rub_uah'

async def handle_text_request(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    
    amount_match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
    if not amount_match:
        await update.message.reply_text(
            "❌ Не вижу сумму для обмена. Пример: <i>100 рублей в гривны</i>",
            parse_mode="HTML",
            reply_markup=get_keyboard()
        )
        return
    
    amount = float(amount_match.group(1))
    
    # Определяем направление конвертации
    if any(word in text for word in ["рубл", "р.", "р ", "₽"]):
        if any(word in text for word in ["в грн", "в грив", "грн", "грив", "₴"]):
            # RUB → UAH
            result = amount * RUB_TO_UAH
            await update.message.reply_text(
                f"💸 <b>{amount}₽ → {result:.2f}₴</b>\n"
                f"Курс: 1 рубль = {RUB_TO_UAH}₴",
                parse_mode="HTML",
                reply_markup=get_keyboard()
            )
        else:
            await update.message.reply_text(
                "Укажите валюту для конвертации. Пример: '100 рублей в гривны'",
                reply_markup=get_keyboard()
            )
    elif any(word in text for word in ["грив", "грн", "₴"]):
        if any(word in text for word in ["в руб", "в рубл", "рубл", "р.", "р ", "₽"]):
            # UAH → RUB
            result = amount * UAH_TO_RUB
            await update.message.reply_text(
                f"💸 <b>{amount}₴ → {result:.2f}₽</b>\n"
                f"Курс: 1 гривна = {UAH_TO_RUB}₽",
                parse_mode="HTML",
                reply_markup=get_keyboard()
            )
        else:
            # UAH → RUB по умолчанию
            result = amount * UAH_TO_RUB
            await update.message.reply_text(
                f"💸 <b>{amount}₴ → {result:.2f}₽</b>\n"
                f"Курс: 1 гривна = {UAH_TO_RUB}₽",
                parse_mode="HTML",
                reply_markup=get_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Не понимаю валюту. Используйте 'гривны' или 'рубли'",
            parse_mode="HTML",
            reply_markup=get_keyboard()
        )

async def handle_message(update: Update, context: CallbackContext):
    if 'mode' in context.user_data:
        try:
            amount = float(update.message.text.replace(',', '.'))
            if amount <= 0:
                raise ValueError
                
            if context.user_data['mode'] == 'uah_rub':
                result = amount * UAH_TO_RUB
                await update.message.reply_text(
                    f"💵 <b>{amount}₴ → {result:.2f}₽</b>\n"
                    f"Курс: 1 гривна = {UAH_TO_RUB}₽",
                    parse_mode="HTML",
                    reply_markup=get_keyboard()
                )
            elif context.user_data['mode'] == 'rub_uah':
                result = amount * RUB_TO_UAH
                await update.message.reply_text(
                    f"💵 <b>{amount}₽ → {result:.2f}₴</b>\n"
                    f"Курс: 1 рубль = {RUB_TO_UAH}₴",
                    parse_mode="HTML",
                    reply_markup=get_keyboard()
                )
                
            context.user_data.pop('mode', None)
            
        except ValueError:
            await update.message.reply_text(
                "❌ Ошибка! Введите число больше 0.",
                reply_markup=get_keyboard()
            )
    else:
        await handle_text_request(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
