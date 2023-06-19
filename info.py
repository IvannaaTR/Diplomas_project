# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 22:27:30 2023

@author: Admin
"""
from telebot import types
from dataBase import DataBase
from menu import Menu

db = DataBase()
menu= Menu()

class Info:
    def create_answer_message(self, message, info_source):
        rym_numbers = ['I','II','III', 'IV','V','VI','VII','VIII','IX','X','XI','XII','XIII']
        number = 0
        result = ""
        for item_index, item in enumerate(info_source["text"]):
            if(str(item) != ""):
                res_num = rym_numbers[number]
                result += f"<b>{res_num}{' '+message.text}</b>\n\n{str(item)}\n\n"
                result += "#"
                number= number+1
        return result
    
    def find_info_message(self, message):
        res_text=""
        if(db.get_medical_info(message.text) is not None):
            info_source=db.get_medical_info(message.text)
            res_text=self.create_answer_message(message, info_source)
            return res_text
            
        elif (db.get_minesSafety_info(message.text) is not None):
            url_t=''
            txt="Офіційний портал Києва"
            info_source=db.get_minesSafety_info(message.text)
            res_text = self.create_answer_message(message, info_source)
            if message.text == "Екстрені номери" or message.text == "Аптечка":
                return self.create_answer_message(message, info_source)
            elif message.text=="Мінна безпека":
                url_t='https://kyivcity.gov.ua/bezpeka_ta_pravoporiadok/pam_yatky/minna_bezpeka_scho_potribno_znati_ta_vikonuvati/'
            elif message.text=="Радіаційна загроза":
                url_t= 'https://kyivcity.gov.ua/bezpeka_ta_pravoporiadok/pam_yatky/scho_robiti_u_razi_radiatsiyno_avari_abo_yadernogo_udaru_971291/'
            elif message.text=="Хімічна загроза":
                url_t= 'https://dsns.gov.ua/uk/abetka-bezpeki-1/nebezpeki-texnogennogo-xarakteru/ximicna-nebezpeka'
                txt="ДСНС"
            elif message.text=="Тривожна валіза":
                url_t= 'https://dsns.gov.ua/uk/abetka-bezpeki/diyi-naselennya-v-umovax-nadzvicainix-situacii-vojennogo-xarakteru'
                txt="ДСНС"
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text=txt, url=url_t)
            markup.add(button)
            return res_text, markup
            
        else:
            res_text="None"
            markup = menu.useful_links()
            return res_text, markup
            