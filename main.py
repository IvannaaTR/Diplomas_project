# -*- coding: utf-8 -*-
import telebot
from info import Info
from menu import Menu
from telebot import types
from dataBase import DataBase
from canHelp import CreateHelpItem
from myRequests import myRequests
from allRequests import allRequests
from canHelp import check_name
from canHelp import check_categories
from canHelp import is_valid_phone_number
import re

bot = telebot.TeleBot("token")
info = Info()
menu= Menu()
db = DataBase()
createHelp = CreateHelpItem()
myRequests = myRequests()
allRequests=allRequests()

def get_info(message):
    result=info.find_info_message(message)
    if(len(result)==2):
        if(result[0]=="None"):
            bot.send_message(message.chat.id, "На жаль мені не вдалося знайти жодної інформації по цьому запиту🤔 Однак, не засмучуйтесь, скористайтесть корисними посиланнями, задля пошуку потрібної інформації", reply_markup = result[1])
        else:
            answers = result[0].split('#')
            answers.pop()
            for answer in answers:
                bot.send_message(message.chat.id, answer, parse_mode="HTML")
            bot.send_message(message.chat.id, "✅ Для отримання детальнішої довідкової інформації перейдіть за посиланням 👇", reply_markup = result[1])
            bot.send_message(message.chat.id, "Будьте обачні та обережні 😉")
    else:
        answers = result.split('#')
        answers.pop()
        for answer in answers:
            bot.send_message(message.chat.id, answer, parse_mode="HTML")
   

def my_requests(message):
    result_string = myRequests.build_my_requsests_text(message.chat.id, 0)
    if(result_string != None):
        db.set_user(message.chat.id, {"my_requests_index": 0})
        bot.send_message(message.chat.id,f'{result_string}',reply_markup= myRequests.inline_markup__my_requests())
    else:
        bot.send_message(message.chat.id, text="У вас немає заявок")
    

@bot.callback_query_handler(func=lambda callback: callback.data == "next_request") 
def next_step(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["my_requests_index"]
    if(index!= len(user["requests"])-1):
        index = index + 1
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі cвої заявки ✅')
        return
    db.set_user(callback.message.chat.id, {"my_requests_index": index})
    result_string = myRequests.build_my_requsests_text(callback.message.chat.id, index)
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}',reply_markup= myRequests.inline_markup__my_requests() )
    
@bot.callback_query_handler(func=lambda callback: callback.data == "previous_request") 
def previous_step(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["my_requests_index"]
    if(index!= 0):
        index = index - 1
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі свої заявки ✅')
        return
    db.set_user(callback.message.chat.id, {"my_requests_index": index})
    result_string = myRequests.build_my_requsests_text(callback.message.chat.id, index)
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}',reply_markup= myRequests.inline_markup__my_requests() )

@bot.callback_query_handler(func=lambda callback: callback.data == "cancel_request") 
def cancel_request(callback):
    user = db.get_user(callback.message.chat.id)
    if(len(user["requests"])>1):
        item_index = user["my_requests_index"]
        db.users.update_one({"chat_id": callback.message.chat.id }, {'$unset': {f"requests.{item_index}": ""}})
        db.users.update_one({"chat_id": callback.message.chat.id }, {'$pull': {'requests': None}})
        db.set_user(callback.message.chat.id, {"my_requests_index": 0})
        result_string = myRequests.build_my_requsests_text(callback.message.chat.id, 0)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}',reply_markup= myRequests.inline_markup__my_requests() )
    else:
        item_index = user["my_requests_index"]
        db.users.update_one({"chat_id": callback.message.chat.id }, {'$unset': {f"requests": 1}})
        db.set_user(callback.message.chat.id, {"location_city":False, "location_region":False, "location_district":False, "need_help":False })
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text="У вас не залишилось жодної заявки!")


@bot.callback_query_handler(func=lambda callback: callback.data == "update_request") 
def update_request(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["my_requests_index"]
    result_string = myRequests.build_my_requsests_text(callback.message.chat.id, index)
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}', reply_markup= myRequests.inline_markup_update())
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_place") 
def update_place(callback):
    myRequests.update_place(bot,callback)
    
   
@bot.callback_query_handler(func=lambda callback: callback.data == "update_number") 
def update_phone(callback):
    myRequests.update_phone(bot,callback)
     
@bot.callback_query_handler(func=lambda callback: callback.data == "update_details") 
def update_details(callback):
    myRequests.update_details(bot,callback)
 
@bot.callback_query_handler(func=lambda callback: callback.data == "update_previous") 
def update_previous(callback):
    sent = bot.send_message(callback.message.chat.id, "Вже повертаємось🔙")
    user = db.get_user(callback.message.chat.id)
    index = user["my_requests_index"]
    result_string = myRequests.build_my_requsests_text(callback.message.chat.id, index)
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}', reply_markup= myRequests.inline_markup__my_requests() )


def can_help(message):
    documents = allRequests.get_all_requests(message.chat.id)
    user = db.get_user(message.chat.id)
    index1 = 0
    index2 = 0
    result_string = allRequests.build_button_text(documents,index1,index2)
    bot.send_message(message.chat.id,f'{result_string}',reply_markup= allRequests.inline_markup_creation())
    requests = documents[index1].get('requests', [])
    db.set_user(message.chat.id, {"help_index1":0, "help_index2":0, "end_help": len(requests)-1,"filtering":[False,False,False,False]})

