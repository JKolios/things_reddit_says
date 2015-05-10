from config import bottle_config, socket_config

import logging

import gevent
from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from socketio import socketio_manage
from socketio.server import SocketIOServer

from socket_app import RedditStreamNamespace
from bottle_app import things_app

LOG_FILENAME = 'things.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


def socket_app_router(environ, start_response):
    # route the websocket paths to the correct namespace
    if environ['PATH_INFO'].startswith('/socket.io'):
        return socketio_manage(environ, {'/reddit_stream': RedditStreamNamespace})


def main():
    # setup server to handle webserver requests
    http_server = WSGIServer(bottle_config['host'], things_app)

    # setup server to handle websocket requests
    sio_server = SocketIOServer(
        socket_config['host'], socket_app_router,
        policy_server=False
    )

    gevent.joinall([
        gevent.spawn(http_server.serve_forever),
        gevent.spawn(sio_server.serve_forever)
    ])

if __name__ == "__main__":
    main()