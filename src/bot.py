#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import os
import logging
import json
import base64
from api import Api
from convert import Converter
import configparser
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


CHOOSING, PHOTO, PHOTO_UPLOAD, VIDEO, VIDEO_UPLOAD, LOCATION, CANCEL = range(7)

api = Api()


def start(update, context):
    reply_keyboard = [['Upload Photo', 'Exit']]


    update.message.reply_text(
        'Hi! I\'ll help you to create a hilarious video. '
        'You just need to follow my commands and you\'ll get a video at the end ' 
        'Send /cancel to stop talking to me.\n\n'
        'To get started you\'ll need a portrait photo that you want to animate and a video.\n\n'
        'Press "Upload Photo" to continue...',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CHOOSING


def choice(update, context):
    user = update.message.from_user
    logger.info(f"chat_id:{update.message.chat.id} │ Choice of {user.first_name}: {update.message.text}")
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())
    return PHOTO


def photo(update, context):
    user = update.message.from_user
    logger.info(f"chat_id:{update.message.chat.id} │ Sent photo info to {user.first_name}")
    context.bot.sendPhoto(chat_id=update.message.chat.id, photo=open('example_photo.jpg', 'rb'),
                          caption="That's an example of a good photo to process.\n\n"
                                  "Now you should send me a photo to work with.")
    return PHOTO_UPLOAD


def photo_upload(update, context):
    user = update.message.from_user
    chat_id = update.message.chat.id
    photo_file = update.message.photo[-1].get_file()
    api.set_photo(photo_file.download_as_bytearray())

    # api.set_data("/set", json=json.dumps({'img': f'{bytearr}'}))

    logger.info(f"chat_id:{chat_id} │ Got photo from {user.first_name} {chat_id}_photo.jpg")
    reply_keyboard = [['Upload Video', 'Exit']]
    update.message.reply_text('Gorgeous! '
                              'Now send me a video of you talking or pretending that you\'re the person on the picture.'
                              'I need to see your face clearly.'
                              'The better you upload the video, the better the result will be.\n\n'
                              'Press "Upload Video" to continue...',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSING


def video(update, context):
    user = update.message.from_user
    logger.info(f"chat_id:{update.message.chat.id} │ Sent video info to {user.first_name}")
    update.message.reply_text('I hope you\'ve prepared a video based on my previous message because you\'ll need it now'
                              '.\n\n Now you should send me a video to work with')
    return VIDEO_UPLOAD


def video_upload(update, context):
    user = update.message.from_user
    chat_id = update.message.chat.id
    video_file = update.message.video.get_file()
    video_file.download(f'{chat_id}_video.mp4')
    logger.info("Video upload successful %s", user.first_name)
    # api.video = video_file.download_as_bytearray()
    # api.set_video(video_file.download_as_bytearray())
    logger.info(f"chat_id:{chat_id} │ Got video from {user.first_name} {chat_id}_video.jpg")
    # api.set_data('/set')
    api.set_video(video_file.download_as_bytearray())

    logger.info("Video of %s: %s", user.first_name, f'{chat_id}_video.mp4')
    update.message.reply_text('Perfect! Now, wait, we are processing your request. Please wait, processing can last longer than 30 seconds')
    res = api.set_data('/inference')

    bot = update.message.bot
    c = Converter(base64.b64encode(video_file.download_as_bytearray()),
                  res['video'],result=f"{chat_id}_final.mp4")
    c.convert()

    with open(f"{chat_id}_final.gif", "wb") as fh:
        fh.write(base64.b64decode(res['video']))

    bot.send_video(chat_id, video=open(f'{chat_id}_final.mp4', 'rb'))

    logger.info("Got video from %s: %s", user.first_name, f'{chat_id}_video.mp4')

    update.message.reply_text('Hope you enjoyed the result.\n\nTo start over message /start.',

    
    #
    #   Send result
    #
    logger.info(f"chat_id:{chat_id} │ Send final result {user.first_name}")
    update.message.reply_text('Hope you enjoyed the result.\n\nTo start over message me with /start.',
                              reply_markup=ReplyKeyboardRemove())
    logger.info(f"chat_id:{update.message.chat.id} │ User {user.first.name} ended the conversation")
    return ConversationHandler.END


def skip_photo(update, context):
    user = update.message.from_user
    logger.info(f"chat_id:{update.message.chat.ud} │ User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')
    return LOCATION


def cancel(update, context):
    user = update.message.from_user
    logger.info(f"chat_id:{update.message.chat.id} │ User {user.first.name} ended the conversation")
    update.message.reply_text('Bye! I hope we can talk again some day.\n\n'
                              'Message me with /start if you changed your mind',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logger.info("Start listenings...")
    print(os.environ['TELEGRAM_TOKEN'])
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            # CHOICE: [MessageHandler(Filters.regex('^(Photo|Video|Exit)$'), choice)],
            CHOOSING: [MessageHandler(Filters.regex('^Upload Photo$'),
                                      photo),
                       MessageHandler(Filters.regex('^Upload Video$'),
                                      video),
                       MessageHandler(Filters.regex('.$'),
                                      cancel)
                       ],

            PHOTO_UPLOAD: [MessageHandler(Filters.photo, photo_upload),
                           CommandHandler('skip', skip_photo)],

            VIDEO: [MessageHandler(Filters.photo, video)],

            VIDEO_UPLOAD: [MessageHandler(Filters.video, video_upload),
                           CommandHandler('skip', skip_photo)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
