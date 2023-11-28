"""
About the code:

1. The `Bot` class is a simple implementation of a bot for interacting with a web server via HTTP requests.

2. Method `sign_up(username, password)`: Sends a POST request to register a new user on the server.
     - Options:
         - `username`: Username.
         - `password`: User password.
     - Returns the API key if registration is successful.
     - Handles cases where the username is already taken or other errors occur.

3. Method `create_post(api_key, content)`: Sends a POST request to create a new post on the server.
     - Options:
         - `api_key`: user API key.
         - `content`: Post content.
     - Returns the ID of the created post if the operation was successful.
     - Handles errors that occur when creating a post.

4. Method `like_post(post_id, api_key)`: Sends a POST request to like the specified post.
     - Options:
         - `post_id`: Post ID.
         - `api_key`: user API key.
     - Returns `True` if the operation was successful, and `False` otherwise.
     - Handles errors that occur when liking.

The general functionality of the class is designed to automate routine user actions on the server, such as registration, creating posts and liking.
"""

import requests

class Bot:
    def __init__(self, api_url):
        self.api_url = api_url

    def sign_up(self, username, password):
        if username and password:
            url = f'{self.api_url}/register'
            data = {'username': username, 'password': password}
            response = requests.post(url, json=data)
            
            if response.status_code == 201:
                print(f"Success sign up user - {response}")
                api_key = response.json().get('api_key')
                return api_key
            elif response.status_code == 400 and response.json().get('message') == 'Username is already taken':
                raise ValueError('Username is already taken')
            else:
                raise ValueError(f'Failed to sign up - {response}')


    def create_post(self, api_key: str, content: str):
        url = f'{self.api_url}/post/create'
        
        data = {
            'api_key': api_key,
            'content': content
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print(f"Success to create post - {response}")
            return response.json().get('post_id')
        else:
            raise ValueError(f'Failed to create post - {response}')

    def like_post(self, post_id: int, api_key: str):
        url = f'{self.api_url}/post/{post_id}/like'
        
        data = {
            'api_key': api_key,
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url=url, json=data, headers=headers)
        if response.status_code == 202 or response.status_code == 200:
            print(f"Success to like post - {response}")
            return
        else:
            raise ValueError(f'Failed to like post - {response}')

        
