from dataBase import DataBase
import phonenumbers

db = DataBase()
def is_valid_phone_number(phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False


def check_name(mes):
        regions = [
           "Вінницька",
           "Волинська",
           "Дніпропетровська",
           "Донецька",
           "Житомирська",
           "Закарпатська",
           "Запорізька",
           "Івано-Франківська",
           "Київська",
           "Кіровоградська",
           "Луганська",
           "Львівська",
           "Миколаївська",
           "Одеська",
           "Полтавська",
           "Рівненська",
           "Сумська",
           "Тернопільська",
           "Харківська",
           "Херсонська",
           "Хмельницька",
           "Черкаська",
           "Чернівецька",
           "Чернігівська",
           "Автономна Республіка Крим"]
        if mes in regions:
            return True
        else:
            return False
def check_categories(mes):
    categories=[
        "Продукти",
        "Одяг",
        "Транспорт",
        "Паливо",
        "Житло",
        "Інше"]
    if mes in categories:
        return True
    else:
        return False
class CreateHelpItem:
    def help_item(self, bot, message):
        if(message.text == "Потребую допомоги"):
            user = db.get_user(message.chat.id)
            if(user["location_region"] == False):
                db.set_user(message.chat.id, {"need_help": True})
                sent = bot.reply_to(message, 'Вкажіть Вашу область')
                bot.register_next_step_handler(sent, lambda msg: self.save_region(bot, msg))
            else:
                sent = bot.reply_to(message, f'Збережена відповідь область: {user["location_region"]}. Чи змінилися Ваші дані?')
                bot.register_next_step_handler(sent, lambda msg: self.check_answer_region(bot, msg))
    def check_answer_region(self, bot, message):
        if(message.text.lower()=="так"):
            db.set_user(message.chat.id, {"isDataUpdated": True})
            sent = bot.reply_to(message, 'Вкажіть Вашу область')
            bot.register_next_step_handler(sent, lambda msg: self.save_region(bot, msg))
        else:
            user = db.get_user(message.chat.id)
            if(user["location_district"] == False or user["isDataUpdated"] == True):
               sent = bot.reply_to(message, 'Вкажіть район')
               bot.register_next_step_handler(sent, lambda msg: self.save_district(bot, msg))
            else:
                sent = bot.reply_to(message, f'Збережена відповідь район: {user["location_district"]}. Чи змінилися Ваші дані?')
                bot.register_next_step_handler(sent, lambda msg: self.check_answer_district(bot, msg))
    
    def save_region(self, bot, message):
        message_to_save = message.text
        if(check_name(message_to_save)==True):
            db.set_user(message.chat.id, {"location_region": message_to_save})
            user = db.get_user(message.chat.id)
            if(user["location_district"] == False or user["isDataUpdated"] == True):
               sent = bot.reply_to(message, 'Вкажіть район')
               bot.register_next_step_handler(sent, lambda msg: self.save_district(bot, msg))
            else:
                sent = bot.reply_to(message, f'Збережена відповідь район: {user["location_district"]}. Чи змінилися Ваші дані?')
                bot.register_next_step_handler(sent, lambda msg: self.check_answer_district(bot, msg))
        else:
            sent = bot.reply_to(message, 'На жаль не вдалося знайти таку область.Перевірте будь ласка правильність написання та вкажіть назву області ще раз:')
            bot.register_next_step_handler(sent, lambda msg: self.save_region(bot, msg))
            
    def check_answer_district(self, bot, message):
        if(message.text.lower()=="так"):
            db.set_user(message.chat.id, {"isDataUpdated": True})
            sent = bot.reply_to(message, 'Вкажіть район')
            bot.register_next_step_handler(sent, lambda msg: self.save_district(bot, msg))
        else:
            user = db.get_user(message.chat.id)
            if(user["location_city"] == False or user["isDataUpdated"] == True):
                sent = bot.reply_to(message, 'Вкажіть населений пункт')
                bot.register_next_step_handler(sent, lambda msg: self.save_city(bot, msg))
            else:
                sent = bot.reply_to(message, f'Збережена відповідь населений пункт: {user["location_city"]}. Чи змінилися Ваші дані?')
                bot.register_next_step_handler(sent, lambda msg: self.check_answer_city(bot, msg))
    
    def save_district(self, bot, message):
        message_to_save = message.text
        db.set_user(message.chat.id, {"location_district": message_to_save})
        user = db.get_user(message.chat.id)
        if(user["location_city"] == False or user["isDataUpdated"] == True):
            sent = bot.reply_to(message, 'Вкажіть населений пункт')
            bot.register_next_step_handler(sent, lambda msg: self.save_city(bot, msg))
        else:
            sent = bot.reply_to(message, f'Збережена відповідь населений пункт: {user["location_city"]}. Чи змінилися Ваші дані?')
            bot.register_next_step_handler(sent, lambda msg: self.check_answer_city(bot, msg))
            
    def check_answer_city(self, bot, message):
        if(message.text.lower()=="так"):
            db.set_user(message.chat.id, {"isDataUpdated": True})
            sent = bot.reply_to(message, 'Вкажіть населений пункт')
            bot.register_next_step_handler(sent, lambda msg: self.save_city(bot, msg))
        else:
            user = db.get_user(message.chat.id)
            if(user["phone_number"] == False):
                sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону')
                bot.register_next_step_handler(sent, lambda msg: self.save_phone(bot, msg))
            else:
                sent = bot.reply_to(message, f'Збережена відповідь номер телефону: {user["phone_number"]}. Чи змінилися Ваші дані?')
                bot.register_next_step_handler(sent, lambda msg: self.check_answer_phone(bot, msg))
            
    def save_city(self, bot, message):
        message_to_save = message.text
        db.set_user(message.chat.id, {"location_city": message_to_save})
        db.set_user(message.chat.id,{"isDataUpdated": False})
        user = db.get_user(message.chat.id)
        if(user["phone_number"] == False):
            sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону')
            bot.register_next_step_handler(sent, lambda msg: self.save_phone(bot, msg))
        else:
            sent = bot.reply_to(message, f'Збережена відповідь номер телефону: {user["phone_number"]}. Чи змінилися Ваші дані?')
            bot.register_next_step_handler(sent, lambda msg: self.check_answer_phone(bot, msg))
            
            
    def check_answer_phone(self, bot, message):
        if(message.text.lower()=="так"):
            sent = bot.reply_to(message, 'Вкажіть Ваш номер телефону')
            bot.register_next_step_handler(sent,lambda msg: self.save_phone(bot, msg))
        else:
            sent = bot.reply_to(message, 'Вкажіть категорію допомоги: Продукти, Одяг, Транспорт, Паливо, Житло, Інше')
            bot.register_next_step_handler(sent, lambda msg: self.save_category(bot, msg))
    def save_phone(self, bot, message):
        message_to_save = message.text
        if(is_valid_phone_number(message_to_save)):
            db.set_user(message.chat.id, {"phone_number": message_to_save})
            sent = bot.reply_to(message, 'Вкажіть категорію допомоги: Продукти, Одяг, Транспорт, Паливо, Житло, Інше')
            bot.register_next_step_handler(sent, lambda msg: self.save_category(bot, msg))
        else:
            sent = bot.reply_to(message, 'На жаль введений номер не є валідним. Перевірте будь ласка правильність написання та вкажіть номер ще раз:')
            bot.register_next_step_handler(sent, lambda msg: self.save_phone(bot, msg))
        
    def save_category(self, bot, message):
        message_to_save = message.text
        if(check_categories(message_to_save)==True):
            user = db.get_user(message.chat.id)
            if "requests" not in user:
                user["requests"] = []
            user["requests"].append({"category": message_to_save})
            db.set_user(message.chat.id, {"requests": user["requests"]})
            sent = bot.reply_to(message, 'Вкажіть деталі допомоги наприклад, які розміри одягу потрібні, тощо')
            bot.register_next_step_handler(sent,lambda msg: self.save_details(bot, msg) )
        else:
            sent = bot.reply_to(message, 'На жаль категорія введена неправильно. Перевірте будь ласка правильність написання та вкажіть категорію ще раз:')
            bot.register_next_step_handler(sent, lambda msg: self.save_category(bot, msg))
        
    def save_details(self, bot, message):
        message_to_save = message.text
        user = db.get_user(message.chat.id)
        last_index = len(user["requests"]) - 1
        user["requests"][last_index]["details"] = message_to_save
        db.set_user(message.chat.id, {"requests": user["requests"]})
        bot.reply_to(message, 'Ваші відповіді збережено. Очікуйте, людина, яка зможе Вам допомогти зв*яжеться з Вами')