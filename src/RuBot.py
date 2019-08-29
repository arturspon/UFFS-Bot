import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import os
import re
import telegram
from conf.settings import htciId, htciKey
import schedule
import sqlite3
from Utils import Utils

class RuBot:
    menuCache = {}
    menuCacheHTML = {}
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
            self.menuCacheHTML[str(date.today().isocalendar()[1]) + campus] = html
        else:
            html = str(week[1]) + str(table[1])
            self.menuCacheHTML[str(date.today().isocalendar()[1]) + campus] = html

        img = requests.post('https://hcti.io/v1/image', data = {'HTML': html}, auth=(htciId, htciKey))
        imgUrl = img.text.split('"')[3]
        self.menuCache[str(date.today().isocalendar()[1]) + campus] = imgUrl

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
            print("isInDataBase: "+str(e)+"\n")

    def showCardapio(self, bot, update, campus):
        chatId = None
        try:
            chatId = update.message.chat_id
        except:
            chatId = update['callback_query']['message']['chat']['id']

        if str(date.today().isocalendar()[1]) + campus in self.menuCache:
            imgToSend = self.menuCache[str(date.today().isocalendar()[1]) + campus]
        else:
            bot.sendMessage(chatId, 'Aguarde enquanto baixamos o cardápio...')
            imgToSend = self.getMenu(campus)

        if imgToSend:
            bot.send_photo(chat_id=chatId, photo=imgToSend)

    def isInDataBase(self, chat_id):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id FROM users WHERE chat_id = '+str(chat_id)+';')
            users = cursor.fetchall()
            conn.close()
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
            try:
                chat_id = update.message.chat_id
            except:
                chat_id = update['callback_query']['message']['chat']['id']
            if self.isInDataBase(chat_id):
                query = "UPDATE users SET campus = '"+campus+"', period = '"+period+"' WHERE chat_id = "+str(chat_id)+';'
            else:
                query = "INSERT INTO users VALUES ("+str(chat_id)+", '"+campus+"', '"+period+"');"

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()

            bot.send_message(
                chat_id=chat_id,
                text='Cardápio automático ativado'
            )
            Utils.showStartMenuInExistingMsg(bot, update)
        except Exception as e:
            print("subToPeriodicMenu: "+str(e)+"\n")

    def unsubToPeriodicMenu(self, bot, update):
        try:
            try:
                chat_id = update.message.chat_id
            except:
                chat_id = update['callback_query']['message']['chat']['id']
            query = "UPDATE users SET period = 'none' WHERE chat_id = "+str(chat_id)+';'
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()

            bot.send_message(
                chat_id=chat_id,
                text='Cardápio automático desativado'
            )

        except Exception as e:
            print("unsubToPeriodicMenu: "+str(e)+"\n")

    def sendMenuToSubs(self, bot, period):
        try:
            query = "SELECT * FROM users WHERE period = '"+period+"';"
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(query)
            users = cursor.fetchall()
            conn.commit()
            conn.close()
            for user in users:
                chat_id = user[0]
                campus = user[1]
                try: #Tenta enviar mensagem para o chat_id cadastrado
                    if period == 'weekly':
                        bot.send_photo(
                            chat_id=chat_id,
                            photo=self.getMenu(campus)
                        )
                    elif period == 'daily':
                        bot.send_message(
                            chat_id=chat_id,
                            text=self.getDailyMenu(campus)
                        )
                except:
                    query = 'DELETE * FROM users WHERE chat_id = '+chat_id+';'
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    conn.close()

        except Exception as e:
            print("sendMenuToSubs: "+str(e)+"\n")

    def getDailyMenu(self, campus):
        try:
            today = str(date.today().isocalendar()[1]) + campus + str(date.today().weekday())
            if today not in self.dailyMenus:
                soup = BeautifulSoup(self.menuCacheHTML[str(date.today().isocalendar()[1]) + campus], 'html.parser')
                column = ''
                for row in soup.findAll('table')[0].tbody.findAll('tr'):
                    column = column + '\n' + row.findAll('td')[date.today().weekday()].p.text
                self.dailyMenus[today] = column
            return self.dailyMenus[today]
        except Exception as e:
            print("getDailyMenu: "+str(e)+"\n")

    def selectPeriod(self, bot, update):
        keyboard = [
            [
                telegram.InlineKeyboardButton('Diário', callback_data = 'daily'),
                telegram.InlineKeyboardButton('Semanal', callback_data = 'weekly')
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
            chat_id = update.callback_query.message.chat.id,
            text = 'Selecione a periodicidade:',
            parse_mode = 'HTML',
            reply_markup = replyMarkup
        )

    def sendMenuPeriodically(self, bot):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
                # Cria tabela para armazenar os chat_id dos usuarios possibilitando o envio de mensagens sem o chamado de comandos
                # campus armazena o campus do qual o usuario deseja saber o cardapio
                # Period armazena se ira receber o cardapio semanalmente ou diariamente ou não receber
            cursor.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, campus TEXT, period TEXT);")
            conn.commit()
            conn.close()

            #Todo dias as 10:00 manda o cardaio para os cadastrados
            schedule.every().monday.at('10:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().tuesday.at('10:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().wednesday.at('10:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().thursday.at('10:00').do(self.sendMenuToSubs, bot, "daily")
            schedule.every().friday.at('10:00').do(self.sendMenuToSubs, bot, "daily")
            #Toda segunda as 9:00 manda o cardapio para os cadastrados
            schedule.every().sunday.at('10:00').do(self.sendMenuToSubs, bot, "weekly")

            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as e:
            print("sendMenuPeriodically: "+str(e)+"\n")