@bot.callback_query_handler(func=lambda callback: callback.data == "next") 
def next_step(callback):
    flag_found=True
    user = db.get_user(callback.message.chat.id)
    index1 = user["help_index1"]
    index2 = user["help_index2"]
    documents = allRequests.get_documents(user)[0]
    requests = documents[index1].get('requests', [])
    db.set_user(callback.message.chat.id, {"end_help": len(requests)-1})
    end_index = len(requests)-1
    if(index2 != end_index):  
        if(user["filtering"][3] != False):
            index2 = index2 + 1
            while(documents[index1]["requests"][index2].get("category") != user["filtering"][3]):
                if(index2 == end_index):
                    flag_found=False
                    break
                index2 = index2 + 1
            db.set_user(callback.message.chat.id, {"help_index2": index2})
        else: 
            index2 = index2 + 1
            db.set_user(callback.message.chat.id, {"help_index2": index2})   
    else:
        if index1 != len(documents) - 1:
            index1 = index1 + 1
            requests = documents[index1].get('requests', [])
            db.set_user(callback.message.chat.id, {"end_help": len(requests)-1})
            user = db.get_user(callback.message.chat.id)
            end_index = user["end_help"]
            if(user["filtering"][3] != False):
                index2 = 0
                while(documents[index1]["requests"][index2].get("category") != user["filtering"][3]):
                    if(index2 == end_index):
                        flag_found=False
                        break
                    index2 = index2 + 1
            else:
                index2 = 0
            db.set_user(callback.message.chat.id, {"help_index1": index1, "help_index2": index2})
        else:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'Ви переглянули всі запити ✅', reply_markup=allRequests.inline_markup_creation())
            return
    if(flag_found == True):
        result_string  = allRequests.build_button_text(documents,index1,index2)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}', reply_markup=allRequests.inline_markup_creation())
            print("Повідомлення оновлено")
        except telebot.apihelper.ApiException as e:
            if "message is not modified" in str(e):
                print("Повідомлення не змінювалося")
        
    else:
        next_step(callback)

@bot.callback_query_handler(func=lambda callback: callback.data == "previous") 
def previous_step(callback):
    flag_found=True
    user = db.get_user(callback.message.chat.id)
    index1 = user["help_index1"]
    index2 = user["help_index2"]
    documents = allRequests.get_documents(user)[0]
    requests = documents[index1].get('requests', [])
    db.set_user(callback.message.chat.id, {"end_help": len(requests)-1})
    end_index = len(requests)-1
    if(index2 != 0):
        if(user["filtering"][3] != False):
            index2 = index2 - 1
            while(documents[index1]["requests"][index2].get("category") != user["filtering"][3]):
                if(index2 == 0):
                    flag_found=False
                    break
                index2 = index2 - 1
            db.set_user(callback.message.chat.id, {"help_index2": index2})
        else: 
            index2 = index2 - 1
            db.set_user(callback.message.chat.id, {"help_index2": index2}) 
    else:
        if index1!=0:
            index1 = index1 - 1
            requests = documents[index1].get('requests', [])
            db.set_user(callback.message.chat.id, {"end_help": len(requests)-1})
            user = db.get_user(callback.message.chat.id)
            end_index = user["end_help"]
            if(user["filtering"][3] != False):
                index2 = end_index
                while(documents[index1]["requests"][index2].get("category") != user["filtering"][3]):
                    if(index2 == end_index):
                        flag_found=False
                        break
                    index2 = index2 - 1
            else:
                index2 = end_index
                
            db.set_user(callback.message.chat.id, {"help_index1": index1})
            db.set_user(callback.message.chat.id, {"help_index2": index2})       
        else:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'Ви переглянули всі запити ✅', reply_markup=allRequests.inline_markup_creation())
            return
    if(flag_found == True):
        result_string  = allRequests.build_button_text(documents,index1,index2)
        try:
             bot.edit_message_text(chat_id=callback.message.chat.id, message_id = callback.message.id, text=f'{result_string}', reply_markup=allRequests.inline_markup_creation())
             print("Повідомлення оновлено")
        except telebot.apihelper.ApiException as e:
            if "message is not modified" in str(e):
                print("Повідомлення не змінювалося")
    else:
        previous_step(callback)


def get_filter(getted_id,messaged_id,index):
    user = db.get_user(getted_id)
    documents = allRequests.get_documents(user)
    if(len(documents[0])>0):
        index1 = 0
        index2 = 0
        if(user["filtering"][3] != False):
            while(documents[0][index1]["requests"][index2].get("category") != user["filtering"][3]):
                index2 = index2+1
            db.set_user(getted_id, {"help_index2":index2})
        result_string = allRequests.build_button_text(documents[0],index1,index2)
        try:
            bot.edit_message_text(chat_id=getted_id,message_id = messaged_id,text=f'{result_string}',reply_markup= allRequests.inline_markup_creation())
            print("Повідомлення оновлено")
        except telebot.apihelper.ApiException as e:
            if "message is not modified" in str(e):
                print("Повідомлення не змінювалося")
            else:
                print("Помилка при оновленні повідомлення:", e)
        
        requests = documents[0][index1].get('requests', [])
        db.set_user(getted_id, {"end_help": len(requests)-1})
        if(index!=-1):
            bot.send_message(getted_id, f'{documents[1]}️')
    else:
        db.set_user(getted_id, {f'filtering.{index}': False})
        bot.send_message(getted_id, "З використанням цього фільтра не знайдено жодних даних🤷‍♀️")
    
