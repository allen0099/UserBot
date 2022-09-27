"""
Copy and modified from Django-environ

* https://github.com/joke2k/django-environ

License: MIT License

* https://github.com/joke2k/django-environ/blob/main/LICENSE.txt

Owner: joke2k

* https://github.com/joke2k
"""
import json
import logging
import os
import re
import sys
import warnings
from collections.abc import MutableMapping
from os import PathLike
from urllib.parse import urlparse

can_open: tuple = (str, PathLike)
logger: logging.Logger = logging.getLogger(__name__)


class FileAwareMapping(MutableMapping):
    def __init__(self, env=None, cache=True):
        self.env = env if env is not None else os.environ
        self.cache = cache
        self.files_cache = {}

    def __getitem__(self, key):
        if self.cache and key in self.files_cache:
            return self.files_cache[key]
        key_file = self.env.get(key + "_FILE")
        if key_file:
            with open(key_file) as f:
                value = f.read()
            if self.cache:
                self.files_cache[key] = value
            return value
        return self.env[key]

    def __iter__(self):
        for key in self.env:
            yield key
            if key.endswith("_FILE"):
                no_file_key = key[:-5]
                if no_file_key and no_file_key not in self.env:
                    yield no_file_key

    def __len__(self):
        return len(tuple(iter(self)))

    def __setitem__(self, key, value):
        self.env[key] = value
        if self.cache and key.endswith("_FILE"):
            no_file_key = key[:-5]
            if no_file_key and no_file_key in self.files_cache:
                del self.files_cache[no_file_key]

    def __delitem__(self, key):
        file_key = key + "_FILE"
        if file_key in self.env:
            del self[file_key]
            if key in self.env:
                del self.env[key]
            return
        if self.cache and key.endswith("_FILE"):
            no_file_key = key[:-5]
            if no_file_key and no_file_key in self.files_cache:
                del self.files_cache[no_file_key]
        del self.env[key]


class ImproperlyConfigured(Exception):
    pass


class NoValue:
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)


