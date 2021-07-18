import telebot
import config
import time
import my_class
from telebot import types


# BOT--------------------------------------------------

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Субтитры", callback_data='subs')
    markup.add(item1)
    bot.send_message(
        message.chat.id,
        'Привет, я умею переводить субтитры на'
        ' платформе YouTube на любой язык.\n' +
        'Выберите "Субтитры"', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'subs':
        tmp = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="Введите ссылку на видео.",
                                    reply_markup=None)
        bot.register_next_step_handler(tmp, video_url)


@bot.message_handler(content_types=['text'])
def video_url(message):
    url = message.text
    youtube_api = my_class.YoutubeSubsTranslate(url)
    go_next = 0
    no_subs = "К сожалению у этого видео нет субтитров." \
              " Повторите попытку с другим видео."
    for i in youtube_api.error_type:
        if i == "no_subs":
            bot.send_message(message.chat.id, no_subs)
            go_next = 1
    if not go_next:
        info_lang = 'Теперь введите язык, на который хотите получить' \
                    ' перевод. Название языка вводите с большой буквы.\n'
        info_lang += "\nэто список достпуных для перевода языков:"
        list_lang = ""
        for language in youtube_api.subs_list._translation_languages:
            list_lang += language['language'] + "\n"
        bot.send_message(message.chat.id, info_lang)
        time.sleep(2)
        tmp = bot.send_message(message.chat.id, list_lang)
        bot.register_next_step_handler(tmp, take_lang, youtube_api)


@bot.message_handler(content_types=['text'])
def take_lang(message, youtube_api):
    no_lang_to_translate = "К сожалению язык, который вы ввели не" \
                           " доступен для перевода. Пожалуста" \
                           " свертись со списком выше и повторите попытку."
    lang = message.text
    find = 0
    for language in youtube_api.subs_list._translation_languages:
        if lang == language['language']:
            find = 1
            break
    if find:
        youtube_api(lang)
        bot.send_document(message.chat.id, open(r'translate.txt', 'rb'))
    else:
        tmp = bot.send_message(message.chat.id, no_lang_to_translate)
        bot.register_next_step_handler(tmp, take_lang, youtube_api)


bot.polling(none_stop=True)
