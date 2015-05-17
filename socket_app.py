import logging
from uuid import uuid4

from gevent import sleep
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from praw import Reddit
from praw.errors import RedirectException
from requests import HTTPError


class RedditStream(object):
    reddit_api = Reddit('A mass-data comment stream parser. Or something.')

    def __init__(self, emitter, subreddit='all'):
        self.emitter = emitter

        self.subreddit_name = subreddit
        self.subreddit_object = self.reddit_api.get_subreddit(self.subreddit_name)
        self.comment_stream = self.subreddit_object.get_comments()
        # "Rev up" the generator by getting the first item
        # self.comment_stream.next()

    def get_next(self, *args, **kwargs):
        try:
            next_comment = self.comment_stream.next()
        except StopIteration:
            self.comment_stream = self.subreddit_object.get_comments()
            self.get_next()
            return

        print 'Served get_next'
        self.emitter('message', dict(comment=next_comment.body,
                                     author_name=next_comment.author.name,
                                     subreddit=next_comment.subreddit.display_name,
                                     permalink=next_comment.permalink))

    def change_subreddit(self, new_subreddit):
        self.subreddit_object = self.reddit_api.get_subreddit(new_subreddit)
        self.comment_stream = self.subreddit_object.get_comments()
        try:
            self.get_next()
        except (RedirectException, HTTPError, AttributeError, KeyError):
            self.subreddit_object = self.reddit_api.get_subreddit(self.subreddit_name)
            return False
        else:
            self.subreddit_name = new_subreddit
            return True


class RedditStreamNamespace(BaseNamespace, BroadcastMixin):
    streams = {}

    def __init__(self, environ, ns_name, request=None):
        super(RedditStreamNamespace, self).__init__(environ, ns_name, request)
        logging.debug('Namespace initialized')

    def initialize(self):
        frontend_id = self.generate_id()
        logging.debug('Connection initialized: %s' % frontend_id)

        self.streams[frontend_id] = RedditStream(self.emit)
        self.emit('init_response', frontend_id)

    def disconnect(self, *args, **kwargs):
        logging.debug('Connection closed.')
        super(RedditStreamNamespace, self).disconnect(*args, **kwargs)

    def on_get_next(self, frontend_id):
        print 'got get_next from %s' % frontend_id
        self.spawn(self.streams[frontend_id].get_next)

    def on_change_subreddit(self, data):
        print 'got change_subreddit from %s to %s' % (data['frontend_id'], data['new_subreddit'])

        if self.streams[data['frontend_id']].change_subreddit(data['new_subreddit']):
            self.emit('notification', 'OK, changed to r/%s.' % data['new_subreddit'])
            self.spawn(self.streams[data['frontend_id']].get_next)
            return
        else:
            print 'notifying %s' % data['frontend_id']
            self.emit('notification', 'This Subreddit does not exist or is not publicly accessible.')
            self.spawn(self.streams[data['frontend_id']].get_next)

    @staticmethod
    def generate_id():
        return str(uuid4())[:8]
