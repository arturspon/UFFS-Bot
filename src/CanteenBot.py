import telegram
from Utils import Utils

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
        imgToSend = 'https://i.imgur.com/ec3Rvub.png'
        bot.send_photo(chat_id = Utils.getChatId(bot, update), photo = imgToSend)