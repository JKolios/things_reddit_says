import logging

from gevent import sleep
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from praw import Reddit
from praw.helpers import comment_stream

from config import praw_config


class RedditStreamNamespace(BaseNamespace, BroadcastMixin):
    # a websocket 'app'
    reddit_api = None
    comment_stream = None

    def __init__(self, environ, ns_name, request=None):
        super(RedditStreamNamespace, self).__init__(environ, ns_name, request)
        self.reddit_api = Reddit('A mass-data comment stream parser. Or something.')
        self.comment_stream = comment_stream(self.reddit_api, 'all', limit=3)

    def initialize(self):
        logging.debug('Connection initialized')
        while True:
            self.broadcast_event('message', 'Hi there!')
            self.spam_reddit_comments()

    def disconnect(self, *args, **kwargs):
        logging.debug('Connection closed')
        super(RedditStreamNamespace, self).disconnect(*args, **kwargs)

    def spam_reddit_comments(self):
        for comment in self.comment_stream:
            self.broadcast_event('reddit_comment', comment.body)
            sleep(5)