@bot.callback_query_handler(func=lambda callback: callback.data == "filter_region") 
def filter_region(callback):
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть область:')
    bot.register_next_step_handler(sent, lambda msg: get_region(msg,callback.message.id))
    
    
def get_region(message,message_id):
    getted_message = message.text
    if(check_name(getted_message)==True):
        db.set_user(message.chat.id, {"help_index1":0, "help_index2":0, f'filtering.0': getted_message})
        get_filter(message.chat.id,message_id,0)
    else:
        sent = bot.reply_to(message, 'На жаль не вдалося знайти таку область.Перевірте будь ласка правильність написання та вкажіть назву області ще раз:')
        bot.register_next_step_handler(sent, lambda msg: get_region(msg,message_id))
 
@bot.callback_query_handler(func=lambda callback: callback.data == "filter_district") 
def filter_district(callback):
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть район:')
    bot.register_next_step_handler(sent, lambda msg: get_district(msg,callback.message.id))
    
    
def get_district(message,message_id):
    getted_message = message.text
    db.set_user(message.chat.id, {"help_index1":0, "help_index2":0, f'filtering.1': getted_message})
    get_filter(message.chat.id,message_id,1)
    
@bot.callback_query_handler(func=lambda callback: callback.data == "filter_city") 
def filter_city(callback):
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть населений пункт:')
    bot.register_next_step_handler(sent, lambda msg: get_city(msg,callback.message.id))
    
    
def get_city(message,message_id):
    getted_message = message.text
    db.set_user(message.chat.id, {"help_index1":0, "help_index2":0, f'filtering.2': getted_message})
    get_filter(message.chat.id,message_id,2)
    

@bot.callback_query_handler(func=lambda callback: callback.data == "filter_category") 
def filter_category(callback):
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть категорію: Продукти, Одяг, Транспорт, Паливо, Житло, Інше')
    bot.register_next_step_handler(sent,lambda msg: get_category(msg,callback.message.id) )
    
    
def get_category(message,message_id):
    getted_message = message.text
    if(check_categories(getted_message)==True):
        db.set_user(message.chat.id, {"help_index1":0, "help_index2":0, f'filtering.3': getted_message})
        get_filter(message.chat.id,message_id,3)
    else:
        sent = bot.reply_to(message, 'На жаль категорія введена неправильно.Перевірте будь ласка правильність написання та вкажіть категорію ще раз:')
        bot.register_next_step_handler(sent, lambda msg: get_category(msg,message_id))

@bot.callback_query_handler(func=lambda callback: callback.data == "cancel_filter") 
def cancel_filter(callback):
    bot.send_message(callback.message.chat.id, f'Всі обрані фільтри скасовано!')
    db.set_user(callback.message.chat.id, {"help_index1":0, "help_index2":0, "filtering.0": False, "filtering.1": False, "filtering.2": False, "filtering.3": False})
    get_filter(callback.message.chat.id,callback.message.id,-1)

@bot.callback_query_handler(func=lambda callback: callback.data == "respond")
def respond(callback):
    user = db.get_user(callback.message.chat.id)
    index1 = user["help_index1"]
    index2 = user["help_index2"]
    documents = allRequests.get_documents(user)[0]
    getted_id = documents[index1].get('chat_id')
    getted_number = documents[index1].get('phone_number')
    result_string  = allRequests.build_button_text(documents,index1,index2)
    if(user["phone_number"]!=False):
        sent = bot.send_message(callback.message.chat.id, f'Збережена відповідь номер телефону: {user["phone_number"]}. Чи змінилися Ваші дані?')
        bot.register_next_step_handler(sent, lambda msg: check_answer_phone(msg,getted_id,getted_number,result_string,user["phone_number"]))
    else:
        sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону:')
        bot.register_next_step_handler(sent, lambda msg: save_phone(msg,getted_id,getted_number,result_string))

def check_answer_phone(message,getted_id,getted_number,result_string,phone):
    if(message.text.lower()=="так"):
        sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону:')
        bot.register_next_step_handler(sent,lambda msg: save_phone(msg,getted_id,getted_number,result_string))
    else:
        bot.send_message(message.chat.id, f'Номер телефону особи, що подала заявку: {getted_number}')
        bot.send_message(getted_id, f'На вашу заявку: {result_string} відгукнувся контакт з номером {phone}')
def save_phone(message,getted_id,getted_number,result_string):
    message_to_save = message.text
    if(is_valid_phone_number(message_to_save)):
        db.set_user(message.chat.id, {"phone_number": message_to_save})
        bot.send_message(message.chat.id, f'Номер телефону особи, що подала заявку: {getted_number}')
        bot.send_message(getted_id, f'На вашу заявку: {result_string} відгукнувся контакт з номером {message_to_save}')
    else:
        sent = bot.reply_to(message, 'На жаль введений номер не є валідним. Перевірте будь ласка правильність написання та вкажіть номер ще раз:')
        bot.register_next_step_handler(sent, lambda msg: save_phone(msg,getted_id,getted_number,result_string))