class Env:
    ENVIRON = os.environ
    NOTSET = NoValue()
    BOOLEAN_TRUE_STRINGS = ("true", "on", "ok", "y", "yes", "1")

    def __init__(self, **scheme):
        self.smart_cast = True
        self.escape_proxy = False
        self.prefix = ""
        self.scheme = scheme

    def __call__(self, var, cast=None, default=NOTSET, parse_default=False):
        return self.get_value(
            var, cast=cast, default=default, parse_default=parse_default
        )

    def __contains__(self, var):
        return var in self.ENVIRON

    # Shortcuts

    def str(self, var, default=NOTSET, multiline=False):
        value = self.get_value(var, cast=str, default=default)
        if multiline:
            return re.sub(r"(\\r)?\\n", r"\n", value)
        return value

    def unicode(self, var, default=NOTSET):
        """Helper for python2"""
        warnings.warn(
            "`%s.unicode` is deprecated, use `%s.str` instead"
            % (
                self.__class__.__name__,
                self.__class__.__name__,
            ),
            DeprecationWarning,
            stacklevel=2,
        )

        return self.get_value(var, cast=str, default=default)

    def bytes(self, var, default=NOTSET, encoding="utf8"):
        value = self.get_value(var, cast=str, default=default)
        if hasattr(value, "encode"):
            return value.encode(encoding)
        return value

    def bool(self, var, default=NOTSET):
        return self.get_value(var, cast=bool, default=default)

    def int(self, var, default=NOTSET):
        return self.get_value(var, cast=int, default=default)

    def float(self, var, default=NOTSET):
        return self.get_value(var, cast=float, default=default)

    def json(self, var, default=NOTSET):
        return self.get_value(var, cast=json.loads, default=default)

    def list(self, var, cast=None, default=NOTSET):
        return self.get_value(var, cast=list if not cast else [cast], default=default)

    def tuple(self, var, cast=None, default=NOTSET):
        return self.get_value(var, cast=tuple if not cast else (cast,), default=default)

    def dict(self, var, cast=dict, default=NOTSET):
        return self.get_value(var, cast=cast, default=default)

    def url(self, var, default=NOTSET):
        return self.get_value(var, cast=urlparse, default=default, parse_default=True)

    def path(self, var, default=NOTSET, **kwargs):
        return Path(self.get_value(var, default=default), **kwargs)

    def get_value(self, var, cast=None, default=NOTSET, parse_default=False):
        logger.debug(
            "get '{}' casted as '{}' with default '{}'".format(var, cast, default)
        )

        var_name = "{}{}".format(self.prefix, var)
        if var_name in self.scheme:
            var_info = self.scheme[var_name]

            try:
                has_default = len(var_info) == 2
            except TypeError:
                has_default = False

            if has_default:
                if not cast:
                    cast = var_info[0]

                if default is self.NOTSET:
                    try:
                        default = var_info[1]
                    except IndexError:
                        pass
            else:
                if not cast:
                    cast = var_info

        try:
            value = self.ENVIRON[var_name]
        except KeyError as exc:
            if default is self.NOTSET:
                error_msg = "Set the {} environment variable".format(var)
                raise ImproperlyConfigured(error_msg) from exc

            value = default

        # Resolve any proxied values
        prefix = b"$" if isinstance(value, bytes) else "$"
        escape = rb"\$" if isinstance(value, bytes) else r"\$"
        if hasattr(value, "startswith") and value.startswith(prefix):
            value = value.lstrip(prefix)
            value = self.get_value(value, cast=cast, default=default)

        if self.escape_proxy and hasattr(value, "replace"):
            value = value.replace(escape, prefix)

        # Smart casting
        if self.smart_cast:
            if (
                cast is None
                and default is not None
                and not isinstance(default, NoValue)
            ):
                cast = type(default)

        value = None if default is None and value == "" else value

        if value != default or (parse_default and value):
            value = self.parse_value(value, cast)

        return value

    # Class and static methods

    @classmethod
    def parse_value(cls, value, cast):
        if cast is None:
            return value
        elif cast is bool:
            try:
                value = int(value) != 0
            except ValueError:
                value = value.lower() in cls.BOOLEAN_TRUE_STRINGS
        elif isinstance(cast, list):
            value = list(map(cast[0], [x for x in value.split(",") if x]))
        elif isinstance(cast, tuple):
            val = value.strip("(").strip(")").split(",")
            value = tuple(map(cast[0], [x for x in val if x]))
        elif isinstance(cast, dict):
            key_cast = cast.get("key", str)
            value_cast = cast.get("value", str)
            value_cast_by_key = cast.get("cast", dict())
            value = dict(
                map(
                    lambda kv: (
                        key_cast(kv[0]),
                        cls.parse_value(
                            kv[1], value_cast_by_key.get(kv[0], value_cast)
                        ),
                    ),
                    [val.split("=") for val in value.split(";") if val],
                )
            )
        elif cast is dict:
            value = dict([val.split("=") for val in value.split(",") if val])
        elif cast is list:
            value = [x for x in value.split(",") if x]
        elif cast is tuple:
            val = value.strip("(").strip(")").split(",")
            value = tuple([x for x in val if x])
        elif cast is float:
            # clean string
            float_str = re.sub(r"[^\d,.-]", "", value)
            # split for avoid thousands separator and different
            # locale comma/dot symbol
            parts = re.split(r"[,.]", float_str)
            if len(parts) == 1:
                float_str = parts[0]
            else:
                float_str = "{}.{}".format("".join(parts[0:-1]), parts[-1])
            value = float(float_str)
        else:
            value = cast(value)
        return value

    @classmethod
    def read_env(cls, env_file=None, overwrite=False, **overrides):
        if env_file is None:
            # noinspection PyUnresolvedReferences, PyProtectedMember
            frame = sys._getframe()
            env_file = os.path.join(
                os.path.dirname(frame.f_back.f_code.co_filename), ".env"
            )
            if not os.path.exists(env_file):
                logger.info(
                    "%s doesn't exist - if you're not configuring your "
                    "environment separately, create one." % env_file
                )
                return

        try:
            if isinstance(env_file, can_open):
                # Python 3.5 support (wrap path with str).
                with open(str(env_file)) as f:
                    content = f.read()
            else:
                with env_file as f:
                    content = f.read()
        except OSError:
            logger.info(
                "%s not found - if you're not configuring your "
                "environment separately, check this." % env_file
            )
            return

        logger.debug("Read environment variables from: {}".format(env_file))

        def _keep_escaped_format_characters(match):
            """Keep escaped newline/tabs in quoted strings"""
            escaped_char = match.group(1)
            if escaped_char in "rnt":
                return "\\" + escaped_char
            return escaped_char

        for line in content.splitlines():
            m1 = re.match(r"\A(?:export )?(\w+)=(.*)\Z", line)
            if m1:
                key, val = m1.group(1), m1.group(2)
                m2 = re.match(r"\A'(.*)'\Z", val)
                if m2:
                    val = m2.group(1)
                m3 = re.match(r'\A"(.*)"\Z', val)
                if m3:
                    val = re.sub(r"\\(.)", _keep_escaped_format_characters, m3.group(1))
                overrides[key] = str(val)
            elif not line or line.startswith("#"):
                # ignore warnings for empty line-breaks or comments
                pass
            else:
                logger.warning("Invalid line: %s", line)

        def set_environ(env_val):
            if overwrite:
                return lambda k, v: env_val.update({k: str(v)})
            return lambda k, v: env_val.setdefault(k, str(v))

        setenv = set_environ(cls.ENVIRON)

        for key, value in overrides.items():
            setenv(key, value)


