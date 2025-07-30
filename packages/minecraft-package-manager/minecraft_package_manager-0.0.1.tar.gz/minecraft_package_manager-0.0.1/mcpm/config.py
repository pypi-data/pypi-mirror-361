import tomlkit
import json
import pathlib
import os
import mcpm.common as common
import mcpm.api as api

def _find_root_directory(dir=None):
    if dir is None:
        dir = pathlib.Path.cwd()
    if (dir / 'mcpm.toml').is_file():
        return dir
    if dir.parent:
        return _find_root_directory(dir.parent)
    return None

def disambiguate_plugin_name(name):
    source = None
    channel = None
    if "/" in name:
        source, name = name.split('/', maxsplit=1)
    if "#" in name:
        name, channel = name.rsplit('#', maxsplit=1)
    return name, source, channel


class McpmPluginConfig:
    def __init__(self, full_name):
        self._full_name = full_name
        self._name, self._source, self._channel = disambiguate_plugin_name(full_name)

    @property
    def full_name(self):
        return self._full_name

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def channel(self):
        return self._channel


class McpmConfig:
    DEFAULT_VERSION = "latest"
    DEFAULT_LOADER = "paper"

    def __init__(self, root_dir, cfg):
        self._root_dir = root_dir
        self._doc = cfg
        if "server" not in self._doc:
            self._doc["server"] = {}
        if "version" not in self._doc["server"]:
            self._doc["server"]["version"] = self.DEFAULT_VERSION
        if "loader" not in self._doc["server"]:
            self._doc["server"]["loader"] = self.DEFAULT_LOADER
        if "plugins" not in self._doc["server"]:
            self._doc["server"]["plugins"] = []
        assert self._doc["server"]["loader"] == "paper" # only supporting paper for now

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def version(self):
        return self._doc["server"]["version"]

    @version.setter
    def version(self, value):
        self._doc["server"]["version"] = value

    @property
    def loader(self):
        return self._doc["server"]["loader"]

    @loader.setter
    def loader(self, value):
        self._doc["server"]["loader"] = value

    @property
    def plugins(self):
        for plugin in self._doc["server"]["plugins"]:
            yield McpmPluginConfig(plugin)

    def find_plugin(self, name):
        name, source, channel = disambiguate_plugin_name(name)
        for plugin in self.plugins:
            if plugin.name != name:
                continue
            if source is not None and plugin.source != source:
                continue
            if channel is not None and plugin.channel != channel:
                continue
            return plugin
        return None

    def add_plugin(self, full_name):
        name, source, channel = disambiguate_plugin_name(full_name)
        assert self.find_plugin(name) is None
        self._doc["server"]["plugins"].append(full_name)

    def remove_plugin(self, name):
        plugin = self.find_plugin(name)
        assert plugin is not None
        self._doc["server"]["plugins"].remove(plugin.full_name)

def init_config(root_dir=None):
    if root_dir is None:
        root_dir = pathlib.Path.cwd()
    if (root_dir / "mcpm.toml").is_file():
        msg = f"The mcpm.toml file already exists in directory {root_dir}."
        raise common.McpmError(msg)
    cfg = McpmConfig(root_dir, {})
    doc = tomlkit.document()
    doc.add(tomlkit.comment("generated with 'mcpm init'. feel free to modify."))
    doc["server"] = tomlkit.table()
    doc["server"]["loader"] = cfg.loader
    doc["server"]["loader"].comment("paper is the only supported loader for now.")
    doc["server"]["version"] = cfg.version
    doc["server"]["version"].comment("can be a minecraft number, or the word 'latest'.")
    doc["server"].add(tomlkit.nl())
    doc["server"].add(tomlkit.comment("add new plugins with 'mcpm add' or by modifying the list below."))
    doc["server"]["plugins"] = []
    return McpmConfig(root_dir, doc)


def get_config():
    root_dir = _find_root_directory()
    with open(root_dir / "mcpm.toml") as f:
        doc = tomlkit.parse(f.read())
    return McpmConfig(root_dir, doc)


def save_config(cfg):
    with open(cfg.root_dir / "mcpm.toml", "w") as f:
        f.write(tomlkit.dumps(cfg._doc))


def new_lock(cfg):
    game_version = cfg.version
    if game_version == "latest":
        game_version = api.get_latest_game_version(cfg.loader)
    return common.LockRecord(cfg.loader, game_version)


def get_lock(cfg):
    if not (cfg.root_dir / "mcpm.lock").is_file():
        return new_lock(cfg)
    with open(cfg.root_dir / "mcpm.lock") as f:
        lock_dict = json.loads(f.read())
        return common.LockRecord.from_dict(lock_dict)

def update_lock(cfg, lock_record):
    if cfg.loader != lock_record.loader:
        msg = f"The mcpm.lock uses loader '{lock_record.loader}', but mcpm.toml specifies loader '{cfg.loader}'."
        msg += os.linesep + "Please delete mcpm.lock in order to switch loaders."
        raise common.McpmError(msg)
    if cfg.version != "latest" and cfg.version != lock_record.game_version:
        msg = f"The mcpm.lock uses Minecraft {lock_record.game_version}, but mcpm.toml specifies version {cfg.version}."
        msg += os.linesep + "Please delete mcpm.lock in order to switch game versions."
        raise common.McpmError(msg)
    if lock_record.server is None:
        lock_record.server = api.get_server_version(lock_record.loader, lock_record.game_version)
    for plugin in cfg.plugins:
        if lock_record.find_plugin(plugin.name) is None:
            plugin_version = api.get_plugin_version(
                    plugin.name, plugin.source, plugin.channel,
                    lock_record.loader, lock_record.game_version
                )
            lock_record.add_plugin(plugin_version)
    lock_record.remove_plugins_except([
        plugin.name for plugin in cfg.plugins
    ])

def write_lock(cfg, lock):
    with open(cfg.root_dir / "mcpm.lock", "w") as f:
        f.write(json.dumps(lock.to_dict(), indent=2))