#ОГОЛОШЕННЯ
def save_advertisement_region(message):
    sent = bot.send_message(message.chat.id, "Вкажіть область в якій останній раз бачили людину:")
    bot.register_next_step_handler(sent, save_advertisement_district)

def save_advertisement_district(message):
    message_to_save = message.text
    if(check_name(message_to_save)==True):
        index = len(db.get_announcements(message.chat.id))
        db.create_announcement(message.chat.id, index)
        db.set_announcement(message.chat.id,index,{"location_region":message_to_save})
        sent = bot.send_message(message.chat.id, "Вкажіть район в якому останній раз бачили людину:")
        bot.register_next_step_handler(sent, save_advertisement_city)
    else:
        sent = bot.reply_to(message, 'На жаль не вдалося знайти таку область.Перевірте будь ласка правильність написання та вкажіть назву області ще раз:')
        bot.register_next_step_handler(sent, save_advertisement_district)
    
def save_advertisement_city(message):
    message_to_save = message.text
    index = len(db.get_announcements(message.chat.id))-1
    db.set_announcement(message.chat.id,index,{"location_district":message_to_save})
    sent = bot.send_message(message.chat.id, "Вкажіть місто в якому останній раз бачили людину:")
    bot.register_next_step_handler(sent, save_advertisement_full_name)
    
def save_advertisement_full_name(message):
    message_to_save = message.text
    index = len(db.get_announcements(message.chat.id))-1
    db.set_announcement(message.chat.id,index,{"location_city":message_to_save})
    sent = bot.send_message(message.chat.id, "Вкажіть Прізвище Ім*я По-батькові:")
    bot.register_next_step_handler(sent, save_advertisement_details)
    
def save_advertisement_details(message):
    message_to_save = message.text
    index = len(db.get_announcements(message.chat.id))-1
    db.set_announcement(message.chat.id,index,{"full_name":message_to_save})
    sent = bot.send_message(message.chat.id, "Вкажіть деталі, дату зникнення, умови, тощо:")
    bot.register_next_step_handler(sent, save_advertisement_photo)

def save_advertisement_photo(message):
    message_to_save = message.text
    index = len(db.get_announcements(message.chat.id))-1
    db.set_announcement(message.chat.id,index,{"details":message_to_save})
    sent = bot.send_message(message.chat.id, "Додайте фото")
    bot.register_next_step_handler(sent, save_advertisement_end)
    
