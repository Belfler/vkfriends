import os
from typing import Callable, Iterable
import re
import http.client

from .handlers import index_handler, login_handler

import redis


class App:
    def __init__(self, handlers: dict):
        self.handlers = handlers
        self.db = redis.StrictRedis.from_url(os.getenv('REDIS_URL'), decode_responses=True)

    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        environ['db'] = self.db
        url = environ['PATH_INFO']

        handler, url_args = self.get_handler(url)

        status_code, extra_headers, response_content = handler(environ, url_args)

        headers = {
            'Content-Type': 'text/html; charset=utf-8'
        }
        headers.update(extra_headers)

        start_response(
            f'{status_code} {http.client.responses[status_code]}',
            list(headers.items())
        )
        return [response_content.encode('utf-8')]

    def get_handler(self, url):
        handler = None
        url_args = None

        for url_regexp, current_handler in self.handlers.items():
            match = re.match(url_regexp, url)
            if match is None:
                continue
            url_args = match.groupdict()
            handler = current_handler
            break

        if handler is None:
            handler = App.not_found_handler

        return handler, url_args

    @staticmethod
    def not_found_handler(environ: dict, url_args: dict) -> tuple:
        return 404, {}, 'Not found'


handlers = {
    r'^/$': index_handler,
    r'^/login/$': login_handler,
}

app = App(handlers)
