import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time

class RuBot:
    URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/chapeco/restaurante_universitario'
    menuCache = {}

    def getMenu(self):
        page = requests.get(self.URL_MENU_RU_CCO)
        soup = BeautifulSoup(page.text, 'html.parser')
        week = soup.find_all('strong')
        table = soup.find_all('table')
        for index, textContent in enumerate(week):
            if('Semana' in textContent.string):
                weekNumberToday = datetime.today().isocalendar()[1]
                weekNumberCalendar = date(datetime.today().year, datetime.today().month, int(week[index+1].string)).isocalendar()[1]
                if(weekNumberToday == weekNumberCalendar):
                    table = table[0]
                else:
                    table = table[1]
                break
        dayNumber = datetime.today().weekday()
        results = []
        trList = table.find_all('tr')
        
        for i in range(0, 10):
            tdList = trList[i + 1].find_all('td')
            results.append(tdList[dayNumber].find('p').string)

        return results

    def formatMenuMsg(self, dirtyMenuList):
        prettyMsg ='O cardápio para hoje é:\n\n'

        for menuItem in dirtyMenuList:
            prettyMsg += menuItem + '\n'

        self.menuCache[date.today()] = prettyMsg

        return prettyMsg

    def showCardapio(self, bot, update):
        if date.today() in self.menuCache:
            msgToSend = self.menuCache[date.today()]
        else:
            bot.sendMessage(update.message.chat_id, 'Aguarde enquanto baixamos o cardápio...')
            msgToSend = self.formatMenuMsg(self.getMenu())
        
        if msgToSend:
            bot.sendMessage(update.message.chat_id, msgToSend)