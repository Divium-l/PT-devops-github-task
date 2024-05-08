import dotenv, os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from regex_search import find_email, find_phone
from regex_verify import verify_password
from pt_logger import logger
import pt_linux_monitoring as plm
import db_access as dba
from init_db import init_db

dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f'Привет {user.full_name}!')
    
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

async def helpCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
"""
*Доступные команды:*

`help` \- Показать это сообщение
`find_email` \- Поиск Email адреса
`find_phone_number` \- Поиск номера телефона
    Поддерживаемые форматы:
        • 8XXXXXXXXXX
        • 8\(XXX\)XXXXXXX
        • 8 XXX XXX XX XX 
        • 8 \(XXX\) XXX XX XX
        • 8\-XXX\-XXX\-XX\-XX
`verify_password` \- Проверка пароля на простоту
    Требования к паролю:
        • не менее восьми символов
        • как минимум одна заглавная буква \(A\-Z\)
        • хотя бы одна строчная буква \(a\-z\)
        • хотя бы одна цифра \(0\-9\)
        • хотя бы один специальный символ \!@\#$%^&\*\(\)
`get_emails` \- Показать сохранённые адреса
`get_phone_numbers` \- Показать сохранённые телефоны

*Мониторинг Linux\-системы*
`get_release` \- О релизе
`get_uname` \- Об архитектуры процессора, имени хоста системы и версии ядра 
`get_uptime` \- О времени работы
`get_df` \- Сбор информации о состоянии файловой системы
`get_free` \- Сбор информации о состоянии оперативной памяти
`get_mpstat` \- Сбор информации о производительности системы
`get_w` \- Сбор информации о работающих в данной системе пользователях
`get_auths` \- Последние 10 входов в систему
`get_critical` \- Последние 5 критических события
`get_ps` \- Сбор информации о запущенных процессах
`get_ss` \- Сбор информации об используемых портах
`get_apt_list` \<пакет\> \- Сбор информации об установленных пакетах, если \<пакет\> не указан, будут выведены все пакеты
`get_services` \- Сбор информации о запущенных сервисах
`get_repl_logs` \- Вывод информации о репликации
""", parse_mode='MarkdownV2')

async def findEmailCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите текст для поиска Email-адресов: ')

    return 'findEmailAddresses'

async def findPhoneNumbersCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

async def findEmailsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите текст для поиска Email адресов: ')
    return 'findEmails'

async def verifyPasswordCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите пароль для оценки: ')
    return 'verifyPassword'

async def findPhoneNumbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userInput = update.message.text

    foundPhones = find_phone(userInput)

    if (foundPhones == None):
        await update.message.reply_text('Номера не найдены')
        return ConversationHandler.END
    else:
        context.user_data["phones"] = foundPhones
        phonesString = ""
        for i in range(len(foundPhones)):
            phonesString += f"{i + 1}: {foundPhones[i]}\n"
        await update.message.reply_text(phonesString)
        await update.message.reply_text("Сохранить запись? (Да/нет)")

    return "savePhone"

async def findEmails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userInput = update.message.text

    foundEmails = find_email(userInput)

    if (foundEmails == None):
        await update.message.reply_text('Email адреса не найдены')
        return ConversationHandler.END
    else:
        context.user_data["emails"] = foundEmails
        emailsString = ""
        for i in range(len(foundEmails)):
            emailsString += f"{i + 1}: {foundEmails[i]}\n"
        await update.message.reply_text(emailsString)
        await update.message.reply_text("Сохранить запись? (Да/нет)")

    return "saveEmail"

async def saveEmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userInput = update.message.text

    if (userInput.lower() == "да"):
        emails = context.user_data["emails"]
        dba.save_emails(emails)
        await update.message.reply_text("Данные сохранены")
    elif (userInput.lower() == "нет"):
        context.user_data["emails"] = None
    else:
        await update.message.reply_text("Формат ответа: да/нет")
        return "saveEmail"
    
    context.user_data["emails"] = None
    return ConversationHandler.END

