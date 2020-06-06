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
import configparser
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
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
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Upload photo to start',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CHOOSING


def choice(update, context):
    user = update.message.from_user
    logger.info("Choice of %s: %s", user.first_name, update.message.text)

    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())
    return PHOTO


def photo(update, context):
    user = update.message.from_user
    logger.info("Sent info to  %s: %s", user.first_name, f'{user.first_name}_{user.last_name}')
    update.message.reply_text('Description what we\'ll do with the photo\n Send me some photo now')
    return PHOTO_UPLOAD


def photo_upload(update, context):
    user = update.message.from_user
    chat_id = update.message.chat.id
    photo_file = update.message.photo[-1].get_file()
    # api.photo = photo_file.download_as_bytearray()
    api.set_photo(photo_file.download_as_bytearray())
    # photo_file.download(f'{chat_id}_photo.jpg')
    # api.set_data("/set", json=json.dumps({'img': f'{bytearr}'}))
    logger.info("Photo of %s: %s", user.first_name, f'{chat_id}_photo.jpg')
    reply_keyboard = [['Upload Video', 'Exit']]
    update.message.reply_text('Gorgeous! Now, wait, we\'re processing your photo and you have to upload a video',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    # That's how we can send photo to a user
    # context.bot.sendPhoto(chat_id=chat_id, photo=open('phil.jpg', 'rb'), caption="This is the test photo caption")
    return CHOOSING


def video(update, context):
    # user = update.message.from_user
    # logger.info("Sent info to  %s: %s", user.first_name, f'{user.first_name}_{user.last_name}')
    update.message.reply_text('Description what we\'ll do with the video\n Send me some video now')
    return VIDEO_UPLOAD


def video_upload(update, context):
    user = update.message.from_user
    chat_id = update.message.chat.id
    logger.info("Video upload successful %s", user.first_name)
    video_file = update.message.video.get_file()
    video_file.download(f'{chat_id}_video.mp4')
    # api.video = video_file.download_as_bytearray()
    api.set_video(video_file.download_as_bytearray())
    logger.info("Video of %s: %s", user.first_name, f'{chat_id}_video.mp4')
    res = api.set_data('/inference')

    bot = update.message.bot
    with open(f"{chat_id}_final.gif", "wb") as fh:
        fh.write(base64.b64decode(res['video']))
    # with open('data.txt', 'w') as outfile:
    #     json.dump(res, outfile)
    # bot.send_video(chat_id,res['video'])
    bot.send_video(chat_id, video=open(f'{chat_id}_final.gif', 'rb'))
    update.message.reply_text('Gorgeous! Now, wait, we\'re processing your video')
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return CANCEL


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def regular_choice():
    pass


def main():
    logger.info("Start listenings...")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
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
