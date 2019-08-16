import os
from telegram.ext import Updater, CommandHandler
import config
import RuBot

def showStartMenu(bot, update):
    msgToSend = 'Olá!\nExecute um dos comandos abaixo para continuar:\n/cardapio - Mostra o cardápio do dia'
    bot.sendMessage(update.message.chat_id, msgToSend)

def main():
    ruBot = RuBot.RuBot()

    updater = Updater(os.environ['telegramToken'])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', showStartMenu))
    dp.add_handler(CommandHandler('cardapio', ruBot.showCardapio))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()