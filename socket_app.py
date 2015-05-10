import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from praw import Reddit
from praw.helpers import comment_stream
from praw.errors import RedirectException

from config import praw_config


class RedditStreamNamespace(BaseNamespace, BroadcastMixin):
    reddit_api = None
    comment_stream = None
    subreddit = 'all'

    def __init__(self, environ, ns_name, request=None):
        super(RedditStreamNamespace, self).__init__(environ, ns_name, request)
        self.reddit_api = Reddit('A mass-data comment stream parser. Or something.')
        self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=50)

    def initialize(self):
        logging.debug('Connection initialized')

    def disconnect(self, *args, **kwargs):
        logging.debug('Connection closed')
        super(RedditStreamNamespace, self).disconnect(*args, **kwargs)

    def on_get_next(self, message):
        print 'got get_next'
        self._get_next()

    def _get_next(self):
        comment = self.comment_stream.next()
        self.broadcast_event('message', dict(comment=comment.body,
                                             author_name=comment.author.name,
                                             subreddit=comment.subreddit.display_name,
                                             permalink=comment.permalink))

    def _send_exception_alert(self, message):
        print 'sending exception message'
        self.broadcast_event('exception', message)

    def on_change_subreddit(self, new_subreddit):
        print 'got change_subreddit to %s' % new_subreddit
        old_subreddit = self.subreddit
        try:
            self.subreddit = new_subreddit
            self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=50)

        except RedirectException as e:
            self.subreddit = old_subreddit
            self.comment_stream = comment_stream(self.reddit_api, subreddit=self.subreddit, limit=50)
            self._send_exception_alert('Cannot get that subreddit.')

        finally:
            self._get_next()


