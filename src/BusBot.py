import telegram

class BusBot:
    assetFolderPath = 'assets/BusBot/'
    scheduleFiles = {
        'cco': 'scheduleCCO.txt'
    }
    schedules = {}

    def __init__(self):
        self.loadSchedules()

    def loadSchedules(self):
        for city, fileName in self.scheduleFiles.items():
            file = open(self.assetFolderPath + fileName, 'r')
            results = {
                'week': {
                    'terminal': [],
                    'uffs': []
                },
                'sat': {
                    'terminal': [],
                    'uffs': []
                }
            }

            isWeek = None
            fromTerminal = None
            for line in file:
                line = line.rstrip("\n\r")
                if line == 'semana':
                    isWeek = True
                    fromTerminal = None
                    continue
                if line == 'sabado':
                    isWeek = False
                    fromTerminal = None
                    continue
                if line == 'terminal':
                    fromTerminal = True
                    continue
                if line == 'uffs':
                    fromTerminal = False
                    continue
                
                if isWeek is not None and fromTerminal is not None and line:
                    if isWeek:
                        if fromTerminal:
                            results['week']['terminal'].append(str(line))
                        else:
                            results['week']['uffs'].append(str(line))
                    else:
                        if fromTerminal:
                            results['sat']['terminal'].append(str(line))
                        else:
                            results['sat']['uffs'].append(str(line))


        self.schedules[city] = results

    def selectCampus(self, bot, update):
        keyboard = [[telegram.InlineKeyboardButton('RU Chapecó', callback_data = 'bus-cco'),
                telegram.InlineKeyboardButton('RU Cerro Largo', callback_data = 'bus-cerro'),
                telegram.InlineKeyboardButton('RU Erechim', callback_data = 'bus-erechim')],
                [telegram.InlineKeyboardButton('RU Laranjeiras', callback_data = 'bus-laranjeiras'),
                telegram.InlineKeyboardButton('RU Passo Fundo', callback_data = 'bus-passofundo'),
                telegram.InlineKeyboardButton('RU Realeza', callback_data = 'bus-realeza')]]
        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = 'Selecione o campus:',
            parse_mode = 'HTML',
            reply_markup = replyMarkup
        )

    def selectStartPoint(self, bot, update, city):
        keyboard = [[telegram.InlineKeyboardButton('Terminal', callback_data = 'startPointBus-terminal-' + city),
                telegram.InlineKeyboardButton('UFFS', callback_data = 'startPointBus-uffs-' + city)]]
        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = 'Selecione o ponto de partida:',
            parse_mode = 'HTML',
            reply_markup = replyMarkup
        )

    def showSchedule(self, bot, update, startPointAndCity):
        try:
            startPointAndCity = startPointAndCity.split('-')
            startPoint = startPointAndCity[0]
            city = startPointAndCity[1]
            bot.send_message(
                chat_id = update.callback_query.message.chat.id,
                text = self.formatSchedule(self.schedules[city]['week'][startPoint])
            )
        except Exception as err:
            print(err)

    def formatSchedule(self, scheduleList):
        formattedText = 'Os horários de saída dos ônibus são:\n'
        for schedule in scheduleList:
            formattedText += schedule + ', '         
        return formattedText[:-2] + '.\n'