import telebot
import config
from model import *
import logging
from time import sleep
from sqlalchemy.orm import sessionmaker, scoped_session
import sys

bot = telebot.TeleBot(config.token)
session = scoped_session(sessionmaker(bind=engine))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, config.messages["welcome"])


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as err:
            logging.error(err)
            sleep(5)
