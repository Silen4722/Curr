from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    Application
)

TOKEN = "7652644354:AAFoamIjw_7YU8jH9ypBfklCOHQqG-gLlyE"

# Курсы обмена
UAH_TO_RUB = 1.7  # 1 гривна = 1.7 рубля
RUB_TO_UAH = 2.4  # 1 рубль = 2.4 гривны

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Гривны → Рубли", callback_data='uah_rub')],
        [InlineKeyboardButton("Рубли → Гривны", callback_data='rub_uah')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔹 Выберите направление обмена:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'uah_rub':
        await query.edit_message_text(
            f"<b>Гривны → Рубли</b>\n"
            f"Курс: 1 гривна = {UAH_TO_RUB}₽\n\n"
            "Введите сумму в гривнах:",
            parse_mode="HTML"
        )
        context.user_data['mode'] = 'uah_rub'

    elif query.data == 'rub_uah':
        await query.edit_message_text(
            f"<b>Рубли → Гривны</b>\n"
            f"Курс: 1 рубль = {RUB_TO_UAH}₴\n\n"
            "Введите сумму в рублях:",
            parse_mode="HTML"
        )
        context.user_data['mode'] = 'rub_uah'

async def handle_message(update: Update, context: CallbackContext):
    if 'mode' not in context.user_data:
        return await start(update, context)

    try:
        amount = float(update.message.text)
        if amount <= 0:
            raise ValueError

        if context.user_data['mode'] == 'uah_rub':
            result = amount * UAH_TO_RUB
            await update.message.reply_text(
                f"💵 <b>{amount}₴ → {result:.2f}₽</b>",
                parse_mode="HTML"
            )
        elif context.user_data['mode'] == 'rub_uah':
            result = amount * RUB_TO_UAH
            await update.message.reply_text(
                f"💵 <b>{amount}₽ → {result:.2f}₴</b>",
                parse_mode="HTML"
            )

        # Возвращаем меню
        await start(update, context)

    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите корректную сумму (число больше 0).")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
