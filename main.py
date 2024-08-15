from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, Application
from config import TOKEN, TABLE_NAME, DB_NAME
from table import FinancialTableManager
from db import DatabaseManager
from utils import initialize_database, initialize_table, generate_chart_buffer

table_manager = FinancialTableManager(TABLE_NAME)  # Инициализация менеджера таблиц
db_manager = DatabaseManager(db_path=DB_NAME)  # Инициализация менеджера бд


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало работы"""
    keyboard = [
        [InlineKeyboardButton("Выбрать компанию", callback_data="choose_company")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=reply_markup
    )


async def choose_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора компании, применяет методы менеджера таблиц"""
    companies = table_manager.get_company_names()
    keyboard = [
        [InlineKeyboardButton(company, callback_data=f"company_{company}")]
        for company in companies
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        "Выберите компанию:", reply_markup=reply_markup
    )


async def choose_data_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора типа данных (доход, расход и т.д.)"""
    company = update.callback_query.data.split("_")[1]
    context.user_data["company"] = company
    keyboard = [
        [InlineKeyboardButton("Доход", callback_data="column_Доход")],
        [InlineKeyboardButton("Расход", callback_data="column_Расход")],
        [InlineKeyboardButton("Прибыль", callback_data="column_Прибыль")],
        [InlineKeyboardButton("Налоги", callback_data="column_КПН")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(
        f"Вы выбрали компанию: {company}. Теперь выберите тип данных:",
        reply_markup=reply_markup,
    )


async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка вывода графика с данными"""
    if "company" not in context.user_data:
        # Если компания не выбрана, предложите пользователю выбрать компанию
        keyboard = [
            [InlineKeyboardButton("Выбрать компанию", callback_data="choose_company")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "Сначала выберите компанию:", reply_markup=reply_markup
        )
        return

    company = context.user_data["company"]
    data_type = update.callback_query.data.split("_")[1]

    try:
        data = table_manager.get_company_data(company, data_type)
        buffer = generate_chart_buffer(company, data_type, data)
        message = await update.callback_query.message.reply_photo(buffer)
        db_manager.save_message_data(
            message.chat_id, message.message_id, company, data_type
        )
    except ValueError as e:
        await update.callback_query.message.reply_text(
            f"Ошибка получения данных: {e}. Пожалуйста, попробуйте снова.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Выбрать компанию", callback_data="choose_company"
                        )
                    ]
                ]
            ),
        )


async def check_for_updates(context: ContextTypes.DEFAULT_TYPE):
    """Инициализатор проверки обновления по последним запрошенным данным и обновления графика"""
    data = db_manager.get_message_data()
    if not data:
        return  # Нет данных для обновления

    chat_id, message_id, company, data_type = data

    try:
        new_data = table_manager.get_company_data(company, data_type)
        buffer = generate_chart_buffer(company, data_type, new_data)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        new_message = await context.bot.send_photo(chat_id=chat_id, photo=buffer)
        db_manager.update_message_id(
            chat_id, company, data_type, new_message.message_id
        )
    except ValueError as e:
        # Если произошла ошибка получения данных
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Ошибка обновления данных: {e}. Пожалуйста, проверьте данные и попробуйте снова.",
        )


def main():
    """Создание и запуск бота"""
    # Инициализация базы данных и таблиц
    initialize_database(db_manager)
    initialize_table(table_manager)

    # Создание и запуск бота
    app = Application.builder().token(TOKEN).build()

    job_queue = app.job_queue
    job_queue.run_repeating(
        check_for_updates, interval=60, first=0
    )  # проверяем обновления раз в минуту

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_company, pattern="^choose_company$"))
    app.add_handler(CallbackQueryHandler(choose_data_type, pattern="^company_"))
    app.add_handler(CallbackQueryHandler(show_data, pattern="^column_"))

    app.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
