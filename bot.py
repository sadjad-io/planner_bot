# -*- coding: utf-8 -*-

import telebot
from telebot import types
import config
from model import *
import logging
from time import sleep
from sqlalchemy.orm import sessionmaker, scoped_session
import sys

bot = telebot.TeleBot(config.token)
session = scoped_session(sessionmaker(bind=engine))

#Send Inline Message After Enter Bot Id ( @bot_id ... )
@bot.inline_handler(lambda query: len(query.query) is 0)
def first_query(inline_query):
    try:
        bot.answer_inline_query(inline_query.id, [], cache_time=1, switch_pm_parameter="123",switch_pm_text="ساخت برنامه جدید")
    except Exception, e:
        print(e)

#Welcome Message After Enter Start Command
@bot.message_handler(commands=['start'])
@user
def welcome(message):
    try:
        chat_id = message.chat.id
        bot.send_message( chat_id , config.messages['welcome'] )
        get_name(message)
    except Exception, e:
        print(e)

@command
def get_name(message):
    try:
        chat_id = message.chat.id
        msg = bot.send_message( chat_id , config.messages['req_name'] )
        bot.register_next_step_handler(msg , get_details )
    except Exception, e:
        print(e)
        
@command
def get_details(message): 
    try:
        chat_id = message.chat.id
        msg = bot.send_message( chat_id , config.messages['req_details'] )
        bot.register_next_step_handler(msg , query_master )
    except Exception, e:
        print(e)
        
@command
def query_master(message):
    try:
        chat_id = message.chat.id
        keyboard = types.InlineKeyboardMarkup()
        k1 = types.InlineKeyboardButton( "text" , switch_inline_query='text'  )
        keyboard.add(k1)
        bot.send_message(message.chat.id , "@EZPlanneBot test" , reply_markup=keyboard )
    except Exception, e:
        print(e)
    
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as err:
            logging.error(err)
            sleep(5)