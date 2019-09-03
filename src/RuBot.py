import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import os
import re
import telegram
from conf.settings import htciId, htciKey
import schedule
import DatabaseConnection
from Utils import Utils

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
        query = "INSERT INTO images (weekNumber, imgUrl, imgHtml, campus) VALUES ({}, '{}', '{}', '{}');".format(weekNumberToday, imgUrl, html, campus)
        self.databaseConnection.executeQuery(query)
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

        query = "SELECT imgUrl FROM images WHERE weekNumber = {} AND campus = '{}';".format(Utils.getWeekNumber(), campus)
        image = self.databaseConnection.fetchAll(query)

        if len(image):
            imgToSend = image[0][0]
        else:
            bot.sendMessage(chatId, 'Aguarde enquanto baixamos o cardápio...')
            imgToSend = self.getMenu(campus)

        if imgToSend:
            bot.send_photo(chat_id=chatId, photo=imgToSend)
            print('Enviado cardápio para', Utils.getUsername(bot, update))

    def isInDataBase(self, chat_id, period):
        try:
            query = "SELECT chat_id FROM users WHERE chat_id = '{}' AND period = '{}';".format(str(chat_id), period)
            users = self.databaseConnection.fetchAll(query)
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
                query = "UPDATE users SET campus = '{}', period = '{}', username = '{}' WHERE chat_id = '{}';".format(campus, period, username, chat_id)
            else:
                query = "INSERT INTO users (chat_id, username, campus, period) VALUES ('{}', '{}', '{}', '{}');".format(str(chat_id), username, campus, period)

            self.databaseConnection.executeQuery(query)

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
            query = "DELETE FROM users WHERE chat_id = '{}';".format(chat_id)
            self.databaseConnection.executeQuery(query)

            bot.send_message(
                chat_id=chat_id,
                text='Cardápio automático desativado'
            )
            Utils.showStartMenuInExistingMsg(bot, update)
            print('Usuário', Utils.getUsername(bot, update), 'desativou o cardápio automático')

        except Exception as e:
            print("unsubToPeriodicMenu: "+str(e)+"\n")

    def sendMenuToSubs(self, bot, period):
        try:
            query = "SELECT chat_id, username, campus FROM users WHERE period = '{}';".format(period)
            users = self.databaseConnection.fetchAll(query)
            for user in users:
                chat_id = user[0]
                username = user[1]
                campus = user[2]
                try: #Tenta enviar mensagem para o chat_id cadastrado
                    if period == 'weekly':
                        query = "SELECT imgUrl FROM images WHERE weekNumber = {} AND campus = '{}';".format(Utils.getWeekNumber(), campus)
                        image = self.databaseConnection.fetchAll(query)
                        bot.send_photo(
                            chat_id=chat_id,
                            photo=image[0][0]
                        )
                    elif period == 'daily':
                        bot.send_message(
                            chat_id=chat_id,
                            text=self.getDailyMenu(campus)
                        )
                    print('Enviado', period, 'para', username)
                except Exception as e:
                    print("sendMenuToUser: "+str(e)+"\n")

        except Exception as e:
            print("sendMenuToSubs: "+str(e)+"\n")

    def getDailyMenu(self, campus):
        try:
            today = str(Utils.getWeekNumber()) + campus + str(date.today().weekday())
            if today not in self.dailyMenus:
                query = "SELECT imgHtml FROM images WHERE weekNumber = {} AND campus = '{}';".format(Utils.getWeekNumber(), campus)
                image = self.databaseConnection.fetchAll(query)
                soup = BeautifulSoup(image[0][0], 'html.parser')
                column = ''
                for row in soup.findAll('table')[0].tbody.findAll('tr'):
                    column = column + '\n' + row.findAll('td')[date.today().weekday()].p.text
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

            for i in range(len(listOfCampus)):
                query = "SELECT * FROM images WHERE weekNumber = {} AND campus = '{}';".format(Utils.getWeekNumber(), listOfCampus[i])
                image = self.databaseConnection.fetchAll(query)
                if len(image) == 0:
                    self.getMenu(listOfCampus[i])
        except Exception as e:
            print("getImages: "+str(e)+"\n")

    def sendMenuPeriodically(self, bot):
        try:
            # Download do cardápio toda segundas às 08h caso já não tenha sido baixado
            schedule.every().monday.at('08:00').do(self.getImages)

            #Todo dias as 09:00 manda o cardaio para os cadastrados
            schedule.every().monday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().tuesday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().wednesday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().thursday.at('09:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().friday.at('09:00').do(self.sendMenuToSubs, bot, "daily")

            #Toda segunda as 09:00 manda o cardapio para os cadastrados
            schedule.every().monday.at('09:00').do(self.sendMenuToSubs, bot, "weekly")

            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as e:
            print("sendMenuPeriodically: "+str(e)+"\n")