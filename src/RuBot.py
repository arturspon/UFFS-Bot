import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import os
import re

class RuBot:
    URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/chapeco/restaurante_universitario'
    menuCache = {}

    def getMenu(self):
        page = requests.get(self.URL_MENU_RU_CCO)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find_all('table')
        week = soup.findAll(text=re.compile('Semana'))
        firstWeek = re.search(r'(\d+/\d+/\d+)', week[0].findParent('p').text).group(1).split('/')
        weekNumberToday = datetime.today().isocalendar()[1]
        weekNumberCalendar = date(int(firstWeek[2]), int(firstWeek[1]), int(firstWeek[0])).isocalendar()[1]
        if(weekNumberToday == weekNumberCalendar):
            html = str(week[0].findParent('p')) + str(table[0])
        else:
            html = str(week[1].findParent('p')) + str(table[1])

        img = requests.post('https://hcti.io/v1/image', data = {'HTML': html}, auth=(os.environ['htciId'], os.environ['htciKey']))
        imgUrl = img.text.split('"')[3]

        self.menuCache[date.today()] = imgUrl

        return imgUrl

    def showCardapio(self, bot, update):
        chatId = None
        try:
            chatId = update.message.chat_id
        except:
            chatId = update['callback_query']['message']['chat']['id']

        if date.today() in self.menuCache:
            imgToSend = self.menuCache[date.today()]
        else:
            bot.sendMessage(chatId, 'Aguarde enquanto baixamos o cardápio...')
            imgToSend = self.getMenu()
        
        if imgToSend:
            bot.send_photo(chat_id=chatId, photo=imgToSend)