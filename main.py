import configparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openpyxl import load_workbook
from datetime import datetime



async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def download(update, context):
    print("START DOWNLOADING")
    
    file = await context.bot.get_file(update.message.document)
    await file.download_to_drive('sheet.xlsx')    
    await update.message.reply_text(f'Unloading completed')





# def reminder(update: Update, context: CallbackContext) -> None:
#     chat_id = update.message.chat_id
#     current_date = datetime.now().date()

#     for row in ws.iter_rows(values_only=True):
#         day, user_id, message = row
#         if current_date == day and user_id == chat_id:
#             context.bot.send_message(chat_id=chat_id, text=message)

def main():
    # loading data from excel
    wb = load_workbook('sheet.xlsx')
    ws = wb.active 


    # reading configs
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['General']['token']


    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), download))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()