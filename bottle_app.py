import bottle
from config import socket_config

bottle.debug(True)
things_app = bottle.Bottle()


@things_app.route('/')
def show_home():
    return bottle.template('templates/things.tpl', dict(host=socket_config['host']))


@things_app.route('/static/<filename>')
def server_static(filename):
    print 'routing'
    return bottle.static_file(filename, root='./static')