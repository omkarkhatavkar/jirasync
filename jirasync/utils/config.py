# coding: utf-8
import os

from passlib.context import CryptContext
from xdg import BaseDirectory

from jirasync.utils import echo_error, echo_success


class Config(object):
    def __init__(self):
        self.config_file = self.get_config_file("config.yaml")
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=30000,
        )

    def get_config_file(self, filename):
        """Look for the proper config file path based on
        https://github.com/omkarkhatavkar/jirasync/issues/5
        """
        # Try to find the file from path exported to JIRASYNC_SETTINGS_PATH
        # this variable can be a directory path like /foo/bar
        # and also can be full path like /etc/foo/config.yaml
        path = os.environ.get("JIRASYNC_SETTINGS_PATH")
        if path is not None:
            if not path.endswith(("yaml", "yml")):
                path = os.path.join(path, filename)
            if os.path.exists(path):
                echo_success("Found config file in {}".format(path))
                return path
            else:
                echo_error(
                    "JIRASYNC_SETTINGS_PATH={0} cannot be found".format(path)
                )

        # Try to find in the XDG paths
        # look ~/.config/jirasync/config.yaml
        # then /etc/xdg/jirasync/config.yaml
        # then /etc/jirasync/config.yaml
        BaseDirectory.xdg_config_dirs.append("/etc")
        for dir_ in BaseDirectory.load_config_paths("jirasync"):
            path = os.path.join(dir_, filename)
            if os.path.exists(path):
                echo_success("Found config file in {}".format(path))
                return path

        # load from current directory
        path = os.path.join(os.curdir, filename)
        if os.path.exists(path):
            echo_success("Found config file in {}".format(path))
            return path

        raise IOError("{0} cannot be found".format(path))
