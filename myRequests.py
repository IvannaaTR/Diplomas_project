# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 00:52:23 2023

@author: Admin
"""
from telebot import types
from dataBase import DataBase
from canHelp import check_name
from canHelp import is_valid_phone_number


db = DataBase()
class myRequests:
    def inline_markup__my_requests(self):
        kb = types.InlineKeyboardMarkup(row_width=2)
        btn_next = types.InlineKeyboardButton(text='Далі', callback_data='next_request')
        btn_previous = types.InlineKeyboardButton(text='Назад', callback_data='previous_request')
        btn_update =  types.InlineKeyboardButton(text='Редагувати', callback_data='update_request')
        btn_cancel =  types.InlineKeyboardButton(text='Скасувати', callback_data='cancel_request')
        kb.row(btn_previous,btn_next)
        kb.row(btn_update,btn_cancel)
        return kb
    
    def inline_markup_update(self):
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_place = types.InlineKeyboardButton(text='Змінити місце проживання', callback_data='update_place')
        btn_number = types.InlineKeyboardButton(text='Змінити номер телефону', callback_data='update_number')
        btn_details =  types.InlineKeyboardButton(text='Змінити деталі', callback_data='update_details')
        btn_previous =  types.InlineKeyboardButton(text='Повернутись назад', callback_data='update_previous')
        kb.add(btn_place,btn_number,btn_details,btn_previous)
        return kb

    def build_my_requsests_text(self, getted_id, my_requests_index):
        result_string=""
        user = db.get_user(getted_id)
        if('requests'in user and len(user["requests"])!=0):
            user_region = user["location_region"]
            user_district = user["location_district"]
            user_city = user["location_city"]
            user_phone = user["phone_number"]
            user_category = user["requests"][my_requests_index]["category"]
            user_details = user["requests"][my_requests_index]["details"]
            
            result_string += f"Область: {user_region}\n"
            result_string += f"Район: {user_district}\n"
            result_string += f"Місто: {user_city}\n"
            result_string += f"Номер телефону: {user_phone}\n"
            result_string += f"Категорія допомоги: {user_category}\n"
            result_string += f"Деталі: {user_details}\n"
            result_string += "---\n"
            return result_string
    def update_place(self,bot,callback):
        sent = bot.send_message(callback.message.chat.id, "Вкажіть Вашу область:")
        bot.register_next_step_handler(sent, lambda msg: self.changed_region(bot, msg,callback.message.id))

    def changed_region(self,bot,message,message_id):
        message_to_save = message.text
        if(check_name(message_to_save)==True):
            db.set_user(message.chat.id, {"location_region": message_to_save})
            sent = bot.send_message(message.chat.id, "Вкажіть Ваш район:")
            bot.register_next_step_handler(sent, lambda msg: self.changed_district(bot, msg,message_id))
        else:
            sent = bot.reply_to(message, 'На жаль не вдалося знайти таку область.Перевірте будь ласка правильність написання та вкажіть назву області ще раз:')
            bot.register_next_step_handler(sent, lambda msg: self.changed_region(bot, msg,message_id))
    
    def changed_district(self,bot,message,message_id):
        message_to_save = message.text
        db.set_user(message.chat.id, {"location_district": message_to_save})
        sent = bot.send_message(message.chat.id, "Вкажіть Ваш населений пункт:")
        bot.register_next_step_handler(sent, lambda msg: self.changed_city(bot, msg,message_id))
        
    def changed_city(self,bot,message,message_id):
        message_to_save = message.text
        db.set_user(message.chat.id, {"location_city": message_to_save})
        bot.send_message(message.chat.id, "Дані успішно змінено✅")
        user = db.get_user(message.chat.id)
        index = user["my_requests_index"]
        result_string = self.build_my_requsests_text(message.chat.id, index)
        bot.edit_message_text(chat_id=message.chat.id, message_id = message_id, text=f'{result_string}', reply_markup= self.inline_markup_update())
        
    def update_phone(self,bot,callback):
        sent = bot.send_message(callback.message.chat.id, "Вкажіть Ваш номер телефону:")
        bot.register_next_step_handler(sent, lambda msg: self.changed_phone(bot, msg,callback.message.id))
    
    def changed_phone(self,bot,message,message_id):
        message_to_save = message.text
        if(is_valid_phone_number(message_to_save)):
            db.set_user(message.chat.id, {"phone_number": message_to_save})
            bot.send_message(message.chat.id, "Дані успішно змінено✅")
            user = db.get_user(message.chat.id)
            index = user["my_requests_index"]
            result_string = self.build_my_requsests_text(message.chat.id, index)
            bot.edit_message_text(chat_id=message.chat.id, message_id = message_id, text=f'{result_string}', reply_markup= self.inline_markup_update())
        else:
            sent = bot.reply_to(message, 'На жаль введений номер не є валідним. Перевірте будь ласка правильність написання та вкажіть номер ще раз:')
            bot.register_next_step_handler(sent, lambda msg: self.changed_phone(bot, msg,message_id))
    def update_details(self,bot,callback):
        sent = bot.send_message(callback.message.chat.id, "Вкажіть деталі:")
        bot.register_next_step_handler(sent, lambda msg: self.changed_details(bot, msg,callback.message.id))
    
    def changed_details(self,bot,message,message_id):
        message_to_save = message.text
        user = db.get_user(message.chat.id)
        item_index = user["my_requests_index"]
        db.set_user(message.chat.id, {f'requests.{item_index}.details': message_to_save})
        bot.send_message(message.chat.id, "Дані успішно змінено✅")
        user = db.get_user(message.chat.id)
        index = user["my_requests_index"]
        result_string = self.build_my_requsests_text(message.chat.id, index)
        bot.edit_message_text(chat_id=message.chat.id, message_id = message_id, text=f'{result_string}', reply_markup= self.inline_markup_update())