def save_advertisement_end(message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        index = len(db.get_announcements(message.chat.id))-1
        downloaded_file = bot.download_file(file_path)
        db.set_announcement(message.chat.id,index,{"file_id":file_id, "file_path":file_path, "photo":downloaded_file})
        bot.reply_to(message, "Фото було збережено!")
        user = db.get_user(message.chat.id)
        phone=user["phone_number"]
        if(phone==False):
            sent = bot.send_message(message.chat.id, "Вкажіть свій номер телефону:")
            bot.register_next_step_handler(sent, save_advertisement_phone)
        else:
             sent = bot.send_message(message.chat.id, f'Чи не змінились ваші дані? Номер телефону: {phone}:')
             bot.register_next_step_handler(sent, check_phone)
    else:
        sent = bot.reply_to(message, "Будь ласка, надішліть фото.")
        bot.register_next_step_handler(sent, save_advertisement_end)
def save_advertisement_phone(message):
     message_to_save = message.text
     if(is_valid_phone_number(message_to_save)):
        db.set_user(message.chat.id, {"phone_number": message_to_save})
        bot.send_message(message.chat.id, "Оголошення успішно створено✅")
     else:
          sent = bot.reply_to(message, 'На жаль введений номер не є валідним. Перевірте будь ласка правильність написання та вкажіть номер ще раз:')
          bot.register_next_step_handler(sent, save_advertisement_phone)
def check_phone(message):
     if(message.text.lower()=="так"):
          sent = bot.send_message(message.chat.id, "Вкажіть свій номер телефону:")
          bot.register_next_step_handler(sent, save_advertisement_phone)
     else:
         bot.send_message(message.chat.id, "Оголошення успішно створено✅")



def get_all_announcement_requests():    
    return list(db.announcements.find())

def get_announcement_documents(user):
    filter = {}
    if(user["announcement_filtering"][0] != False):
        filter['location_region'] = user["announcement_filtering"][0]
    if(user["announcement_filtering"][1] != False):
        filter['location_district'] = user["announcement_filtering"][1]
    if(user["announcement_filtering"][2] != False):
        filter['location_city'] = user["announcement_filtering"][2]
    if(user["announcement_filtering"][3] != False):
        regex = re.compile('^' + user["announcement_filtering"][3] + '[а-яА-ЯЄєЇїІіҐґ]+', re.IGNORECASE | re.UNICODE)
        filter['full_name'] = {'$regex': regex}
    if(user["announcement_filtering"][0] == False and user["announcement_filtering"][1] == False and user["announcement_filtering"][2] == False and user["announcement_filtering"][3] == False):
        filter = {}

    return list(db.announcements.find(filter))

def build_announcement_text(documents, index):
    result_string=""
    document = documents[index]
    announcement_region = document.get('location_region')
    announcement_district = document.get('location_district')
    announcement_city = document.get('location_city')
    announcement_full_name = document.get('full_name')
    announcement_details = document.get('details')
    
    result_string += f"Область: {announcement_region}\n"
    result_string += f"Район: {announcement_district}\n"
    result_string += f"Місто: {announcement_city}\n"
    result_string += f"ПІБ: {announcement_full_name}\n"
    result_string += f"Деталі: {announcement_details}\n"
    result_string += "---\n"
    return result_string
    
def announcement_markup_creation():
    kb = types.InlineKeyboardMarkup(row_width=2)
    btn_respond = types.InlineKeyboardButton(text= 'Відгукнутись', callback_data='advertisement_respond')
    btn_next = types.InlineKeyboardButton(text='Далі', callback_data='advertisement_next')
    btn_previous = types.InlineKeyboardButton(text='Назад', callback_data='advertisement_previous')
    btn_filter_region =  types.InlineKeyboardButton(text='Фільтрування за областю', callback_data='advertisement_filter_region')
    btn_filter_district =  types.InlineKeyboardButton(text='Фільтрування за районом', callback_data='advertisement_filter_district')
    btn_filter_city =  types.InlineKeyboardButton(text='Фільтрування за містом', callback_data='advertisement_filter_city')
    btn_filter_full_name =  types.InlineKeyboardButton(text='Фільтрування за прізвищем', callback_data='advertisement_filter_full_name')
    btn_cancel_filter = types.InlineKeyboardButton(text='Скасувати обрані фільтри', callback_data='advertisement_cancel_filter')
    kb.row(btn_previous,btn_next)
    kb.row(btn_respond)
    kb.row(btn_filter_region,btn_filter_district)
    kb.row(btn_filter_city,btn_filter_full_name)
    kb.row(btn_cancel_filter)
    return kb
    

def announcement_view(message):
    documents = get_all_announcement_requests()
    user = db.get_user(message.chat.id)
    index = 0
    db.set_user(message.chat.id, {"announcement_index": 0, "announcement_filtering":[False,False,False,False]})
    result_string = build_announcement_text(documents,index)
    photo = documents[index].get('photo')
    bot.send_photo(message.chat.id, photo, caption=f'{result_string}', reply_markup= announcement_markup_creation())
    
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_next") 
def next_step_adv(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["announcement_index"]
    documents = get_announcement_documents(user)
    
    if(index!= len(documents)-1):
        index = index + 1
        db.set_user(callback.message.chat.id, {"announcement_index": index})
        photo = documents[index].get('photo')
        result_string = build_announcement_text(documents, index)
        updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
        bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= announcement_markup_creation() )
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі cвої заявки ✅')
        return
    
    
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_previous") 
def previous_step_adv(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["announcement_index"]
    documents = get_announcement_documents(user)
    
    if(index!= 0):
        index = index - 1
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі cвої заявки ✅')
        return
    db.set_user(callback.message.chat.id, {"announcement_index": index})
    photo = documents[index].get('photo')
    result_string = build_announcement_text(documents, index)
    updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
    bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= announcement_markup_creation() )
    
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_respond")
def respond(callback):
    user = db.get_user(callback.message.chat.id)
    index = user["announcement_index"]
    documents = get_announcement_documents(user)
    getted_id = documents[index].get('chat_id')
    getted_another_user = db.get_user(getted_id)
    getted_number = getted_another_user["phone_number"]
    sent = bot.send_message(callback.message.chat.id, 'Вкажіть деталі, які вам відомо стосовно зникнення цієї людини:')
    bot.register_next_step_handler(sent, lambda msg: send_details(msg,getted_id,getted_number))
    
def send_details(message,getted_id,getted_number):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["announcement_index"]
    documents = get_announcement_documents(user)
    photo = documents[index].get('photo')
    result_string = build_announcement_text(documents, index)
    bot.send_message(message.chat.id, f'Дякуємо за інформацію!')
    if(user["phone_number"]!=False):
        sent = bot.send_message(message.chat.id, f'Збережена відповідь номер телефону: {user["phone_number"]}. Чи змінилися Ваші дані?')
        bot.register_next_step_handler(sent, lambda msg: check_answer_advertisement_phone(msg,getted_id,getted_number,result_string,photo,user["phone_number"],message_to_save))
    else:
        sent = bot.send_message(message.chat.id, 'Вкажіть Ваш номер телефону:')
        bot.register_next_step_handler(sent, lambda msg: save_phone(msg,getted_id,getted_number,result_string,photo))
   
def check_answer_advertisement_phone(message,getted_id,getted_number,result_string,photo,phone,details):
    if(message.text.lower()=="так"):
        sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону:')
        bot.register_next_step_handler(sent,lambda msg: save_phone(msg,getted_id,getted_number,result_string,photo))
    else:
        bot.send_message(message.chat.id, f'Номер телефону особи, що подала заявку: {getted_number}')
        bot.send_photo(getted_id, photo, caption=f'На ваше оголошення: {result_string} відгукнувся контакт з номером {phone} і залишив повідомлення: {details}')

def save_phone(message,getted_id,getted_number,result_string,photo):
    message_to_save = message.text
    if(is_valid_phone_number(message_to_save)):
        db.set_user(message.chat.id, {"phone_number": message_to_save})
        bot.send_message(message.chat.id, f'Номер телефону особи, що подала заявку: {getted_number}')
        bot.send_photo(getted_id, photo, caption=f'На ваше оголошення: {result_string} відгукнувся контакт з номером {phone} і залишив повідомлення: {details}')
    else:
        sent = bot.reply_to(message, 'На жаль введений номер не є валідним. Перевірте будь ласка правильність написання та вкажіть номер ще раз:')
        bot.register_next_step_handler(sent, lambda msg: save_phone(msg,getted_id,getted_number,result_string,photo))



def get_announcement_filter(getted_id):
    db.set_user(getted_id, {'announcement_index': 0})
    user = db.get_user(getted_id)
    index = 0
    documents = get_announcement_documents(user)
    result_string = build_announcement_text(documents,index)
    photo = documents[index].get('photo')
    bot.send_photo(getted_id, photo, caption=f'{result_string}', reply_markup= announcement_markup_creation())

    
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_filter_region") 
def advertisement_filter_region(callback):
    bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть область')
    bot.register_next_step_handler(sent, advertisement_get_region)
    
    
def advertisement_get_region(message):
    getted_message = message.text
    db.set_user(message.chat.id, {"announcement_index":0, f'announcement_filtering.0': getted_message})
    get_announcement_filter(message.chat.id)
 
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_filter_district") 
def advertisement_filter_district(callback):
    bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть район')
    bot.register_next_step_handler(sent, advertisement_get_district)
    
    
def advertisement_get_district(message):
    getted_message = message.text
    db.set_user(message.chat.id, {"announcement_index":0, f'announcement_filtering.1': getted_message})
    get_announcement_filter(message.chat.id)
    
@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_filter_city") 
def advertisement_filter_city(callback):
    bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть населений пункт')
    bot.register_next_step_handler(sent, advertisement_get_city)
    
    
def advertisement_get_city(message):
    getted_message = message.text
    db.set_user(message.chat.id, {"announcement_index":0, f'announcement_filtering.2': getted_message})
    get_announcement_filter(message.chat.id)
    

@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_filter_full_name") 
def advertisement_filter_category(callback):
    bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
    sent = bot.send_message(callback.message.chat.id, f'Вкажіть прізвище')
    bot.register_next_step_handler(sent, advertisement_get__full_name)
    
    
def advertisement_get__full_name(message):
    getted_message = message.text
    db.set_user(message.chat.id, {"announcement_index":0, f'announcement_filtering.3': getted_message})
    get_announcement_filter(message.chat.id)

@bot.callback_query_handler(func=lambda callback: callback.data == "advertisement_cancel_filter") 
def advertisement_cancel_filter(callback):
    bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
    bot.send_message(chat_id=callback.message.chat.id, text="Всі обрані попередні фільтри скасовано")
    db.set_user(callback.message.chat.id, {"announcement_index":0,"announcement_filtering.0": False, "announcement_filtering.1": False, "announcement_filtering.2": False, "announcement_filtering.3": False})
    get_announcement_filter(callback.message.chat.id)

def inline_markup__my_advertisement():
    kb = types.InlineKeyboardMarkup(row_width=2)
    btn_next = types.InlineKeyboardButton(text='Далі', callback_data='next_advertisement_request')
    btn_previous = types.InlineKeyboardButton(text='Назад', callback_data='previous_advertisement_request')
    btn_update =  types.InlineKeyboardButton(text='Редагувати', callback_data='update_advertisement_request')
    btn_cancel =  types.InlineKeyboardButton(text='Скасувати', callback_data='cancel_advertisement_request')
    kb.row(btn_previous,btn_next)
    kb.row(btn_update,btn_cancel)
    return kb

def build_my_advertisement_requsests_text(getted_id, my_announcement_requests_index):
    result_string=""
    announcements = db.get_announcements(getted_id)
    user = db.get_user(getted_id)
    if(len(announcements)!=0):
        document = announcements[my_announcement_requests_index]
        announcement_region = document.get('location_region')
        announcement_district = document.get('location_district')
        announcement_city = document.get('location_city')
        announcement_full_name = document.get('full_name')
        announcement_details = document.get('details')
        user_phone = user["phone_number"]
        
        result_string += f"Область: {announcement_region}\n"
        result_string += f"Район: {announcement_district}\n"
        result_string += f"Місто: {announcement_city}\n"
        result_string += f"ПІБ: {announcement_full_name}\n"
        result_string += f"Деталі: {announcement_details}\n"
        result_string += f"Номер телефону: {user_phone}\n"
        result_string += "---\n"
        return result_string


def my_advertisement_requests(message):
    result_string = build_my_advertisement_requsests_text(message.chat.id, 0)
    if(result_string != None):
        documents=db.get_announcements(message.chat.id)
        photo = documents[0].get('photo')
        bot.send_photo(message.chat.id, photo, caption=f'{result_string}', reply_markup= inline_markup__my_advertisement())
        db.set_user(message.chat.id, {"my_announcement_requests_index":0})
    else:
        bot.send_message(message.chat.id, text="У вас немає заявок")
    

@bot.callback_query_handler(func=lambda callback: callback.data == "next_advertisement_request") 
def next_step_adv_req(callback):
    user = db.get_user(callback.message.chat.id)
    documents=db.get_announcements(callback.message.chat.id)
    index = user["my_announcement_requests_index"]
    if(index!= len(documents)-1):
        index = index + 1
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі cвої заявки !')
        return
    db.set_user(callback.message.chat.id, {"my_announcement_requests_index": index})
    #result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    photo = documents[index].get('photo')
    result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
    bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= inline_markup__my_advertisement() )
    
