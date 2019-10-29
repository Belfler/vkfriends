import json
import urllib
from uuid import uuid4

from utils import parse_session_id_from_cookie

import requests


def index_handler(environ: dict, url_args: dict) -> tuple:
    db = environ['db']

    if 'HTTP_COOKIE' in environ:
        session_id = parse_session_id_from_cookie(environ['HTTP_COOKIE'])
    else:
        session_id = None

    if session_id and db.get(f'{session_id}:user_id'):
        user_id = db.get(f'{session_id}:user_id')
        access_token = db.get(f'{session_id}:access_token')
        print(access_token)
        url = f'https://api.vk.com/method/friends.get?user_id={user_id}&access_token={access_token}&count=5&v=5.102'
        request = requests.get(url)
        data = request.json()
        content = json.dumps(data)
    else:
        content = f'<a href="https://oauth.vk.com/authorize?client_id=7188294&redirect_uri=https://{environ["HTTP_HOST"]}/login/&display=popup&scope=friends&v=5.102">Войти</a>'

    return 200, {}, content


def login_handler(environ: dict, url_args: dict) -> tuple:
    """
    Add 'sessionid' to cookie, create two raws in database with user_id and access_token and redirect to index page.
    """
    db = environ['db']

    headers = {'Location': f'http://{environ["HTTP_HOST"]}/'}

    code = urllib.parse.parse_qs(environ['QUERY_STRING']).get('code')
    if code:
        code = code[0]
        url = f'https://oauth.vk.com/access_token?client_id=7188294&client_secret=mCbI0mURTZ9au8rOuFIE&redirect_uri=https://{environ["HTTP_HOST"]}/login/&code={code}'
        request = requests.get(url)
        data = request.json()

        session_id = str(uuid4())
        for field in ('user_id', 'access_token'):
            db.set(f'{session_id}:{field}', data[field])
            db.expire(f'{session_id}:{field}', data['expires_in'])
        headers['Set-Cookie'] = f'sessionid={session_id}; path=/; max-age={data["expires_in"]}'

    return 303, headers, ''


def logout_handler(environ: dict, url_args: dict) -> tuple:
    """
    Delete session id from database and redirect to index page.
    """
    db = environ['db']

    headers = {'Location': f'http://{environ["HTTP_HOST"]}/'}

    if 'HTTP_COOKIE' in environ:
        session_id = parse_session_id_from_cookie(environ['HTTP_COOKIE'])
    else:
        session_id = None

    if session_id:
        db.delete(session_id)

    return 303, headers, ''
