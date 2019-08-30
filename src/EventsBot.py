import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, date
from Utils import Utils

class EventsBot:

    months = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

    URL_EVENTS = 'https://www.uffs.edu.br/eventos'

    def formatList(self, eventList):
        formatedText = 'Próximos Eventos:\n'
        for event in eventList:
            formatedText += '\n\nEvento: ' + event[0] + '\nQuando: ' + event[1] + '\nLink: ' + event[2]
        return formatedText

    def getEvents(self):
        eventList = []
        page = requests.get(self.URL_EVENTS)
        soup = BeautifulSoup(page.text, 'html.parser')
        divDescription = soup.find_all('div', {"class": "detalhes-evento"})
        divTitle = soup.find_all('div', {"class": "titulo-evento"})
        for index, div in enumerate(divDescription):
            regex = re.compile(r'\d+/\w+/\d+')
            eventDesc = div.find('span').text
            eventDate = regex.findall(eventDesc)
            eventDate = [date.split('/') for date in eventDate]
            endDate = date(int(eventDate[len(eventDate)-1][2]), self.months[eventDate[len(eventDate)-1][1]], int(eventDate[len(eventDate)-1][0]))
            todayDate = datetime.today().date()
            if(todayDate <= endDate):
                eventList.append([divTitle[index].p.text, eventDesc, divTitle[index].p.parent['href'], endDate])

        eventList.sort(key=lambda x: x[3])
        return self.formatList(eventList)

    def showEvents(self, bot, update):        
        message = self.getEvents()
        bot.send_message(
            chat_id = Utils.getChatId(bot, update),
            text = message
        )
        Utils.showStartMenu(bot, update)