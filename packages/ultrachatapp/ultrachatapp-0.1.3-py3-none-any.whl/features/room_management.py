# Group chats 
class RoomManagement:
    def __init__(self):
        self.rooms = {}

    def create_room(self, room_name):
        if room_name in self.rooms:
            raise ValueError("Room already exists.")
        self.rooms[room_name] = []

    def delete_room(self, room_name):
        if room_name not in self.rooms:
            raise ValueError("Room does not exist.")
        del self.rooms[room_name]

    def add_user_to_room(self, room_name, user):
        if room_name not in self.rooms:
            raise ValueError("Room does not exist.")
        if user in self.rooms[room_name]:
            raise ValueError("User already in the room.")
        self.rooms[room_name].append(user)

    def remove_user_from_room(self, room_name, user):
        if room_name not in self.rooms:
            raise ValueError("Room does not exist.")
        if user not in self.rooms[room_name]:
            raise ValueError("User not in the room.")
        self.rooms[room_name].remove(user)

    def list_rooms(self):
        return list(self.rooms.keys())

    def list_users_in_room(self, room_name):
        if room_name not in self.rooms:
            raise ValueError("Room does not exist.")
        return self.rooms[room_name]