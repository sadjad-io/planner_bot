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

class Event_Det :
    def __ini__(self):
        self.title = None

#Send Inline Message After Enter Bot Id ( @bot_id ... )
@bot.inline_handler(lambda query: len(query.query) is 0)
def first_query(inline_query):
    try:
        events = session.query(Events).filter_by(owner_id=int(inline_query.from_user.id)).all()
        session.commit()
        event_list = []
        counter = 1
        for event in events:
            keyboard = types.InlineKeyboardMarkup()
            plan_text = event.text
            k1 = types.InlineKeyboardButton( "من هستم" , callback_data="add_me" + "|" + str(event.id) )
            k2 = types.InlineKeyboardButton( "من نیستم" , callback_data="remove_me" + "|" + str(event.id) )
            keyboard.add(k1,k2)
            event_list.append( types.InlineQueryResultArticle( str(counter) , u'انتشار پلن : ' + event.title + "( " + str( event.id ) + " )" , types.InputTextMessageContent( plan_text ) , reply_markup=keyboard ))
            counter+=1
        bot.answer_inline_query(inline_query.id, event_list , cache_time=1 , switch_pm_parameter="Create" ,switch_pm_text="ساخت برنامه جدید")
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

def get_name(message):
    try:
        chat_id = message.chat.id
        msg = bot.send_message( chat_id , config.messages['req_name'] )
        bot.register_next_step_handler( msg , get_details )
    except Exception, e:
        print(e)

@command
def get_details(message):
    try:
        chat_id = message.chat.id
        Event_Det.title = message.text
        msg = bot.send_message( chat_id , config.messages['req_details'] )
        bot.register_next_step_handler(msg , query_master )
    except Exception, e:
        print(e)

@command
def query_master(message):
    try:
        chat_id = message.chat.id
        event = Events(owner_id = chat_id , title = Event_Det.title , description = message.text , text = config.messages['plan'].format( message.chat.first_name , message.chat.username , event.title , event.description , " " , " " ) , agree_users = u" ", disagree_users = u" ")
        session.add( event )
        session.commit()
        keyboard = types.InlineKeyboardMarkup()
        k1 = types.InlineKeyboardButton( "منتشر کردن در ..." , switch_inline_query=event.title )
        keyboard.add(k1)
        bot.send_message(message.chat.id , u"خوب \n برنامه ریزی مون در مورد" + event.title + u" ساخته شد " , reply_markup = keyboard)
    except Exception, e:
        print(e)

@bot.inline_handler(lambda query: len(query.query) > 0)
def first_query(inline_query):
    try:
        query = inline_query.query
        events = session.query(Events).filter(Events.title.contains(query)).all()
        session.commit()
        event_list = []
        counter = 1
        for event in events:
            keyboard = types.InlineKeyboardMarkup()
            plan_text = event.text
            k1 = types.InlineKeyboardButton( "من هستم" , callback_data="add_me" + "|" + str(event.id) )
            k2 = types.InlineKeyboardButton( "من نیستم" , callback_data="remove_me" + "|" + str(event.id) )
            keyboard.add(k1,k2)
            event_list.append( types.InlineQueryResultArticle( str(counter) , u'انتشار پلن : ' + event.title + "( " + str( event.id ) + " )" , types.InputTextMessageContent( plan_text ) , reply_markup=keyboard ))
            counter+=1
        bot.answer_inline_query(inline_query.id, event_list , cache_time=1 , switch_pm_parameter="Create" ,switch_pm_text="ساخت برنامه جدید")
    except Exception, e:
        print(e)

@bot.callback_query_handler(func=lambda call : True )
def callback_inline(call):
    data = call.data.split( '|' )
    if data[0]=="add_me": ##Add note
        event = session.query(Events).filter_by(id=int(data[1])).first()
        session.commit()
        owner = session.query(Users).filter_by(user_id=int(event.owner_id)).first()
        session.commit()
        user = config.messages['user'].format( call.from_user.first_name , call.from_user.last_name , call.from_user.username )
        if user in event.disagree_users:
            event.disagree_users = event.disagree_users.replace( user , "")
        if user in event.agree_users:
            event.agree_users = event.agree_users.replace( user , "")
            bot.answer_callback_query( callback_query_id= call.id , text = u"اسمت از تو لیست اونایی که میان حذف شد" , cache_time = 0 )
        else:
            event.agree_users+= user
        keyboard = types.InlineKeyboardMarkup()
        k1 = types.InlineKeyboardButton( "من هستم" , callback_data="add_me" + "|" + str(event.id) )
        k2 = types.InlineKeyboardButton( "من نیستم" , callback_data="remove_me" + "|" + str(event.id) )
        keyboard.add(k1,k2)
        bot.edit_message_text(inline_message_id = call.inline_message_id , text = config.messages['plan'].format( owner.fname , owner.username , event.title , event.description , event.agree_users , event.disagree_users ) , reply_markup = keyboard )
        bot.answer_callback_query( callback_query_id= call.id , text = u"اسمت با موفقیت به لیست اضافه شد 😍" , cache_time = 0 )

    if data[0]=="remove_me": ##Add note
        event = session.query(Events).filter_by(id=int(data[1])).first()
        session.commit()
        owner = session.query(Users).filter_by(user_id=int(event.owner_id)).first()
        session.commit()
        user = config.messages['user'].format( call.from_user.first_name , call.from_user.last_name , call.from_user.username )
        if user in event.agree_users:
            event.agree_users = event.agree_users.replace( user , "")
        if user in event.disagree_users:
            event.disagree_users = event.disagree_users.replace( user , "")
            bot.answer_callback_query( callback_query_id= call.id , text = u"اسمت از تو لیست اونایی که نمیان حذف شد" , cache_time = 0 )
        else:
            event.disagree_users+= user
        keyboard = types.InlineKeyboardMarkup()
        k1 = types.InlineKeyboardButton( "من هستم" , callback_data="add_me" + "|" + str(event.id) )
        k2 = types.InlineKeyboardButton( "من نیستم" , callback_data="remove_me" + "|" + str(event.id) )
        keyboard.add(k1,k2)
        bot.edit_message_text(inline_message_id = call.inline_message_id , text = config.messages['plan'].format( owner.fname , owner.username , event.title , event.description , event.agree_users , event.disagree_users ) , reply_markup = keyboard )
        bot.answer_callback_query( callback_query_id= call.id , text = u"اسمت با موفقیت به لیست اضافه شد 😍" , cache_time = 0 )
if __name__ == '__main__':
    bot.polling(none_stop=True)
