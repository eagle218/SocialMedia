import yaml

CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

URL = CMD_LIST['Commands']['url']
NUMBER_OF_USERS = CMD_LIST['Commands']['number_of_users']
MAX_POSTS_PER_USER = CMD_LIST['Commands']['max_posts_per_user']
MAX_LIKES_PER_USER = CMD_LIST['Commands']['max_likes_per_user']

USERS_DATA = []
for user_info in CMD_LIST['Commands']['users']:
    username = user_info['username']
    content = user_info['content']
    USERS_DATA.append({'username': username, 'content': content})

