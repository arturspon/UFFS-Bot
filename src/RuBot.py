import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import os
import re
import telegram

class RuBot:
    menuCache = {}

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

        img = requests.post('https://hcti.io/v1/image', data = {'HTML': html}, auth=(os.environ['htciId'], os.environ['htciKey']))
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
            text = 'Selecione o campus:',
            parse_mode = 'HTML',
            reply_markup = replyMarkup
        )

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
