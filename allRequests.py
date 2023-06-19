from dataBase import DataBase
from telebot import types

db = DataBase()

class allRequests:
    def get_all_requests(self,value):
        filter = {
        'need_help': True,
        'chat_id': {'$ne': value}
        }
        return db.users.find(filter)
    
    def get_documents(self,user):
        filter = {}
        answer='Використовується фільтрування: \n'
        if(user["filtering"][0] != False):
            answer+="Область: "+user["filtering"][0]+"\n"
            filter['need_help'] = True
            filter['location_region'] = user["filtering"][0]
            filter['chat_id'] = {'$ne': user["chat_id"]}
        if(user["filtering"][1] != False):
            answer+="Район: " + user["filtering"][1]+"\n"
            filter['need_help'] = True
            filter['location_district'] = user["filtering"][1]
            filter['chat_id'] = {'$ne': user["chat_id"]}
        if(user["filtering"][2] != False):
            answer+="Місто: "+user["filtering"][2]+"\n"
            filter['need_help'] = True
            filter['location_city'] = user["filtering"][2]
            filter['chat_id'] = {'$ne': user["chat_id"]}
        if(user["filtering"][3] != False):
            answer+="Категорія: "+user["filtering"][3]+"\n"
            filter['need_help'] = True
            filter['requests.category']= user["filtering"][3]
            filter['chat_id'] = {'$ne': user["chat_id"]}
        if(user["filtering"][0] == False and user["filtering"][1] == False and user["filtering"][2] == False and user["filtering"][3] == False):
            filter['need_help'] = True
            filter['chat_id'] = {'$ne': user["chat_id"]}
            
    
        return list(db.users.find(filter)),answer
    
    def build_button_text(self,documents, index1, index2):
        result_string=""
        document = documents[index1]
        user_region = document.get('location_region')
        user_district = document.get('location_district')
        user_city = document.get('location_city')
        user_category = document["requests"][index2].get("category")
        user_details = document["requests"][index2].get("details")
        
        result_string += f"Область: {user_region}\n"
        result_string += f"Район: {user_district}\n"
        result_string += f"Місто: {user_city}\n"
        result_string += f"Категорія допомоги: {user_category}\n"
        result_string += f"Деталі: {user_details}\n"
        result_string += "---\n"
        return result_string
    
    def inline_markup_creation(self):
        kb = types.InlineKeyboardMarkup(row_width=2)
        btn_respond = types.InlineKeyboardButton(text= 'Відгукнутись', callback_data='respond')
        btn_next = types.InlineKeyboardButton(text='Далі', callback_data='next')
        btn_previous = types.InlineKeyboardButton(text='Назад', callback_data='previous')
        btn_filter_region =  types.InlineKeyboardButton(text='Фільтрування за областю', callback_data='filter_region')
        btn_filter_district =  types.InlineKeyboardButton(text='Фільтрування за районом', callback_data='filter_district')
        btn_filter_city =  types.InlineKeyboardButton(text='Фільтрування за містом', callback_data='filter_city')
        btn_filter_category =  types.InlineKeyboardButton(text='Фільтрування за категорією', callback_data='filter_category')
        btn_cancel_filter = types.InlineKeyboardButton(text='Скасувати обрані фільтри', callback_data='cancel_filter')
        kb.row(btn_previous,btn_next)
        kb.row(btn_respond)
        kb.row(btn_filter_region,btn_filter_district)
        kb.row(btn_filter_city,btn_filter_category)
        kb.row(btn_cancel_filter)
        return kb
        
