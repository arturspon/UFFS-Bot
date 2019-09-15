import telegram

class BusBot:
    assetFolderPath = 'assets/BusBot/'
    scheduleFiles = {
        'cco': 'scheduleCCO.txt',
        'cerro': 'scheduleCL.txt',
        'erechim': 'scheduleERE.txt'
    }
    schedules = {}

    citiesFullName = {
        'cco': 'Chapecó',
        'cerro': 'Cerro Largo',
        'erechim': 'Erechim',
        'laranjeiras': 'Laranjeiras do Sul',
        'passofundo': 'Passo Fundo',
        'realeza': 'Realeza'
    }

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
                line = line.strip()
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
        keyboard = [
            [
                telegram.InlineKeyboardButton('Campus Chapecó', callback_data = 'bus-cco'),
                telegram.InlineKeyboardButton('Campus Cerro Largo', callback_data = 'bus-cerro')
            ],
            [
                telegram.InlineKeyboardButton('Campus Erechim', callback_data = 'bus-erechim'),
                telegram.InlineKeyboardButton('Campus Laranjeiras', callback_data = 'bus-laranjeiras')
            ],
            [
                telegram.InlineKeyboardButton('Campus Passo Fundo', callback_data = 'bus-passofundo'),
                telegram.InlineKeyboardButton('Campus Realeza', callback_data = 'bus-realeza')
            ],
            [
                telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
            ]
        ]

        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = '*Selecione o campus:*',
            parse_mode = 'Markdown',
            reply_markup = replyMarkup
        )

    def selectStartPoint(self, bot, update, city):
        keyboard = [
            [
                telegram.InlineKeyboardButton('Terminal', callback_data = 'startPointBus-terminal-' + city + '-week'),
                telegram.InlineKeyboardButton('Terminal (Sábado)', callback_data = 'startPointBus-terminal-' + city + '-sat'),
            ],
            [
                telegram.InlineKeyboardButton('UFFS', callback_data = 'startPointBus-uffs-' + city + '-week'),
                telegram.InlineKeyboardButton('UFFS (Sábado)', callback_data = 'startPointBus-uffs-' + city + '-sat'),
            ],
            [
                telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
            ]
        ]
        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = '*Selecione o ponto de partida:*',
            parse_mode = 'Markdown',
            reply_markup = replyMarkup
        )

    def showSchedule(self, bot, update, startPointAndCityAndPeriod):
        startPointAndCityAndPeriod = startPointAndCityAndPeriod.split('-')
        startPoint = startPointAndCityAndPeriod[0]
        city = startPointAndCityAndPeriod[1]
        period = startPointAndCityAndPeriod[2]

        if city in self.schedules and self.schedules[city][period][startPoint]:
            bot.send_message(
                chat_id = update.callback_query.message.chat.id,
                text = self.formatSchedule(self.schedules[city][period][startPoint], startPoint, city, period),
                parse_mode = 'Markdown'
            )
        else:
            bot.send_message(
                chat_id = update.callback_query.message.chat.id,
                text = '*Desculpe, ainda não há horários registrados para essa rota/cidade.*',
                parse_mode = 'Markdown'
            )

    def formatSchedule(self, scheduleList, startPoint, city, period):
        if period == 'sat':
            formattedText = '*Horários de saída dos ônibus do(a) ' + startPoint.upper() + ' em ' + self.citiesFullName[city] + ' no sábado:*\n'
        else:
            formattedText = '*Horários de saída dos ônibus do(a) ' + startPoint.upper() + ' em ' + self.citiesFullName[city] + ':*\n'

        for schedule in scheduleList:
            formattedText += schedule + ', '
        return formattedText[:-2] + '.\n'