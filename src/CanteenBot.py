import telegram

class CanteenBot:

    def selectCampus(self, bot, update):
        keyboard = [
            [
                telegram.InlineKeyboardButton('Cantina Chapecó', callback_data = 'canteen-chapeco'),
            ],
            [
                telegram.InlineKeyboardButton('← Menu principal', callback_data = 'main-menu')
            ]
        ]
        replyMarkup = telegram.InlineKeyboardMarkup(keyboard)

        bot.editMessageText(
            message_id = update.callback_query.message.message_id,
            chat_id = update.callback_query.message.chat.id,
            text = '*Selecione o campus:*',
            parse_mode = 'Markdown',
            reply_markup = replyMarkup
        )

    def showCardapio(self, bot, update):
        chatId = None
        try:
            chatId = update.message.chat_id
        except:
            chatId = update['callback_query']['message']['chat']['id']
        
        imgToSend = 'https://i.imgur.com/ec3Rvub.png'

        bot.send_photo(chat_id=chatId, photo=imgToSend)