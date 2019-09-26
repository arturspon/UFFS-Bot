import telegram
from Utils import Utils

class CanteenBot:

    def selectCampus(self, bot, update):
        buttonsNameAndData = [
            ['Cantina Chapecó', 'canteen-chapeco']
        ]
        textToShow = '*Selecione o campus:*'
        numButtonsPerLine = 2
        Utils.keyboardOptions(bot, update, buttonsNameAndData, textToShow, numButtonsPerLine, True)

    def showCardapio(self, bot, update):
        imgToSend = 'https://i.imgur.com/ec3Rvub.png'
        bot.send_photo(chat_id = Utils.getChatId(bot, update), photo = imgToSend)