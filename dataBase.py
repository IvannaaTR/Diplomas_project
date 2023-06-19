# -*- coding: utf-8 -*-
from pymongo import MongoClient
class DataBase:
    def __init__(self):
        cluster = MongoClient("connection_string")
        self.db = cluster["MavkaDB"]
        self.users = self.db["User"]
        self.announcements = self.db["Announcements"]
        self.medical_help = self.db["MedicalHelp"]
        self.minesSafety_help = self.db["MinesSafety"]
        
    def get_user(self, chat_id):
        user = self.users.find_one({"chat_id":chat_id})
        
        if user is not None:
            return user
        
        user = {
            "chat_id" : chat_id,
            "phone_number":False,
            "location_region":False,
            "location_district":False,
            "location_city":False
        }
        self.users.insert_one(user)
        return user
    def create_announcement(self, chat_id, index):
        announcement = {
            "chat_id" : chat_id,
            "index_announcement":index, 
            "location_region":False,
            "location_district":False,
            "location_city":False,
            "full_name": False,
            "details":False,
            "file_id":False,
            "file_path":False,
            "photo": False,
        }
        self.announcements.insert_one(announcement)
        return announcement
    def get_announcement(self, chat_id, index):
        announcement = self.announcements.find_one({"chat_id":chat_id, "index_announcement":index})
        return announcement
    def get_announcements(self, chat_id):
        filter = {
        "chat_id":chat_id
        }
        return list(self.announcements.find(filter))
    def set_announcement(self, chat_id,index, update):
        self.announcements.update_one({"chat_id":chat_id,"index_announcement":index},{"$set":update}) 
    def set_user(self, chat_id, update):
        self.users.update_one({"chat_id":chat_id},{"$set":update})
    def delete_user(self, chat_id, update):
        self.users.update_one({"chat_id":chat_id},{"$set":update})
    def get_medical_info(self,title):
        return self.medical_help.find_one({"title":title})
    def get_minesSafety_info(self,title):
        return self.minesSafety_help.find_one({"title":title})