from flask import g, has_request_context, request, current_app
from frasco.ext import *
from frasco.users import is_user_logged_in, current_user
from frasco.models import delayed_tx_calls
from frasco.ctx import ContextStack, DelayedCallsContext
from frasco.utils import expose_package
from itsdangerous import URLSafeTimedSerializer
import hashlib
import logging
import uuid
import click
import socketio


suppress_push_events = ContextStack(False, default_item=True, ignore_nested=True)
delayed_push_events = DelayedCallsContext()
testing_push_events = ContextStack(None, list, ignore_nested=True)
dont_skip_self_push_events = ContextStack(False, default_item=True, ignore_nested=True)
logger = logging.getLogger('frasco.push')


class FrascoPushState(ExtensionState):
    def __init__(self, *args, **kwargs):
        super(FrascoPushState, self).__init__(*args, **kwargs)
        self.current_user_loader = default_current_user_loader


class FrascoPush(Extension):
    name = 'frasco_push'
    state_class = FrascoPushState
    defaults = {"redis_url": None,
                "server_url": None,
                "server_port": 8888,
                "server_secured": False,
                "channel": "socketio",
                "secret": None,
                "prefix_event_with_room": True,
                "default_current_user_loader": True,
                "testing_ignore_redis_publish": True}

    def _init_app(self, app, state):
        expose_package(app, "frasco_push", __name__)

        if state.options['secret'] is None:
            state.options["secret"] = app.config['SECRET_KEY']

        if not state.options['redis_url'] and has_extension('frasco_redis', app):
            state.options['redis_url'] = app.extensions.frasco_redis.options['url']

        state.server_cli = ["python", "-m", "frasco.push.server",
            "--channel", state.options["channel"],
            "--redis", state.options["redis_url"],
            "--port", str(state.options["server_port"])]
        if state.options['secret']:
            state.server_cli.extend(["--secret", state.options["secret"]])
        if app.debug or app.testing:
            state.server_cli.append("--debug")

        if state.options["server_url"]:
            state.server_url = state.options['server_url']
        else:
            server_name = app.config.get('SERVER_NAME') or 'localhost'
            state.server_url = "%s://%s:%s" % (
                "https" if state.options['server_secured'] else "http",
                server_name.split(':')[0], state.options['server_port'])

        state.token_serializer = URLSafeTimedSerializer(state.options['secret'])
        state.redis_manager = socketio.RedisManager(state.options['redis_url'], write_only=True)
        state.host_id = uuid.uuid4().hex

        @app.cli.command('push-server')
        @click.option('--port', type=int)
        @click.option('--access-logs', is_flag=True)
        @click.option('--debug', is_flag=True)
        def cli_server(port=None, access_logs=False, debug=False):
            """Start the push server"""
            from .server import run_server
            run_server(port or state.options["server_port"], debug=debug or app.debug or app.testing, access_logs=access_logs,
                redis_url=state.options["redis_url"], channel=state.options["channel"], secret=state.options["secret"])

        @app.cli.command('push-server-cli')
        def cli_print_cmd():
            """Print the command line to start the push server independently from the app"""
            click.echo(" ".join(state.server_cli))

        @app.before_request
        def before_request():
            if state.options['secret']:
                user_id, user_info, allowed_rooms = state.current_user_loader()
                g.socketio_token = create_push_token(user_info, get_user_room_name(user_id), allowed_rooms)

    @ext_stateful_method
    def current_user_loader(self, state, func):
        state.current_user_loader = func
        return func


def default_current_user_loader():
    if not is_user_logged_in():
        return None, {"guest": True}, None

    allowed_rooms = None
    if hasattr(current_user, 'get_allowed_push_rooms'):
        allowed_rooms = current_user.get_allowed_push_rooms()

    info = {"guest": False}
    info['username'] = getattr(current_user, 'username', current_user.email)
    if has_extension('frasco_users_avatar'):
        info['avatar_url'] = current_user.avatar_url

    return current_user.get_id(), info, allowed_rooms


def create_push_token(user_info=None, user_room=None, allowed_rooms=None):
    return get_extension_state('frasco_push').token_serializer.dumps([user_info, user_room, allowed_rooms])


@delayed_push_events.proxy
@delayed_tx_calls.proxy
def _emit_push_event(event, data=None, skip_self=None, room=None, namespace=None, prefix_event_with_room=True):
    state = get_extension_state('frasco_push')
    if current_app.testing and testing_push_events.top is not None:
        testing_push_events.top.append((event, data, skip_self, room, namespace))
        if state.options['testing_ignore_redis_publish']:
            return
    if state.options['prefix_event_with_room'] and prefix_event_with_room and room:
        event = "%s:%s" % (room, event)
    if skip_self is None:
        skip_self = not dont_skip_self_push_events.top
    skip_sid = None
    if skip_self and has_request_context() and 'x-socketio-sid' in request.headers:
        skip_sid = request.headers['x-socketio-sid']
    logger.debug("Push event '%s' to {namespace=%s, room=%s, skip_sid=%s}: %s" % (event, namespace, room, skip_sid, data))
    return state.redis_manager.emit(event, data=data, room=room, skip_sid=skip_sid, namespace=namespace)


def emit_push_event(event, data=None, skip_self=None, room=None, namespace=None, prefix_event_with_room=True):
    if suppress_push_events.top:
        return
    return _emit_push_event(event, data=data, skip_self=skip_self, room=room, namespace=namespace, prefix_event_with_room=prefix_event_with_room)


def emit_user_push_event(user_id, event, data=None, **kwargs):
    return emit_push_event(event, data, room=get_user_room_name(user_id), prefix_event_with_room=False, **kwargs)


def get_user_room_name(user_id):
    state = get_extension_state('frasco_push')
    if not state.options['secret']:
        raise Exception('A secret must be set to use emit_direct()')
    return hashlib.sha1((str(user_id) + state.options['secret']).encode('utf-8')).hexdigest()