@bot.callback_query_handler(func=lambda callback: callback.data == "previous_advertisement_request") 
def previous_step_adv_req(callback):
    user = db.get_user(callback.message.chat.id)
    documents=db.get_announcements(callback.message.chat.id)
    index = user["my_announcement_requests_index"]
    if(index!= 0):
        index = index - 1
    else:
        bot.send_message(callback.message.chat.id,'Ви переглянули всі cвої заявки ✅')
        return
    db.set_user(callback.message.chat.id, {"my_announcement_requests_index": index})
    #result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    photo = documents[index].get('photo')
    result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
    bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= inline_markup__my_advertisement() )

@bot.callback_query_handler(func=lambda callback: callback.data == "cancel_advertisement_request") 
def cancel_advertisement_request(callback):
    user = db.get_user(callback.message.chat.id)
    documents=db.get_announcements(callback.message.chat.id)
    index = user["my_announcement_requests_index"]
    if index >= 0 and index < len(documents):
        document = documents[index]
        document_id = document['_id']
        db.announcements.delete_one({'_id': document_id})
               
        documents = db.announcements.find({'chat_id': callback.message.chat.id}).sort('index_announcement', 1)
        if(len(list(documents))!=0):
            for i, document in enumerate(documents):
                db.announcements.update_one({'_id': document['_id']}, {'$set': {'index_announcement': i}})
            db.set_user(callback.message.chat.id, {"my_announcement_requests_index": 0}) 
            user = db.get_user(callback.message.chat.id)
            index = user["my_announcement_requests_index"]
            documents=db.get_announcements(callback.message.chat.id)
            #result_string = build_my_requsests_text(callback.message.chat.id, index)
            photo = documents[index].get('photo')
            result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
            updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
            bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= inline_markup__my_advertisement() )
        else:
            bot.delete_message(chat_id=callback.message.chat.id,message_id=callback.message.message_id)
            bot.send_message(chat_id=callback.message.chat.id, text="У вас немає оголошень")
        return True
    else:
        return False
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_request") 
def update_request(callback):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn_place = types.InlineKeyboardButton(text='Змінити місце ', callback_data='update_advertisement_place')
    btn_number = types.InlineKeyboardButton(text='Змінити номер телефону', callback_data='update_advertisement_number')
    btn_full_name =  types.InlineKeyboardButton(text='Змінити ПІБ', callback_data='update_advertisement_full_name')
    btn_details =  types.InlineKeyboardButton(text='Змінити деталі', callback_data='update_advertisement_details')
    btn_photo =  types.InlineKeyboardButton(text='Змінити фото', callback_data='update_advertisement_photo')
    btn_previous =  types.InlineKeyboardButton(text='Повернутись назад', callback_data='update_advertisement_previous')
    kb.add(btn_place,btn_number,btn_full_name,btn_photo, btn_details,btn_previous)
    
    user = db.get_user(callback.message.chat.id)
    index = user["my_announcement_requests_index"]
    documents=db.get_announcements(callback.message.chat.id)
    photo = documents[index].get('photo')
    result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
    bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= kb )
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_place") 
def update_advertisement_place(callback):
   sent = bot.send_message(callback.message.chat.id, "Вкажіть Вашу область:")
   bot.register_next_step_handler(sent, changed_advertisement_region)

