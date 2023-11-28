"""
Automating bot actions and generating random passwords and a:

1. Generate random passwords:
    - `generate_random_password(length=12)`: The function generates a random password of a given length, consisting of letters, numbers and symbols.

2. Main bot script:
    - `main()`: Creates a bot instance with the given parameters and passes through the user data from the configuration.
      - For each user:
        - A random password is generated.
        - User registration is performed using a random password.
        - If registration is successful, a random number of posts (not more than the specified maximum) is created for the user.
        - Each post is assigned a random number of likes (no more than a specified maximum).
"""

import secrets
import string
from bot import Bot
from random import randint


from config import (
    URL,
    NUMBER_OF_USERS,
    MAX_POSTS_PER_USER,
    MAX_LIKES_PER_USER,
    USERS_DATA
)

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
    
def main():
    AutomationBot = Bot(URL)
    
    for user_data in USERS_DATA:
        random_password = generate_random_password()
        api_key = AutomationBot.sign_up(user_data['username'], random_password)
        if api_key:
            for post in range(randint(1, MAX_POSTS_PER_USER)):
                post_id = AutomationBot.create_post(api_key=api_key, content=user_data['content'])
                if post_id:
                    for _ in range(randint(1, MAX_LIKES_PER_USER)):
                        AutomationBot.like_post(post_id, api_key)


if __name__ == '__main__':
    main()