import configparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from openpyxl import load_workbook
from datetime import datetime
import requests
from urllib.parse import urlencode

import logging





counter = 0
async def test_func(context: ContextTypes.DEFAULT_TYPE) -> None:
    global counter
    counter+=1
    print("HELLO ", counter)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def download(update, context):
    print("START DOWNLOADING")
    
    file = await context.bot.get_file(update.message.document)
    await file.download_to_drive('sheet.xlsx')    
    await update.message.reply_text(f'Downloading completed')


def alarm(update, job):
       update.send_message(chat_id=update.message.chat_id, text='ALARM! Wake up!')

def set_alarm(update, context):
       current_time = datetime.datetime.now()
       alarm_time = context.args[0]
       
       if len(alarm_time) != 5 or not alarm_time[2].isdigit():
           update.message.reply_text('Please enter a valid time in HH:MM format.')
           return

       alarm_hour, alarm_minute = map(int, alarm_time.split(':'))
       alarm_datetime = datetime.datetime(current_time.year, current_time.month, current_time.day, alarm_hour, alarm_minute)

       job_queue = context.job_queue
       job_queue.run_once(alarm, alarm_datetime.timestamp() - time.time())

       update.message.reply_text(f'Alarm set for {alarm_time}')


def who_tomorrow(update, context):
    update.message.reply_text('Tommoros is: ')

reminder_time = "21:40"
async def set_reminder_time(update, context):
    global reminder_time
    
    await update.message.reply_text('Write reminder time in format HH:MM')
    reminder_time_tmp = update.message.text
    if len(reminder_time_tmp) != 5 or reminder_time_tmp[2] != ":":
        await update.message.reply_text('Invalid time format. Please try again.')
        return 
    try:
        hours = int(reminder_time_tmp[:2])
        minutes = int(reminder_time_tmp[3:])
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            await update.message.reply_text('Invalid time. Please try again.')
            return
    except:
        await update.message.reply_text('Invalid input. Please try again.')
        return
    reminder_time = reminder_time_tmp
    print(reminder_time_tmp)
    return ConversationHandler.END

def cancel():
    pass
# def reminder(update: Update, context: CallbackContext) -> None:
#     chat_id = update.message.chat_id
#     current_date = datetime.now().date()

#     for row in ws.iter_rows(values_only=True):
#         day, user_id, message = row
#         if current_date == day and user_id == chat_id:
#             context.bot.send_message(chat_id=chat_id, text=message)
async def init(update, context):
    await update.message.reply_text('INPUT')
    return 1

def updateSheet():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.ru/i/3FM22sG-FKwjZQ'  # Here your ya.disk link

    # Take download link
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    # Load and save file
    download_response = requests.get(download_url)
    with open('downloaded_file.xlsx', 'wb') as f:   # Здесь укажите нужный путь к файлу
        f.write(download_response.content)

def main():
    now = datetime.now()
    print(now)

    # loading data from excel
    wb = load_workbook('sheet.xlsx')
    ws = wb.active


    # reading configs
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['General']['token']

    app = ApplicationBuilder().token(token).build()
    job_queue = app.job_queue
    

    
    job_queue.run_once(callback=test_func, when=5)
    


    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), download))
    app.add_handler(CommandHandler("tommorrow", who_tomorrow))
    
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("set", init)],
    states={
        1: [MessageHandler(filters.Text, set_reminder_time)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]

)
    app.add_handler(conv_handler)



    app.debug = True
    app.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == '__main__':
    main()