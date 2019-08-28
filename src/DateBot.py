import telegram
from tika import parser
import time

class DateBot:

    def checkMonth(self, raw):
        if(raw == "JANEIRO" or raw == "FEVEREIRO" or raw == "MARÇO" or raw == "ABRIL" or raw == "MAIO" or raw == "JUNHO" or raw == "JULHO" or raw == "AGOSTO" or raw == "SETEMBRO" or raw == "OUTUBRO" or raw == "NOVEMBRO" or raw == "DEZEMBRO"):
            return True
        else:
            return False

    def checkGradu(self, raw):
        if(raw == "Graduação" or raw == "Pós-Graduação"):
            return True
        else:
            return False

    def getImportantDates(self, raw, term):

        if(term == "matriculas" and 'atrícula' in raw):
            return True
        elif(term == "ccr" and 'CCR' in raw):
            return True
        elif(term == "acc" and 'ACC' in raw):
            return True
        if(term == 'aulas' and ('AULA' in raw or 'aula' in raw or 'érias' in raw)):
            return True
        else:
            return False
       

    def searchTerm(self, bot, update, term):
        
        rawText = parser.from_file('./calendario-academico.pdf')
        rawList = rawText['content'].splitlines()

        results = []
        for i in rawList:
            if(i == '2020'):     #encontrar alguma forma de pegar apenas o ano em andamento dinamicamente
                break

            if(term != "todas"):
                if(self.checkMonth(i) == True):      #se for mes
                    results.append('\n*' + i + '*')

                elif(self.checkGradu(i) == True):        #Pega a graduação
                    results.append('*' + i + '*\n')
                else:
                    if(self.getImportantDates(i, term) == True):      #pega as informacoes que a principio são as mais relevantes
                        results.append(i)

        separator = '\n'
        results = separator.join(results)
        if(len(results) < 4096):
            chatId = None
            try:
                chatId = update.message.chat_id
            except:
                chatId = update['callback_query']['message']['chat']['id']

            bot.sendMessage(chatId, results, parse_mode='Markdown')
        else:
            chatId = None
            try:
                chatId = update.message.chat_id
            except:
                chatId = update['callback_query']['message']['chat']['id']

            bot.sendMessage(chatId, results[:4096], parse_mode='Markdown')
            time.sleep(5)
            bot.sendMessage(chatId, results[4096:8000], parse_mode='Markdown')








    def selectTerm(self, bot, update):
        keyboard = [
            [
                telegram.InlineKeyboardButton('Matriculas e Rematriculas', callback_data = 'date-matriculas'),
                telegram.InlineKeyboardButton('CCRs', callback_data = 'date-ccr')
            ],
            [
                telegram.InlineKeyboardButton('Aulas e Férias/Feriados', callback_data = 'date-aulas'),
                telegram.InlineKeyboardButton('ACCs', callback_data = 'date-acc')
            ]
        ]
            
        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = '*Selecione o Assunto:*',
            parse_mode = 'Markdown',
            reply_markup = replyMarkup
        )