async def savePhone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userInput = update.message.text

    if (userInput.lower() == "да"):
        phones = context.user_data["phones"]
        dba.save_phone_numbers(phones)
        await update.message.reply_text("Данные сохранены")
    elif (userInput.lower() == "нет"):
        context.user_data["phones"] = None
    else:
        await update.message.reply_text("Формат ответа: да/нет")
        return "savePhone"
    
    context.user_data["phones"] = None
    return ConversationHandler.END

async def verifyPassword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userInput = update.message.text

    if (verify_password(userInput)):
        await update.message.reply_text('Пароль сложный')
    else:
        await update.message.reply_text('Пароль простой')

    return ConversationHandler.END

async def getReleaseCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_release()
    await update.message.reply_text(result)

async def getUnameCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_uname()
    await update.message.reply_text(result)

async def getUptimeCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_uptime()
    await update.message.reply_text(result)

async def getDfCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_df()
    await update.message.reply_text(result)

async def getFreeCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_free()
    await update.message.reply_text(result)

async def getMpstatCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_mpstat()
    await update.message.reply_text(result)

async def getWCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_w()
    await update.message.reply_text(result)

async def getAuthsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_auths()
    await update.message.reply_text(result)

async def getCriticalCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_critical()
    await update.message.reply_text(result)

async def getPsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_ps()
    await update.message.reply_text(result)

async def getSsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_ss()
    await update.message.reply_text(result)

async def getAptListCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    packageName = ""
    try:
        packageName = context.args[0]
    except:
        pass

    result = plm.get_apt_list(packageName)
    await update.message.reply_text(result)

async def getServicesCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_services()
    await update.message.reply_text(result)

async def getReplLogsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = plm.get_repl_logs()
    await update.message.reply_text(result)

async def getEmailsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = dba.get_emails()
    await update.message.reply_text(result)

async def getPhoneNumbersCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = dba.get_phone_numbers()
    await update.message.reply_text(result)

def main():
    logger.info("Starting bot setup")
    init_db()
	# Создайте программу обновлений и передайте ей токен вашего бота
    application = Application.builder().token(BOT_TOKEN).build()
	
    # Обработчики диалогов
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(filters.TEXT & ~filters.COMMAND, findPhoneNumbers)],
            'savePhone': [MessageHandler(filters.TEXT & ~filters.COMMAND, savePhone)],
        },
        fallbacks=[]
    )

    convHandlerFindEmailAddresses = ConversationHandler(
        entry_points=[CommandHandler("find_email", findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(filters.TEXT & ~filters.COMMAND, findEmails)],
            'saveEmail': [MessageHandler(filters.TEXT & ~filters.COMMAND, saveEmail)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler("verify_password", verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(filters.TEXT & ~filters.COMMAND, verifyPassword)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helpCommand))
    application.add_handler(CommandHandler("get_release", getReleaseCommand))
    application.add_handler(CommandHandler("get_uname", getUnameCommand))
    application.add_handler(CommandHandler("get_uptime", getUptimeCommand))
    application.add_handler(CommandHandler("get_df", getDfCommand))
    application.add_handler(CommandHandler("get_free", getFreeCommand))
    application.add_handler(CommandHandler("get_mpstat", getMpstatCommand))
    application.add_handler(CommandHandler("get_w", getWCommand))
    application.add_handler(CommandHandler("get_auths", getAuthsCommand))
    application.add_handler(CommandHandler("get_critical", getCriticalCommand))
    application.add_handler(CommandHandler("get_ps", getPsCommand))
    application.add_handler(CommandHandler("get_ss", getSsCommand))
    application.add_handler(CommandHandler("get_apt_list", getAptListCommand))
    application.add_handler(CommandHandler("get_services", getServicesCommand))
    application.add_handler(CommandHandler("get_repl_logs", getReplLogsCommand))
    application.add_handler(CommandHandler("get_emails", getEmailsCommand))
    application.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbersCommand))
    application.add_handler(convHandlerFindPhoneNumbers)
    application.add_handler(convHandlerFindEmailAddresses)
    application.add_handler(convHandlerVerifyPassword)

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
		
	# Запускаем бота пока не нажмём Ctrl+C
    logger.info("Setup comlete, launching bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()