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
