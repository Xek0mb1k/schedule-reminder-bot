import configparser

import openpyxl.worksheet.worksheet
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
from openpyxl import load_workbook
from datetime import datetime
import requests
from urllib.parse import urlencode
import sheet_reader

employee_queue = []
reminder_time = "21:40"
job_queue: JobQueue = None


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('HI, Im work')


async def download_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START DOWNLOADING")

    file = await context.bot.get_file(update.message.document)
    await file.download_to_drive('sheet.xlsx')
    await update.message.reply_text(f'Downloading completed')


async def set_reminders(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    global employee_queue
    global reminder_time
    global job_queue

    # loading data from excel
    wb = load_workbook("sheet.xlsx", read_only=True)
    ws = wb.active

    current_time = datetime.now()
    employee_queue = sheet_reader.update_employee_queue(ws)

    await job_queue.stop()

    alarm_hour, alarm_minute = map(int, reminder_time.split(':'))
    reminder_datetime = datetime(current_time.year, current_time.month, current_time.day, 0, 0)
    for day in range(current_time.day, len(employee_queue)):
        print(day)

        if len(employee_queue[day]) != 0:
            remind_day = datetime(current_time.year, current_time.month, day, alarm_hour, alarm_minute)
            print("time remeaning: " + str((remind_day.timestamp() - reminder_datetime.timestamp())))
            job_queue.run_once(remind, chat_id=update.message.chat_id, when=remind_day.timestamp() - reminder_datetime.timestamp())
    print(employee_queue)
    await job_queue.start()
    await update.message.reply_text(f'Напоминалки установлены')


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Завтра работают... ' + '\n'.join(employee_queue[datetime.now().day]))


async def who_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if datetime.now().day <= len(employee_queue):
        await update.message.reply_text('Завтра работают: \n' + '\n'.join(employee_queue[datetime.now().day]))
    else:
        await update.message.reply_text('Ошибка. Время обновить таблицу')


# This function downloading actual sheet from YA disk
def update_sheet():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.ru/i/3FM22sG-FKwjZQ'  # Here your ya.disk link

    # Take download link
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    # Load and save file
    download_response = requests.get(download_url)
    with open('sheet.xlsx', 'wb') as f:
        f.write(download_response.content)


async def download_actual_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_sheet()
    await update.message.reply_text('Sheet downloaded')


def main():
    global job_queue

    now = datetime.now()
    print(now)



    # reading configs
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['General']['token']

    app = ApplicationBuilder().token(token).build()
    job_queue = app.job_queue
    # job_queue.run_once(callback=test_func, when=5)

    app.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), download_sheet))

    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("set", set_reminders))
    app.add_handler(CommandHandler("tomorrow", who_tomorrow))
    app.add_handler(CommandHandler("download", download_actual_sheet))

    app.debug = True  # TODO('delete this in future')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
