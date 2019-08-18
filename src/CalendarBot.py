import requests
from bs4 import BeautifulSoup
import telegram

class CalendarBot:
    urlAcademicCalendar = 'https://www.uffs.edu.br/institucional/pro-reitorias/graduacao/calendario-academico'
    isCalendarInCache = False

    def getCalendar(self, bot, update):
        chatId = None
        try:
            chatId = update.message.chat_id
        except:
            chatId = update['callback_query']['message']['chat']['id']

        bot.sendMessage(
            chatId,
            'Só um segundo...'
        )

        if(self.downloadCalendar()):
            bot.send_document(
                chat_id = chatId,
                document = open('calendario-academico.pdf', 'rb')
            )
        else:
            bot.sendMessage(
                chatId,
                'Desculpe, não foi possível baixar o calendário, tente novamente mais tarde.'
            )

    def downloadCalendar(self):
        if self.isCalendarInCache is True:
            return True

        page = requests.get(self.urlAcademicCalendar)
        soup = BeautifulSoup(page.text, 'html.parser')
        allLinks = soup.find_all('a')

        calendarPageLink = None
        for link in allLinks:
            if str(link.string)[:8].lower() == 'portaria':
                calendarPageLink = link['href']
                break

        if calendarPageLink is not None:
            page = requests.get(calendarPageLink)
            soup = BeautifulSoup(page.text, 'html.parser')
            allLinks = soup.find_all('a')

            calendarDownloadLink = None
            for link in allLinks:
                if 'anexo' in str(link):
                    calendarDownloadLink = link['href']
                    break

            if calendarDownloadLink is not None:
                calendar = requests.get(calendarDownloadLink)
                open('calendario-academico.pdf', 'wb').write(calendar.content)
                self.isCalendarInCache = True
                return True
                
        return False