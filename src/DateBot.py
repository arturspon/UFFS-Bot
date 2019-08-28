import telegram
from tika import parser

class DateBot:

    def checkMonth(self, raw):
        # if ('JANEIRO' in raw or 'FEVEREIRO' in raw or 'MARÇO' in raw):
        if(raw == "JANEIRO" or raw == "FEVEREIRO" or raw == "MARÇO" or raw == "ABRIL" or raw == "MAIO" or raw == "JUNHO" or raw == "JULHO" or raw == "AGOSTO" or raw == "SETEMBRO" or raw == "OUTUBRO" or raw == "NOVEMBRO" or raw == "DEZEMBRO"):
            return True
        else:
            return False

    def checkGradu(self, raw):
        if(raw == "Graduação" or raw == "Pós-Graduação"):
            return True
        else:
            return False

    def getImportantDates(self, raw):
        if('rematrícula' in raw or 'matrícula' in raw or 'ACC' in raw or 'férias' in raw):
            return True
        else:
            return False

    def loadDates(self, bot, update):

        rawText = parser.from_file('./calendario-academico.pdf')
        rawList = rawText['content'].splitlines()

        results = []
        for i in rawList:
            if(i == '2020'):     #encontrar alguma forma de pegar apenas o ano em andamento dinamicamente
                break

            if(self.checkMonth(i) == True):      #se for mes
                results.append('\n*' + i + '*')

            elif(self.checkGradu(i) == True):        #Pega a graduação
                results.append('*' + i + '*\n')
            else:
                if(self.getImportantDates(i) == True):      #pega as informacoes que a principio são as mais relevantes
                    results.append(i)

        separator = '\n'
        results = separator.join(results)
        print(results)

        chatId = None
        try:
            chatId = update.message.chat_id
        except:
            chatId = update['callback_query']['message']['chat']['id']

        bot.sendMessage(chatId, results, parse_mode='Markdown')
