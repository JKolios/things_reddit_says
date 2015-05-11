import logging
from uuid import uuid4

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from praw import Reddit
from praw.helpers import comment_stream
from praw.errors import RedirectException

from config import praw_config


class RedditStream(object):
    reddit_api = None
    comment_stream = None

    def __init__(self, subreddit='all'):
        self.subreddit = subreddit
        self.reddit_api = Reddit('A mass-data comment stream parser. Or something.')
        self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=100)

    def get_next(self, *args, **kwargs):
        next_comment = self.comment_stream.next()
        print 'Served get_next'
        args[0]('message', dict(comment=next_comment.body,
                                author_name=next_comment.author.name,
                                subreddit=next_comment.subreddit.display_name,
                                permalink=next_comment.permalink))

    def change_subreddit(self, new_subreddit):
        old_subreddit = self.subreddit
        try:
            self.subreddit = new_subreddit
            self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=100)

        except RedirectException as e:
            self.subreddit = old_subreddit
            self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=100)


class RedditStreamNamespace(BaseNamespace, BroadcastMixin):
    stream_dict = {}

    def initialize(self):
        frontend_id = self.generate_id()
        logging.debug('Connection initialized: %s' % frontend_id)
        new_reddit_stream = RedditStream()
        self.stream_dict[frontend_id] = new_reddit_stream
        self.emit('init_response', frontend_id)

    def disconnect(self, *args, **kwargs):
        logging.debug('Connection closed.')
        super(RedditStreamNamespace, self).disconnect(*args, **kwargs)

    @staticmethod
    def generate_id():
        return str(uuid4())[:8]

    def on_get_next(self, frontend_id):
        print 'got get_next from %s' % frontend_id
        self.spawn(self.stream_dict[frontend_id].get_next, self.emit)

    def on_change_subreddit(self, data):
        print 'got change_subreddit from %s to %s' % (data['frontend_id'], data['new_subreddit'])
        self.stream_dict[data['frontend_id']].change_subreddit(data['new_subreddit'])
        self.spawn(self.stream_dict[data['frontend_id']].get_next, self.emit)


