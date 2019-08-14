import requests
from bs4 import BeautifulSoup
import datetime
import telepot

bot = telepot.Bot('914192444:AAFy6E1ykzKeOeHcxZRtrNd_ME7KpoBg9rs')
URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/chapeco/restaurante_universitario'

def onMsgReceived(msg):
    if msg['text'] == '/cardapio':
        bot.sendMessage(msg['chat']['id'], 'Aguarde enquanto baixamos o cardápio...')
        todayMenuResults = getMenu()
        bot.sendMessage(msg['chat']['id'], formatMenuMsg(todayMenuResults))

def getMenu():
    page = requests.get(URL_MENU_RU_CCO)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find('table')
    dayNumber = datetime.datetime.today().weekday()
    results = []
    trList = table.find_all('tr')
    
    for i in range(0, 10):
        tdList = trList[i + 1].find_all('td')
        results.append(tdList[dayNumber].find('p').string)

    return results

def formatMenuMsg(dirtyMenuList):
    prettyMsg ='O cardápio para hoje é:\n\n'

    for menuItem in dirtyMenuList:
        prettyMsg += menuItem + '\n'

    return prettyMsg

bot.message_loop(onMsgReceived)

while True:
    pass