def changed_advertisement_region(message):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["my_announcement_requests_index"]
    db.set_announcement(message.chat.id,index,{"location_region":message_to_save})
    sent = bot.send_message(message.chat.id, "Вкажіть Ваш район:")
    bot.register_next_step_handler(sent, changed_advertisement_district)

def changed_advertisement_district(message):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["my_announcement_requests_index"]
    db.set_announcement(message.chat.id,index,{"location_district":message_to_save})
    sent = bot.send_message(message.chat.id, "Вкажіть Ваш населений пункт:")
    bot.register_next_step_handler(sent, changed_advertisement_city)
    
def changed_advertisement_city(message):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["my_announcement_requests_index"]
    db.set_announcement(message.chat.id,index,{"location_city":message_to_save})
    bot.send_message(message.chat.id, "Дані успішно змінено✅")
    
    
   
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_number") 
def update_advertisement_phone(callback):
    sent = bot.send_message(callback.message.chat.id, "Вкажіть Ваш номер телефону:")
    bot.register_next_step_handler(sent, changed_advertisement_phone)
    
def changed_advertisement_phone(message):
    message_to_save = message.text
    db.set_user(message.chat.id, {"phone_number": message_to_save})
    bot.send_message(message.chat.id, "Дані успішно змінено✅")
    
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_details") 
def update_advertisement_details(callback):
    sent = bot.send_message(callback.message.chat.id, "Вкажіть деталі:")
    bot.register_next_step_handler(sent, changed_advertisement_details)
    
