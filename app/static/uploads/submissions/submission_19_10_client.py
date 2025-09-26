import requests
import json

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_users(self):
        response = requests.get(self.base_url + '/users')
        return response.json()

    def get_user(self, user_id):
        response = requests.get(self.base_url + f'/users/{user_id}')
        return response.json()

    def create_user(self, name, age):
        data = {'name': name, 'age': age}
        response = requests.post(self.base_url + '/users', json=data)
        return response.json()

    def update_user(self, user_id, name=None, age=None):
        data = {}
        if name:
            data['name'] = name
        if age:
            data['age'] = age
        response = requests.put(self.base_url + f'/users/{user_id}', json=data)
        return response.json()

client = APIClient("http://127.0.0.1:5000")
client.create_user("Racheal", 40)
client.update_user(3, "Rachael")
resp = client.get_users()

print(resp)