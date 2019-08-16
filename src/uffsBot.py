import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram
import config
import RuBot, BusBot

ruBot = RuBot.RuBot()
busBot = BusBot.BusBot()

def showStartMenu(bot, update):
    msgToSend = 'Olá!\nSelecione uma opção para continuar...'

    keyboard = [[telegram.InlineKeyboardButton('Cardápio RU', callback_data='cardapio-ru'),
                 telegram.InlineKeyboardButton('Horário ônibus', callback_data='onibus')]]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.message.chat_id,
                     text=msgToSend,
                     reply_markup=reply_markup)

def callHandler(bot, update):
    if update.callback_query.data == 'cardapio-ru':
        ruBot.showCardapio(bot, update)
    elif update.callback_query.data == 'onibus':
        pass

def main():
    updater = Updater(os.environ['telegramToken'])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', showStartMenu))
    dp.add_handler(CommandHandler('cardapio', ruBot.showCardapio))
    dp.add_handler(CallbackQueryHandler(callHandler))
    updater.start_polling()
    updater.idle()    

if __name__ == '__main__':
    main()