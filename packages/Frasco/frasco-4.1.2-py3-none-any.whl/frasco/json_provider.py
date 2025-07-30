from flask.json.provider import DefaultJSONProvider
import speaklater
import datetime


class JSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(o):
        if isinstance(o, speaklater._LazyString):
            return o.value
        if isinstance(o, (set, map)):
            return list(o)
        if isinstance(o, datetime.time):
            return str(o)
        return DefaultJSONProvider.default(o)
