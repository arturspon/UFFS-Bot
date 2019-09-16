import requests
import time
import re
import telegram
import schedule
import DatabaseConnection
from bs4 import BeautifulSoup
from datetime import datetime, date
from conf.settings import htciId, htciKey
from Utils import Utils
from threading import Timer
from psycopg2 import sql

class RuBot:
    databaseConnection = DatabaseConnection.DatabaseConnection()
    dailyMenus = {}

    def findWeek(self, soup):
        paragraphs = soup.find_all('p')
        week = []
        for p in paragraphs:
            if('Semana' in p.text):
                week.append(p)

        return week

    def getMenu(self, campus):
        URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/' + campus + '/restaurante_universitario'
        page = requests.get(URL_MENU_RU_CCO)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find_all('table')

        if not table:
            return

        week = self.findWeek(soup)
        firstWeek = re.search(r'(\d+/\d+/\d+)', week[0].text).group(1).split('/')
        weekNumberToday = datetime.today().isocalendar()[1]
        weekNumberCalendar = date(int(firstWeek[2]), int(firstWeek[1]), int(firstWeek[0])).isocalendar()[1]
        if(weekNumberToday == weekNumberCalendar):
            html = str(week[0]) + str(table[0])
        else:
            html = str(week[1]) + str(table[1])

        img = requests.post('https://hcti.io/v1/image', data = {'HTML': html}, auth=(htciId, htciKey))
        imgUrl = img.text.split('"')[3]
        self.databaseConnection.executeQuery(
            sql.SQL("INSERT INTO images (weekNumber, imgUrl, imgHtml, campus) VALUES (%s, %s, %s, %s)"),
            [weekNumberToday, imgUrl, html, campus]
        )
        print('Inserido nova imagem ao banco\nweekNumber: ', Utils.getWeekNumber(), '\tCampus: ', campus)

        return imgUrl

    def selectCampus(self, bot, update):
        keyboard = [
            [
                telegram.InlineKeyboardButton('RU Chapecó', callback_data = 'RU-chapeco'),
                telegram.InlineKeyboardButton('RU Cerro Largo', callback_data = 'RU-cerro-largo'),
                telegram.InlineKeyboardButton('RU Erechim', callback_data = 'RU-erechim')
            ],
            [
                telegram.InlineKeyboardButton('RU Laranjeiras', callback_data = 'RU-laranjeiras-do-sul'),
                telegram.InlineKeyboardButton('RU Realeza', callback_data = 'RU-realeza')
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

    def selectCampusAuto(self, bot, update, period):
        try:
            keyboard = [
                [
                    telegram.InlineKeyboardButton('Chapecó', callback_data = 'AUTO/'+period+'/chapeco'),
                    telegram.InlineKeyboardButton('Cerro Largo', callback_data = 'AUTO/'+period+'/cerro-largo'),
                    telegram.InlineKeyboardButton('Erechim', callback_data = 'AUTO/'+period+'/erechim')
                ],
                [
                    telegram.InlineKeyboardButton('Laranjeiras', callback_data = 'AUTO/'+period+'/laranjeiras-do-sul'),
                    telegram.InlineKeyboardButton('Realeza', callback_data = 'AUTO/'+period+'/realeza')
                ],
                [
                    telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
                ]
            ]
            replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

            bot.editMessageText(
                message_id = update.callback_query.message.message_id,
                chat_id = update.callback_query.message.chat.id,
                text = 'Selecione o campus:',
                parse_mode = 'HTML',
                reply_markup = replyMarkup
            )
        except Exception as e:
            print("selectCampusAuto: "+str(e)+"\n")

    def showCardapio(self, bot, update, campus):
        chatId = Utils.getChatId(bot, update)

        image = self.databaseConnection.fetchAll(
            sql.SQL("SELECT imgUrl FROM images WHERE weekNumber = %s AND campus = %s;"),
            [Utils.getWeekNumber(), campus]
        )

        if len(image):
            imgToSend = image[0][0]
        else:
            bot.sendMessage(chatId, 'Aguarde enquanto baixamos o cardápio...')
            imgToSend = self.getMenu(campus)

        if imgToSend:
            bot.send_photo(chat_id=chatId, photo=imgToSend)
            print('Enviado cardápio para', Utils.getUsername(bot, update))
        else:
            bot.send_message(
                chat_id = chatId,
                text = "Desculpe-nos, o cardápio atualizado do RU ainda não foi publicado no site.\nTentaremos lhe enviar o cardápio novamente daqui 10 minutos.",
                parse_mode = 'Markdown'
            )
            print("Tentando enviar cardápio novamente daqui a 15 min...")
            Timer(900.0, self.showCardapio, [bot, update, campus]).start()

    def isInDataBase(self, chat_id, period):
        try:
            users = self.databaseConnection.fetchAll(
                sql.SQL("SELECT chat_id FROM users WHERE chat_id = %s AND period = %s;"),
                [chat_id, period]
            )
            if len(users):
                return True
            else:
                return False
        except Exception as e:
            print("isInDataBase: "+str(e)+"\n")

    def subToPeriodicMenu(self, bot, update, callback_data):#, campus, period):
        try:
            callback_data=callback_data.split('/')
            period = callback_data[1]
            campus = callback_data[2]
            chat_id = Utils.getChatId(bot, update)
            username = Utils.getUsername(bot, update)
            if self.isInDataBase(chat_id, period):
                self.databaseConnection.executeQuery(
                    sql.SQL("UPDATE users SET campus = %s, period = %s, username = %s WHERE chat_id = %s AND period = %s;"),
                    [campus, period, username, chat_id, period]
                )
            else:
                self.databaseConnection.executeQuery(
                    sql.SQL("INSERT INTO users (chat_id, username, campus, period) VALUES (%s, %s, %s, %s)"),
                    [chat_id, username, campus, period]
                )


            message = 'Cardápio ' + Utils.getPeriodFormated(period) + ' ativado para ' + Utils.getCampusFormated(campus) + '\nCardápio desta semana:'
            bot.send_message(
                chat_id=chat_id,
                text=message
            )
            Utils.showStartMenuInExistingMsg(bot, update)
            print('Usuário', username, 'ativou o cardápio automático', period, 'para o campus', campus)
            self.showCardapio(bot, update, campus)
        except Exception as e:
            print("subToPeriodicMenu: "+str(e)+"\n")

    def unsubToPeriodicMenu(self, bot, update):
        try:
            chat_id = Utils.getChatId(bot, update)
            self.databaseConnection.executeQuery(
                sql.SQL("DELETE FROM users WHERE chat_id = %s;"),
                [chat_id]
            )

            bot.send_message(
                chat_id=chat_id,
                text='Cardápio automático desativado'
            )
            Utils.showStartMenuInExistingMsg(bot, update)
            print('Usuário', Utils.getUsername(bot, update), 'desativou o cardápio automático')

        except Exception as e:
            print("unsubToPeriodicMenu: "+str(e)+"\n")

    def sendMenuToSubs(self, bot, period):
        results = self.databaseConnection.fetchAll(
            "SELECT value FROM status WHERE description = %s;",
            ['menuAvailable']
        )
        menuAvailable = results[0]
        if menuAvailable:
            try:
                users = self.databaseConnection.fetchAll(
                    "SELECT chat_id, username, campus FROM users WHERE period = %s;",
                    [period]
                )
                for user in users:
                    chat_id = user[0]
                    username = user[1]
                    campus = user[2]
                    try: # Tenta enviar mensagem para o chat_id cadastrado
                        if period == 'weekly':
                            image = self.databaseConnection.fetchAll(
                                "SELECT imgUrl FROM images WHERE weekNumber = %s AND campus = %s;",
                                [Utils.getWeekNumber(), campus]
                            )

                            try:
                                msgSent = bot.send_photo(
                                    chat_id = chat_id,
                                    photo = image[0][0]
                                )
                            except telegram.error.ChatMigrated as chatMigratedError:
                                print('Grupo mudou de id, atualizando informação no banco...')
                                self.databaseConnection.executeQuery(
                                    sql.SQL("UPDATE users SET chat_id = %s WHERE chat_id = %s;"),
                                    [chatMigratedError.new_chat_id, chat_id]
                                )
                                chat_id = chatMigratedError.new_chat_id
                                msgSent = bot.send_photo(
                                    chat_id = chat_id,
                                    photo = image[0][0]
                                )

                            try:
                                bot.pin_chat_message(
                                    chat_id = chat_id,
                                    message_id = msgSent.message_id,
                                    disable_notification = None
                                )
                            except Exception as errPinMsg:
                                print('O bot tentou fixar o cardápio porém não tem permissão para isso -> ', errPinMsg)

                        elif period == 'daily':
                            try:
                                bot.send_message(
                                    chat_id=chat_id,
                                    text=self.getDailyMenu(campus),
                                    parse_mode = 'Markdown'
                                )
                            except telegram.error.ChatMigrated as chatMigratedError:
                                print('Grupo mudou de id, atualizando informação no banco...')
                                self.databaseConnection.executeQuery(
                                    sql.SQL("UPDATE users SET chat_id = %s WHERE chat_id = %s;"),
                                    [chatMigratedError.new_chat_id, chat_id]
                                )
                                chat_id = chatMigratedError.new_chat_id
                                bot.send_message(
                                    chat_id=chat_id,
                                    text=self.getDailyMenu(campus),
                                    parse_mode = 'Markdown'
                                )
                        print('Enviado', period, 'para', username)
                    except Exception as e:
                        print("sendMenuToUser: "+str(e)+"\n")

            except Exception as e:
                print("sendMenuToSubs: "+str(e)+"\n")

        else:
            print("Tentando enviar cardápio novamente daqui a 15 min...")
            Timer(900.0, self.sendMenuToSubs, [bot, period]).start()

    def getDailyMenu(self, campus):
        try:
            today = str(Utils.getWeekNumber()) + campus + str(date.today().weekday())
            if today not in self.dailyMenus:
                image = self.databaseConnection.fetchAll(
                    "SELECT imgHtml FROM images WHERE weekNumber = %s AND campus = %s;",
                    [Utils.getWeekNumber(), campus]
                )
                soup = BeautifulSoup(image[0][0], 'html.parser')
                column = '*O cardápio de '
                for i, row in enumerate(soup.findAll('table')[0].tbody.findAll('tr')):
                    cell = row.findAll('td')[date.today().weekday()].findAll('p')
                    text = ''
                    for line in cell:
                        text = text + line.text + ' '
                    if(i == 0):
                        column += text.lower() + 'será:*'
                        continue
                    column += '\n' + text
                self.dailyMenus[today] = column
            return self.dailyMenus[today]
        except Exception as e:
            print("getDailyMenu: "+str(e)+"\n")

    def selectPeriod(self, bot, update):
        chat_id = update.callback_query.message.chat.id
        dailyButton = 'Diário'
        weeklyButton = 'Semanal'
        if self.isInDataBase(chat_id, 'daily'):
            dailyButton += ' ✔'
        if self.isInDataBase(chat_id, 'weekly'):
            weeklyButton += ' ✔'
        keyboard = [
            [
                telegram.InlineKeyboardButton(dailyButton, callback_data = 'daily'),
                telegram.InlineKeyboardButton(weeklyButton, callback_data = 'weekly')
            ],
            [
                telegram.InlineKeyboardButton('Desativar cardapio automático', callback_data = 'unsub')
            ],
            [
                telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
            ]
        ]

        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = chat_id,
            text = 'Selecione a periodicidade:',
            parse_mode = 'HTML',
            reply_markup = replyMarkup
        )

    def getImages(self):
        try:
            listOfCampus = ['chapeco', 'cerro-largo', 'erechim', 'laranjeiras-do-sul', 'realeza']

            self.databaseConnection.executeQuery(
                sql.SQL("UPDATE status SET value = %s WHERE description = %s;"),
                [True, 'menuAvailable']
            )

            for i in range(len(listOfCampus)):
                image = self.databaseConnection.fetchAll(
                    "SELECT * FROM images WHERE weekNumber = %s AND campus = %s;",
                    [Utils.getWeekNumber(), listOfCampus[i]]
                )
                if len(image) == 0:
                    print('Tentando baixar o cardápio de', listOfCampus[i])
                    if not self.getMenu(listOfCampus[i]):
                        print("Tentando baixar cardápio novamente daqui a 10 min...")
                        Timer(600.0, self.getImages).start()
                        self.databaseConnection.executeQuery(
                            sql.SQL("UPDATE status SET value = %s WHERE description = %s;"),
                            [False, 'menuAvailable']
                        )
        except Exception as e:
            print("getImages: "+str(e)+"\n")

    def sendMenuPeriodically(self, bot):
        try:
            # Download do cardápio toda segunda às 08h caso já não tenha sido baixado
            schedule.every().monday.at('08:00').do(self.getImages)

            # Todos os dias às 09:00 manda o cardápio para os cadastrados
            schedule.every().monday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().tuesday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().wednesday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().thursday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().friday.at('09:00').do(self.sendMenuToSubs, bot, "daily")

            # Toda segunda às 09:00 manda o cardápio para os cadastrados
            schedule.every().monday.at('09:00').do(self.sendMenuToSubs, bot, "weekly")

            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as e:
            print("sendMenuPeriodically: "+str(e)+"\n")