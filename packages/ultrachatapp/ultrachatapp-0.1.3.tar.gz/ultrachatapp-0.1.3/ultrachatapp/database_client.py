# #conection on a mongo DB



# import json
# from typing import List, Dict, Any
# from datetime import datetime


# class DatabaseClient:
#     def __init__(self, file_path: str = "data.json"):
#         self.file_path = file_path
#         self.data = self._load_data()

#     def _load_data(self) -> List[Dict[str, Any]]:
#         try:
#             with open(self.file_path, 'r') as file:
#                 return json.load(file)
#         except FileNotFoundError:
#             return []
#         except json.JSONDecodeError:
#             raise ValueError("Invalid JSON format in the file.")

#     def _save_data(self) -> None:
#         with open(self.file_path, 'w') as file:
#             json.dump(self.data, file, indent=4)

#     def get_all_records(self) -> List[Dict[str, Any]]:
#         return self.data

#     def add_message(self, sender_id: str, receiver_id: str, message: str, status: str = "sent") -> None:
#         timestamp = datetime.utcnow().isoformat() + "Z"

#         for record in self.data:
#             if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
#                 record['messages'].append({
#                     "message": message,
#                     "timestamp": timestamp,
#                     "status": status
#                 })
#                 self._save_data()
#                 return

#         new_record = {
#             "sender_id": sender_id,
#             "receiver_id": receiver_id,
#             "messages": [
#                 {
#                     "message": message,
#                     "timestamp": timestamp,
#                     "status": status
#                 }
#             ],
#             "encryption": "AES256"
#         }
#         self.data.append(new_record)
#         self._save_data()

#     def update_message(self, sender_id: str, receiver_id: str, old_message: str, new_message: str) -> bool:
#         for record in self.data:
#             if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
#                 for msg in record['messages']:
#                     if msg['message'] == old_message:
#                         msg['message'] = new_message
#                         msg['timestamp'] = datetime.utcnow().isoformat() + "Z"
#                         self._save_data()
#                         return True
#         return False

#     def delete_message(self, sender_id: str, receiver_id: str, message: str) -> bool:
#         for record in self.data:
#             if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
#                 record['messages'] = [msg for msg in record['messages'] if msg['message'] != message]
#                 self._save_data()
#                 return True
#         return False

#     def delete_record(self, sender_id: str, receiver_id: str) -> bool:
#         self.data = [record for record in self.data if not (record['sender_id'] == sender_id and record['receiver_id'] == receiver_id)]
#         self._save_data()
#         return True

# from pymongo import MongoClient
# from datetime import datetime
# from typing import List, Dict, Any




# class MongoDBClient:
#     def __init__(self, db_name: str = "chat_db", collection_name: str = "messages", 
#                  uri: str = "mongodb+srv://Acro12123:qF4JTS5Kgm7FUIat@chatcluster.ym1eztb.mongodb.net/?retryWrites=true&w=majority&appName=ChatCluster"):
#         self.client = MongoClient(uri)
#         self.db = self.client[db_name]
#         self.collection = self.db[collection_name]

#     def get_all_records(self) -> List[Dict[str, Any]]:
#         return list(self.collection.find({}, {"_id": 0}))
    

#     def add_message(self, sender_id: str, receiver_id: str, message: str, status: str = "sent") -> None:
#         timestamp = datetime.utcnow().isoformat() + "Z"
        
#         existing_chat = self.collection.find_one({"sender_id": sender_id, "receiver_id": receiver_id})
        
#         if existing_chat:
#             self.collection.update_one(
#                 {"sender_id": sender_id, "receiver_id": receiver_id},
#                 {"$push": {"messages": {"message": message, "timestamp": timestamp, "status": status}}}
#             )
#         else:
#             new_record = {
#                 "sender_id": sender_id,
#                 "receiver_id": receiver_id,
#                 "messages": [{"message": message, "timestamp": timestamp, "status": status}],
#                 "encryption": "AES256"
#             }
#             self.collection.insert_one(new_record)

#     def update_message(self, sender_id: str, receiver_id: str, old_message: str, new_message: str) -> bool:
#         timestamp = datetime.utcnow().isoformat() + "Z"
        
#         result = self.collection.update_one(
#             {"sender_id": sender_id, "receiver_id": receiver_id, "messages.message": old_message},
#             {"$set": {"messages.$.message": new_message, "messages.$.timestamp": timestamp}}
#         )
        
#         return result.modified_count > 0

#     def delete_message(self, sender_id: str, receiver_id: str, message: str) -> bool:
#         result = self.collection.update_one(
#             {"sender_id": sender_id, "receiver_id": receiver_id},
#             {"$pull": {"messages": {"message": message}}}
#         )
#         return result.modified_count > 0

#     def delete_record(self, sender_id: str, receiver_id: str) -> bool:
#         result = self.collection.delete_one({"sender_id": sender_id, "receiver_id": receiver_id})
#         return result.deleted_count > 0










import json
from typing import List, Dict, Any
from datetime import datetime

from pymongo import MongoClient
# from UltraXpertChatApp.ultrachatapp.config import Config
from ultrachatapp.config import Config



client = MongoClient(Config.MONGO_URI)
db = client.get_database()  # Use default DB from URI
users_collection = db["users"]


class DatabaseClient:
    def __init__(self, file_path: str = "data.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self) -> List[dict]:
            try:
                with open("data.json", "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # If any item is a stringified dict, parse it
                        parsed_data = []
                        for item in data:
                            if isinstance(item, str):
                                try:
                                    parsed_data.append(json.loads(item))
                                except json.JSONDecodeError:
                                    print("⚠️ Skipping corrupted string item:", item)
                            elif isinstance(item, dict):
                                parsed_data.append(item)
                        return parsed_data
                    return []
            except Exception as e:
               print(f"⚠️ Failed to load data: {e}")
               return []

    def _save_data(self) -> None:
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.data

    def add_message(self, sender_id: str, receiver_id: str, message: str, status: str = "sent") -> None:
        timestamp = datetime.utcnow().isoformat() + "Z"

        for record in self.data:
            if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
                record['messages'].append({
                    "message": message,
                    "timestamp": timestamp,
                    "status": status
                })
                self._save_data()
                return

        new_record = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "messages": [
                {
                    "message": message,
                    "timestamp": timestamp,
                    "status": status
                }
            ],
            "encryption": "AES256"
        }
        self.data.append(new_record)
        self._save_data()

    def update_message(self, sender_id: str, receiver_id: str, old_message: str, new_message: str) -> bool:
        for record in self.data:
            if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
                for msg in record['messages']:
                    if msg['message'] == old_message:
                        msg['message'] = new_message
                        msg['timestamp'] = datetime.utcnow().isoformat() + "Z"
                        self._save_data()
                        return True
        return False

    def delete_message(self, sender_id: str, receiver_id: str, message: str) -> bool:
        for record in self.data:
            if record['sender_id'] == sender_id and record['receiver_id'] == receiver_id:
                record['messages'] = [msg for msg in record['messages'] if msg['message'] != message]
                self._save_data()
                return True
        return False

    def delete_record(self, sender_id: str, receiver_id: str) -> bool:
        self.data = [record for record in self.data if not (record['sender_id'] == sender_id and record['receiver_id'] == receiver_id)]
        self._save_data()
        return True

