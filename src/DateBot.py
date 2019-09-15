import telegram
from tika import parser
import time
from Utils import Utils
import re

class DateBot:

    def checkMonth(self, raw):
        for char in "*\n":
            raw = raw.replace(char, '')
        
        if(raw == "JANEIRO" or raw == "FEVEREIRO" or raw == "MARÇO" or raw == "ABRIL" or raw == "MAIO" or raw == "JUNHO" or raw == "JULHO" or raw == "AGOSTO" or raw == "SETEMBRO" or raw == "OUTUBRO" or raw == "NOVEMBRO" or raw == "DEZEMBRO"):
            return True
        else:
            return False

    def checkGradu(self, raw):
        for char in "*\n":
            raw = raw.replace(char, '')

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
            if(re.search('^[0-9]{4}$', i)):
                break

            if(term != "todas"):
                if(self.checkMonth(i) == True):      #se for mes
                    results.append('\n*' + i + '*')

                elif(self.checkGradu(i) == True):        #Pega a graduação
                    results.append('*' + i + '*\n')
                else:
                    if(self.getImportantDates(i, term) == True):      #pega as informacoes que a principio são as mais relevantes
                        results.append(i)

        count = 0

        # ------- remove os meses sem informações
        for i in results:
            if(self.checkMonth(results[count]) == True):

                if(self.checkGradu(results[count + 1]) == True):

                    if(self.checkGradu(results[count + 2]) == True):

                        if(self.checkMonth(results[count + 3]) == True):
                            results.pop(count)
                            results.pop(count)
                            results.pop(count)
                            count -=1

                    elif(self.checkMonth(results[count + 2]) == True):
                        results.pop(count)
                        results.pop(count)
                        count-=1
                                    
            count += 1

        separator = '\n'
        results = separator.join(results)

        maxCharactersPerTelegramMsg = 4095
        results = [results[i:i+maxCharactersPerTelegramMsg] for i in range(0, len(results), maxCharactersPerTelegramMsg)]
        for partOfMsg in results:
            bot.sendMessage(Utils.getChatId(bot, update), partOfMsg, parse_mode='Markdown')
            time.sleep(2)
        Utils.showStartMenu(bot, update)

    def selectTerm(self, bot, update):
        keyboard = [
            [
                telegram.InlineKeyboardButton('Matriculas e Rematriculas', callback_data = 'date-matriculas'),
                telegram.InlineKeyboardButton('CCRs', callback_data = 'date-ccr')
            ],
            [
                telegram.InlineKeyboardButton('Aulas e Férias/Feriados', callback_data = 'date-aulas'),
                telegram.InlineKeyboardButton('ACCs', callback_data = 'date-acc')
            ],
            [
                telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
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