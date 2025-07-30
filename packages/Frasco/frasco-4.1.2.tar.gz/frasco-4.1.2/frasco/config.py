
from flask import json
from flask.config import Config as FlaskConfig
from frasco.utils import deep_update_dict
import os
import yaml
import errno
import logging


logger = logging.getLogger('frasco')


class Config(FlaskConfig):
    """Subclass of Flask's Config class to add support to load from YAML file
    """
    def from_mapping(self, mapping, **kwargs):
        deep_update = kwargs.pop('_deep_update', False)
        mappings = []
        if hasattr(mapping[0], 'items'):
            mappings.append(list(mapping[0].items()))
        else:
            mappings.append(mapping[0])
        mappings.append(list(kwargs.items()))
        for mapping in mappings:
            if deep_update:
                deep_update_dict(self, dict((k.upper(), v) for (k, v) in mapping))
            else:
                for (key, value) in mapping:
                    self[key.upper()] = value
        return True

    def from_file(self, filename, load=None, silent=False, text=True, deep_update=False):
        if not load:
            if filename.endswith(".py"):
                return self.from_pyfile(filename, silent)
            if filename.endswith(".js") or filename.endswith(".json"):
                load = json.load
            if filename.endswith(".yml") or filename.endswith(".yaml"):
                load = yaml.safe_load

        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename, "r" if text else "rb") as f:
                obj = load(f)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False

            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise

        return self.from_mapping(obj, _deep_update=deep_update)

    def from_json(self, filename, **kwargs):
        return self.from_file(filename, json.load, **kwargs)

    def from_yaml(self, filename, **kwargs):
        return self.from_file(filename, yaml.safe_load, **kwargs)


def load_config(config, config_filename='config.yml', env=None, deep_update=False, logger=None):
    if logger is None:
        logger = logging.getLogger('frasco')
    if os.path.exists(config_filename):
        if logger:
            logger.info('Loading config from %s' % config_filename)
        config.from_file(config_filename, deep_update=deep_update)
    if not env:
        return
    filename, ext = os.path.splitext(config_filename)
    env_filename = filename + "-" + env + ext
    if os.path.exists(env_filename):
        if logger:
            logger.info('Loading config from %s' % env_filename)
        config.from_file(env_filename, deep_update=True)


def load_app_config(app, **kwargs):
    kwargs.setdefault('env', app.config['ENV'])
    load_config(app.config, **kwargs)


def update_config_with_env_vars(config, prefix, logger=None):
    if logger is None:
        logger = logging.getLogger('frasco')
    config = {}
    prefix = prefix.upper()
    for k, v in os.environ.items():
        if k.startswith(prefix + "_"):
            config[k[len(prefix)+1:]] = v
    if config:
        if logger:
            logger.info('Using config from environment variables')
        config.update(config)


def update_app_config_with_env_vars(app, prefix):
    update_config_with_env_vars(app.config, prefix)
