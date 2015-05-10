import bottle
from config import bottle_config, praw_config, socket_config
from praw import Reddit
from praw.helpers import comment_stream
import logging

import gevent
from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

LOG_FILENAME = 'things.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


class RedditStreamNamespace(BaseNamespace, BroadcastMixin):
    # a websocket 'app'
    reddit_api = None
    comment_stream = None

    def initialize(self):
        logging.debug('Connection initialized')
        self.reddit_api = Reddit('A mass-data comment stream parser. Or something.')
        while True:
            self.broadcast_event('message', 'Getting stuff from Reddit, please wait...')
            self.comment_stream = comment_stream(self.reddit_api, 'all')
            self.spam_reddit_comments()

    def disconnect(self, *args, **kwargs):
        logging.debug('Connection closed')
        super(RedditStreamNamespace, self).disconnect(*args, **kwargs)

    def spam_reddit_comments(self):
        for comment in self.comment_stream:
            self.broadcast_event('reddit_comment', str(comment.body))
            gevent.sleep(5)


def reddit_stream(environ, start_response):
    # route the websocket paths to the correct namespace
    if environ['PATH_INFO'].startswith('/socket.io'):
        return socketio_manage(environ, {'/reddit_stream': RedditStreamNamespace})


bottle.debug(True)
things_app = bottle.Bottle()


@things_app.route('/')
def show_home():
    return bottle.template('templates/things.tpl')


def main():

    # setup server to handle webserver requests
    http_server = WSGIServer(bottle_config['host'], things_app)

    # setup server to handle websocket requests
    sio_server = SocketIOServer(
        socket_config['host'], reddit_stream,
        policy_server=False
    )

    gevent.joinall([
        gevent.spawn(http_server.serve_forever),
        gevent.spawn(sio_server.serve_forever)
    ])

if __name__ == "__main__":
    main()