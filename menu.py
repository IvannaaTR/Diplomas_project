# -*- coding: utf-8 -*-
from telebot import types
class Menu:
    def main_menu(self):
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        markup.add(types.KeyboardButton("Перша медична допомога"))
        markup.add(types.KeyboardButton("Екстрені номери"))
        markup.add(types.KeyboardButton("Безпека"))
        markup.add(types.KeyboardButton("Корисні посилання"))
        markup.add(types.KeyboardButton("Допомога"))
        markup.add(types.KeyboardButton("Оголошення"))
        markup.add(types.KeyboardButton("Про бота"))
        return markup

    def medical_menu(self):
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        markup.add(types.KeyboardButton("Загальний алгоритм"))
        markup.add(types.KeyboardButton("Рани та кровотечі"))
        markup.add(types.KeyboardButton("Накладання джгута"))
        markup.add(types.KeyboardButton("Серцево-легенева реанімація"))
        markup.add(types.KeyboardButton("Ушкодження грудної клітки"))
        markup.add(types.KeyboardButton("Контузія"))
        markup.add(types.KeyboardButton("Здавлення під завалами"))
        markup.add(types.KeyboardButton("Отруєння хімічними речовинами"))
        markup.add(types.KeyboardButton("Термічні опіки"))
        markup.add(types.KeyboardButton("Забій"))
        markup.add(types.KeyboardButton("Розтягнення"))
        markup.add(types.KeyboardButton("Вивих"))
        markup.add(types.KeyboardButton("Перелом"))
        markup.add(types.KeyboardButton("Тепловий удар"))
        markup.add(types.KeyboardButton("Головне меню"))
        return markup
    
    def safe_menu(self):
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        markup.add(types.KeyboardButton("Мінна безпека"))
        markup.add(types.KeyboardButton("Радіаційна загроза"))
        markup.add(types.KeyboardButton("Хімічна загроза"))
        markup.add(types.KeyboardButton("Карта повітряних тривог"))
        markup.add(types.KeyboardButton("Тривожна валіза"))
        markup.add(types.KeyboardButton("Аптечка"))
        markup.add(types.KeyboardButton("Головне меню"))
        return markup
    
    def help_menu(self):
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        markup.add(types.KeyboardButton("Можу допомогти"))
        markup.add(types.KeyboardButton("Потребую допомоги"))
        markup.add(types.KeyboardButton("Мої заявки"))
        markup.add(types.KeyboardButton("Головне меню"))
        return markup
    
    def advertisement_menu(self):
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        markup.add(types.KeyboardButton("Переглянути оголошення"))
        markup.add(types.KeyboardButton("Додати оголошення"))
        markup.add(types.KeyboardButton("Мої оголошення"))
        markup.add(types.KeyboardButton("Головне меню"))
        return markup
    
    def useful_links(self):
        markup = types.InlineKeyboardMarkup()
        url1 = types.InlineKeyboardButton(text="Безпека та правопорядок", url='https://kyivcity.gov.ua/bezpeka_ta_pravoporiadok/')
        url2 = types.InlineKeyboardButton(text="Домедична допомога", url='https://zakon.rada.gov.ua/laws/show/z0356-22#n139')
        url3 = types.InlineKeyboardButton(text="МОЗ", url='https://moz.gov.ua/')
        url4 = types.InlineKeyboardButton(text="ДСНС", url='https://dsns.gov.ua/')
        markup.row(url1, url2)
        markup.row(url3, url4)
        return markup