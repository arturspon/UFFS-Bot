import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram
from Utils import Utils
import RuBot, BusBot, CalendarBot, CanteenBot, EventsBot, DateBot, DatabaseConnection
from conf.settings import telegramToken
import threading

ruBot = RuBot.RuBot()
canteenBot = CanteenBot.CanteenBot()
busBot = BusBot.BusBot()
calendarBot = CalendarBot.CalendarBot()
eventsBot = EventsBot.EventsBot()
dateBot = DateBot.DateBot()
databaseConnection = DatabaseConnection.DatabaseConnection()

def callHandler(bot, update):
    chatType = Utils.getChatType(bot, update)
    if((chatType == 'group' or chatType == 'supergroup') and not Utils.isGroupAdmin(bot, update)):
        bot.send_message(
            chat_id = Utils.getChatId(bot, update),
            text = 'Desculpe, somente admins deste grupo podem usar o bot. Para utilizar o bot, inicie uma conversa privada com @UFFS_Bot'
        )
        return

    if update.callback_query.data == 'menu-ru':
        ruBot.selectCampus(bot, update)

    elif update.callback_query.data[:2] == 'RU':
        ruBot.showCardapio(bot, update, update.callback_query.data[3:])

    elif update.callback_query.data == 'unsub':
        ruBot.unsubToPeriodicMenu(bot, update)

    elif update.callback_query.data[:4] == 'AUTO':
        ruBot.subToPeriodicMenu(bot, update, update.callback_query.data)

    elif update.callback_query.data == 'auto-menu':
        ruBot.selectPeriod(bot, update)

    elif update.callback_query.data == 'daily':
        ruBot.selectCampusAuto(bot, update, 'daily')

    elif update.callback_query.data == 'weekly':
        ruBot.selectCampusAuto(bot, update, 'weekly')

    elif update.callback_query.data == 'menu-canteen':
        canteenBot.selectCampus(bot, update)

    elif update.callback_query.data[:7] == 'canteen':
        canteenBot.showCardapio(bot, update)

    elif update.callback_query.data == 'bus-schedules':
        busBot.selectCampus(bot, update)

    elif update.callback_query.data[:3] == 'bus':
        busBot.selectStartPoint(bot, update, update.callback_query.data[4:])

    elif update.callback_query.data[:13] == 'startPointBus':
        busBot.showSchedule(bot, update, update.callback_query.data[14:])

    elif update.callback_query.data == 'academic-calendar':
        calendarBot.getCalendar(bot, update)
    elif update.callback_query.data == 'events-schedules':
        eventsBot.showEvents(bot, update)


    elif update.callback_query.data == 'academic-date':
        dateBot.selectTerm(bot, update)
    elif update.callback_query.data[:4] == 'date':
        dateBot.searchTerm(bot, update, update.callback_query.data[5:])


    elif update.callback_query.data == 'main-menu':
        Utils.showStartMenuInExistingMsg(bot, update)

def downloadNeededFiles():
    calendarBot.downloadCalendar()

def main():
    downloadNeededFiles()
    databaseConnection.createTables()

    bot =  telegram.Bot(telegramToken)
    updater = Updater(bot=bot)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', Utils.showStartMenu))
    dp.add_handler(CommandHandler('auto', ruBot.subToPeriodicMenu))
    dp.add_handler(CommandHandler('autoCancel', ruBot.unsubToPeriodicMenu))
    dp.add_handler(CallbackQueryHandler(callHandler))
    thread = threading.Thread(target = ruBot.sendMenuPeriodically, args = (bot,))
    thread.start()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()