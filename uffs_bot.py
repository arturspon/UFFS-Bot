import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import telepot

bot = telepot.Bot(os.environ['telegramToken'])
URL_MENU_RU_CCO = 'https://www.uffs.edu.br/campi/chapeco/restaurante_universitario'

menuCache = {}

def onMsgReceived(msg):
    msgToSend = ''

    if msg['text'] == '/start':
        msgToSend = 'Olá!\nExecute um dos comandos abaixo para continuar:\n\\cardapio - Mostra o cardápio do dia'
    elif msg['text'] == '/cardapio':
        if date.today() in menuCache:
            msgToSend = menuCache[date.today()]
        else:
            bot.sendMessage(msg['chat']['id'], 'Aguarde enquanto baixamos o cardápio...')
            msgToSend = formatMenuMsg(getMenu())
    
    if msgToSend:
        bot.sendMessage(msg['chat']['id'], msgToSend)

def getMenu():
    page = requests.get(URL_MENU_RU_CCO)
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

def formatMenuMsg(dirtyMenuList):
    prettyMsg ='O cardápio para hoje é:\n\n'

    for menuItem in dirtyMenuList:
        prettyMsg += menuItem + '\n'

    menuCache[date.today()] = prettyMsg

    return prettyMsg

bot.message_loop(onMsgReceived)

while True:
    pass