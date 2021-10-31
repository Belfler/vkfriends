from typing import Union


def parse_session_id_from_cookie(cookie: str) -> Union[str, None]:
    if 'sessionid' in cookie:
        start_index = cookie.find('sessionid') + 10
        end_index = cookie.find(';', start_index)
        if end_index == -1:
            session_id_slice = slice(start_index, None)
        else:
            session_id_slice = slice(start_index, end_index)
        session_id = cookie[session_id_slice]
        return session_id

    return None


def get_index_template(data: dict) -> str:
    user_id = data['user']['id']
    user_full_name = data['user']['first_name'] + ' ' + data['user']['last_name']
    content = f'<p><a href="https://vk.com/id{user_id}/">{user_full_name}</a></p><p>Мои друзья:</p>'
    for friend in data['friends']:
        friend_id = friend['id']
        friend_full_name = friend['first_name'] + ' ' + friend['last_name']
        content += f'<p><a href="https://vk.com/id{friend_id}/">{friend_full_name}</a></p>'
    return content
