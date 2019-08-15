import os
import requests
from bs4 import BeautifulSoup
import datetime
import telepot

bot = telepot.Bot(os.environ['telegramToken'])
URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/chapeco/restaurante_universitario'

menuCache = {}

def onMsgReceived(msg):
    msgToSend = ''

    if msg['text'] == '/start':
        msgToSend = 'Olá!\nExecute um dos comandos abaixo para continuar:\n1 - \\cardapio'
    elif msg['text'] == '/cardapio':
        if datetime.date.today() in menuCache:
            msgToSend = menuCache[datetime.date.today()]
        else:
            bot.sendMessage(msg['chat']['id'], 'Aguarde enquanto baixamos o cardápio...')
            msgToSend = formatMenuMsg(getMenu())
    
    if msgToSend:
        bot.sendMessage(msg['chat']['id'], msgToSend)

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

    menuCache[datetime.date.today()] = prettyMsg

    return prettyMsg

bot.message_loop(onMsgReceived)

while True:
    pass