class FileAwareEnv(Env):
    ENVIRON = FileAwareMapping()


class Path:
    def path(self, *paths, **kwargs):
        return self.__class__(self.__root__, *paths, **kwargs)

    def file(self, name, *args, **kwargs):
        return open(self(name), *args, **kwargs)

    @property
    def root(self):
        return self.__root__

    def __init__(self, start="", *paths, **kwargs):

        super().__init__()

        if kwargs.get("is_file", False):
            start = os.path.dirname(start)

        self.__root__ = self._absolute_join(start, *paths, **kwargs)

    def __call__(self, *paths, **kwargs):
        return self._absolute_join(self.__root__, *paths, **kwargs)

    def __eq__(self, other):
        if isinstance(other, Path):
            return self.__root__ == other.__root__
        return self.__root__ == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if not isinstance(other, Path):
            return Path(self.__root__, other)
        return Path(self.__root__, other.__root__)

    def __sub__(self, other):
        if isinstance(other, int):
            return self.path("../" * other)
        elif isinstance(other, str):
            if self.__root__.endswith(other):
                return Path(self.__root__.rstrip(other))
        raise TypeError(
            "unsupported operand type(s) for -: '{self}' and '{other}' "
            "unless value of {self} ends with value of {other}".format(
                self=type(self), other=type(other)
            )
        )

    def __invert__(self):
        return self.path("..")

    def __contains__(self, item):
        base_path = self.__root__
        if len(base_path) > 1:
            base_path = os.path.join(base_path, "")
        return item.__root__.startswith(base_path)

    def __repr__(self):
        return "<Path:{}>".format(self.__root__)

    def __str__(self):
        return self.__root__

    def __unicode__(self):
        return self.__str__()

    def __getitem__(self, *args, **kwargs):
        return self.__str__().__getitem__(*args, **kwargs)

    def __fspath__(self):
        return self.__str__()

    def rfind(self, *args, **kwargs):
        return self.__str__().rfind(*args, **kwargs)

    def find(self, *args, **kwargs):
        return self.__str__().find(*args, **kwargs)

    @staticmethod
    def _absolute_join(base, *paths, **kwargs):
        absolute_path = os.path.abspath(os.path.join(base, *paths))
        if kwargs.get("required", False) and not os.path.exists(absolute_path):
            raise ImproperlyConfigured("Create required path: {}".format(absolute_path))
        return absolute_path
