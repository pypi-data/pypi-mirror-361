import socketio
import engineio
from socketio.exceptions import ConnectionRefusedError
import os
import json
from itsdangerous import URLSafeTimedSerializer, BadSignature
import logging


logger = logging.getLogger('frasco.push.server')


class Manager(socketio.AsyncRedisManager):
    def __init__(self, *args, **kwargs):
        self.presence_by_sids = {}
        self.presence_info = {}
        super().__init__(*args, **kwargs)
        
    async def _emit_joined(self, room, sid, info):
        await self.emit('%s:joined' % room, {"sid": sid, "info": info}, room=room, skip_sid=sid)

    async def enter_room(self, sid, namespace, room, eio_sid=None, skip_presence=False):
        await super().enter_room(sid, namespace, room, eio_sid)
        if room and room != sid and not skip_presence:
            self.presence_by_sids.setdefault(f"{namespace}/{sid}", set()).add(room)
            await self._emit_joined(room, sid, self.get_member_info(sid, namespace))

    async def leave_room(self, sid, namespace, room):
        await super().leave_room(sid, namespace, room)
        if room and room != sid:
            self.presence_by_sids[f"{namespace}/{sid}"].discard(room)
            await self.emit('%s:left' % room, sid, room=room, skip_sid=sid)

    async def disconnect(self, sid, namespace, **kwargs):
        if f"{namespace}/{sid}" in self.presence_by_sids:
            for room in self.presence_by_sids[f"{namespace}/{sid}"]:
                await self.emit('%s:left' % room, sid, room=room, skip_sid=sid)
            del self.presence_by_sids[f"{namespace}/{sid}"]
        if f"{namespace}/{sid}" in self.presence_info:
            del self.presence_info[f"{namespace}/{sid}"]
        await super().disconnect(sid, namespace, **kwargs)

    async def set_member_info(self, sid, namespace, info):
        self.presence_info[f"{namespace}/{sid}"] = info
        for room in self.get_rooms(sid, namespace):
            if room != sid:
                await self._emit_joined(room, sid, info)

    def get_member_info(self, sid, namespace):
        return self.presence_info.get(f"{namespace}/{sid}")


class EngineioServer(engineio.AsyncServer):
    def async_modes(self):
        return ['asgi']


class Server(socketio.AsyncServer):
    async def enter_room(self, sid, room, namespace=None, skip_presence=False):
        namespace = namespace or '/'
        self.logger.info('%s is entering room %s [%s]', sid, room, namespace)
        await self.manager.enter_room(sid, namespace, room, skip_presence=skip_presence)

    def _engineio_server_class(self):
        return EngineioServer


def create_app(redis_url='redis://', channel='socketio', secret=None, token_max_age=None, debug=False):
    mgr = Manager(redis_url, channel=channel)
    sio = Server(mgr, logger=debug, engineio_logger=debug, cors_allowed_origins='*') # client must be identified via url token so cors to * is not a big risk
    token_serializer = URLSafeTimedSerializer(secret or "")
    default_ns = '/'

    @sio.on('connect')
    async def connect(sid, environ, auth):
        if not secret:
            raise ConnectionRefusedError('no secret defined')

        if not auth or not auth.get('token'):
            raise ConnectionRefusedError('missing token')

        try:
            token_data = token_serializer.loads(auth['token'], max_age=token_max_age)
        except BadSignature:
            logger.debug('Client provided an invalid token')
            raise ConnectionRefusedError('invalid token')

        if len(token_data) == 3:
            user_info, user_room, allowed_rooms = token_data
        else:
            # old format
            user_info, allowed_rooms = token_data
            user_room = None

        async with sio.session(sid) as session:
            session['allowed_rooms'] = allowed_rooms
        if user_info:
            await mgr.set_member_info(sid, default_ns, user_info)
        if user_room:
            await sio.enter_room(sid, user_room, skip_presence=True)

        logger.debug('New client connection: %s ; %s' % (sid, user_info))
        return True

    @sio.on('members')
    def get_room_members(sid, data):
        if not data.get('room'):
            return []
        return {sid: mgr.get_member_info(sid, default_ns) for sid, _ in mgr.get_participants(default_ns, data['room'])}

    @sio.on('join')
    async def join(sid, data):
        async with sio.session(sid) as session:
            if session.get('allowed_rooms') is not None and data['room'] not in session['allowed_rooms']:
                logger.debug('Client %s is not allowed to join room %s' % (sid, data['room']))
                return False
        await sio.enter_room(sid, data['room'])
        logger.debug('Client %s has joined room %s' % (sid, data['room']))
        return get_room_members(sid, data)

    @sio.on('broadcast')
    async def room_broadcast(sid, data):
        logger.debug('Client %s broadcasting %s to room %s' % (sid, data['event'], data['room']))
        await sio.emit("%s:%s" % (data['room'], data['event']), data.get('data'), room=data['room'], skip_sid=sid)

    @sio.on('leave')
    async def leave(sid, data):
        await sio.leave_room(sid, data['room'])
        logger.debug('Client %s has left room %s' % (sid, data['room']))

    @sio.on('set')
    async def set_member_info(sid, data):
        await mgr.set_member_info(sid, default_ns, data)
        logger.debug('Client %s has updated its user info: %s' % (sid, data))

    @sio.on('get')
    def get_member_info(sid, data):
        return mgr.get_member_info(data['sid'], default_ns)

    return socketio.ASGIApp(sio)


def run_server(port=8888, access_logs=False, debug=False, **kwargs):
    logger.addHandler(logging.StreamHandler())
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Push server running in DEBUG')

    app = create_app(kwargs["redis_url"], kwargs["channel"], kwargs["secret"], debug=debug)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug" if debug else "info", access_log=access_logs)


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(prog='frascopush',
        description='Start frasco.push.server')
    argparser.add_argument('-p', '--port', default=8888, type=int,
        help='Port number')
    argparser.add_argument('-r', '--redis-url', default=os.environ.get('SIO_REDIS_URL', 'redis://'), type=str,
        help='Redis URL')
    argparser.add_argument('-c', '--channel', default=os.environ.get('SIO_CHANNEL', 'socketio'), type=str,
        help='Redis channel')
    argparser.add_argument('-s', '--secret', default=os.environ.get('SIO_SECRET'), type=str,
        help='Secret')
    argparser.add_argument('--debug', action='store_true', help='Debug mode')
    argparser.add_argument('--access-logs', action='store_true', help='Show access logs in console')
    args = argparser.parse_args()
    run_server(args.port, debug=args.debug, access_logs=args.access_logs,
        redis_url=args.redis_url, channel=args.channel, secret=args.secret)
