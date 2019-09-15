import telegram
from datetime import datetime

class Utils:

    @staticmethod
    def getChatId(bot, update):
        chatId = None
        try:
            chatId = update['message']['chat_id']
        except:
            chatId = update['callback_query']['message']['chat']['id']
        return chatId

    @staticmethod
    def getUsername(bot, update):
        chatType = Utils.getChatType(bot, update)
        chatName = 'DESCONHECIDO'
        if chatType == 'private':
            try:
                chatName = update['message']['from_user']['first_name'] + ' '
                if update['message']['from_user']['last_name']: chatName += update['message']['from_user']['last_name']
            except:
                chatName = update['callback_query']['message']['chat']['first_name'] + ' '
                if update['callback_query']['message']['chat']['last_name']: chatName+= update['callback_query']['message']['chat']['last_name']
        elif chatType == 'group':
            return update['callback_query']['message']['chat']['title']
        return chatName

    @staticmethod
    def getUserFirstName(bot, update):
        try:
            return update['callback_query']['from_user']['first_name']
        except:
            return 'parça'
    
    @staticmethod
    def getAdminIds(bot, chatId):
        """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
        return [admin['user']['id'] for admin in bot.get_chat_administrators(chatId)]

    @staticmethod
    def isGroupAdmin(bot, update):
        try:
            if update['message']['from_user']['id']:
                return True
        except:
            if update['callback_query']['from_user']['id'] in Utils.getAdminIds(bot, update['callback_query']['message']['chat']['id']):
                return True
        return False

    @staticmethod
    def getChatType(bot, update):
        return update['callback_query']['message']['chat']['type']

    @staticmethod
    def getWeekNumber():
        return datetime.today().isocalendar()[1]

    @staticmethod
    def getPeriodFormated(period):
        if(period == 'daily'):
            return 'Diário'
        return 'Semanal'

    @staticmethod
    def getCampusFormated(campus):
        if(campus == 'chapeco'):
            return 'Chapecó'
        if(campus == 'cerro-largo'):
            return 'Cerro Largo'
        if(campus == 'erechim'):
            return 'Erechim'
        if(campus == 'laranjeiras-do-sul'):
            return 'Laranjeiras do Sul'
        if(campus == 'realeza'):
            return 'Realeza'

    @staticmethod
    def showStartMenu(bot, update):
        bot.send_message(
            chat_id = Utils.getChatId(bot, update),
            text = '*\nSelecione uma opção para continuar...*',
            parse_mode = 'Markdown',
            reply_markup = Utils.getMainMenuMarkup()
        )

    @staticmethod
    def showStartMenuInExistingMsg(bot, update):
        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = '*Olá!\nSelecione uma opção para continuar...*',
            parse_mode = 'Markdown',
            reply_markup = Utils.getMainMenuMarkup()
        )

    @staticmethod
    def getMainMenuMarkup():
        keyboard = [
            [
                telegram.InlineKeyboardButton('Cardápio RU', callback_data = 'menu-ru'),
                telegram.InlineKeyboardButton('Cardápio Cantina', callback_data = 'menu-canteen')
            ],
            [
                telegram.InlineKeyboardButton('Horário ônibus', callback_data = 'bus-schedules'),
                telegram.InlineKeyboardButton('Calendário acadêmico', callback_data = 'academic-calendar')
            ],
            [
                telegram.InlineKeyboardButton('Próximos Eventos', callback_data = 'events-schedules'),
                telegram.InlineKeyboardButton('Datas Importantes', callback_data = 'academic-date')
            ],
            [
                telegram.InlineKeyboardButton('Cardápio Automático', callback_data = 'auto-menu')
            ]
        ]
        return telegram.InlineKeyboardMarkup(keyboard)