def changed_advertisement_details(message):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["my_announcement_requests_index"]
    db.set_announcement(message.chat.id,index,{"details":message_to_save})
    bot.send_message(message.chat.id, "Дані успішно змінено✅")
    
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_full_name") 
def update_advertisement_details(callback):
    sent = bot.send_message(callback.message.chat.id, "Вкажіть ПІБ:")
    bot.register_next_step_handler(sent, changed_advertisement_details)
    
def changed_advertisement_details(message):
    message_to_save = message.text
    user = db.get_user(message.chat.id)
    index = user["my_announcement_requests_index"]
    db.set_announcement(message.chat.id,index,{"full_name":message_to_save})
    bot.send_message(message.chat.id, "Дані успішно змінено✅")
    
@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_photo") 
def update_advertisement_photo(callback):
    sent = bot.send_message(callback.message.chat.id, "Завантажте фото:")
    bot.register_next_step_handler(sent, changed_advertisement_photo)
    
def changed_advertisement_photo(message):
    if message.content_type == 'photo':  
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        user = db.get_user(message.chat.id)
        index = user["my_announcement_requests_index"]
        downloaded_file = bot.download_file(file_path)
        db.set_announcement(message.chat.id,index,{"file_id":file_id, "file_path":file_path, "photo":downloaded_file})
        bot.reply_to(message, "Фото було збережено✅!")
        user = db.get_user(message.chat.id)
    else:
        sent = bot.reply_to(message, "Будь ласка, надішліть фото.")
        bot.register_next_step_handler(sent, changed_advertisement_photo)
    

@bot.callback_query_handler(func=lambda callback: callback.data == "update_advertisement_previous") 
def update_advertisement_previous(callback):
    bot.send_message(callback.message.chat.id, "Вже повертаємось🔙")
    user = db.get_user(callback.message.chat.id)
    index = user["my_announcement_requests_index"]
    documents=db.get_announcements(callback.message.chat.id)
    photo = documents[index].get('photo')
    result_string = build_my_advertisement_requsests_text(callback.message.chat.id, index)
    updated_media = types.InputMediaPhoto(media=photo, caption=f'{result_string}')
    bot.edit_message_media(media= updated_media, chat_id=callback.message.chat.id, message_id = callback.message.id,reply_markup= inline_markup__my_advertisement())
    



@bot.message_handler(commands=['start'])
def start_message(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Привіт, {user_name} 👋 Я Мавка, твоя помічниця під час війни')
    bot.send_message(message.chat.id,'Чим можу допомогти?',reply_markup = menu.main_menu())
    user = db.get_user(message.chat.id)
    
@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Перша медична допомога":
        bot.send_message(message.chat.id,'Вкажіть точніше, яку саме інформацію Ви шукаєте 🔜',reply_markup= menu.medical_menu())
    elif message.text=="Головне меню":
        bot.send_message(message.chat.id,'Вже повертаємось 🔙',reply_markup= menu.main_menu())
    elif message.text=="Безпека":
        bot.send_message(message.chat.id,'Вкажіть точніше, яку саме інформацію Ви шукаєте 🔜',reply_markup= menu.safe_menu())
    elif message.text=="Допомога":
        bot.send_message(message.chat.id,'Вкажіть точніше, яку саме інформацію Ви шукаєте 🔜',reply_markup= menu.help_menu())
    elif message.text=="Можу допомогти":
         can_help(message)
    elif message.text=="Потребую допомоги":
         createHelp.help_item(bot, message)
    elif message.text=="Мої заявки":
         my_requests(message)
    elif message.text=="Оголошення":
        bot.send_message(message.chat.id,'Вкажіть точніше, яку саме інформацію Ви шукаєте 🔜',reply_markup=menu.advertisement_menu())
    elif message.text=="Переглянути оголошення":  
         announcement_view(message)
    elif message.text=="Додати оголошення":   
         save_advertisement_region(message)
    elif message.text=="Мої оголошення":   
         my_advertisement_requests(message)
    elif message.text=="Карта повітряних тривог":
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Карта повітряних тривог", url='https://war.ukrzen.in.ua/alerts/')
        markup.add(button)
        bot.send_message(message.chat.id, "Будьте обачні та обережні 😉"+ '\n'+ "Перейдіть за посиланням 👇", reply_markup = markup)
    elif message.text=="Корисні посилання":
        res_text="Тут Ви можете знайти всю необхідну інформацію і навіть більше 👇"
        markup =  menu.useful_links()
        bot.send_message(message.chat.id, res_text, reply_markup = markup)
    elif message.text=="Про бота":
        information = "Цей бот створено для надання допомоги під час війни.\n" \
              "Ви можете переглядати корисну інформацію з розділів, залишати заявки про допомогу чи пошук зниклих людей, а також обмінятися контактами з тими, кому маєте змогу допомогти.\n" \
              "Для обміну контактами слід скористатися опцією Відгукнутися, не будьмо байдужими!\n" \
              "Важливо❗️ Не вказуйте і не повідомляйте детальної інформації про себе, такої як паспортні дані, дані карток, точну адресу тощо!\n" \
              "Бот функціонує завдяки небайдужим людям, однак ми не можемо гарантувати відсутність людей з лихими намірами 😢\n" \
              "Тож будьте обережні та обачні!"

        bot.send_message(message.chat.id,information,reply_markup= menu.main_menu())
    else:
        get_info(message)
bot.infinity_polling()