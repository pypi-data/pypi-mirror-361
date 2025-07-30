import os

class ApiError(Exception):
    pass


class McpmError(Exception):
    pass

class DownloadRecord:

    def __init__(self, url, filename, checksums):
        self._url = url
        self._filename = filename
        self._checksums = checksums

    @property
    def url(self):
        return self._url

    @property
    def filename(self):
        return self._filename

    @property
    def checksums(self):
        return self._checksums

    def __repr__(self):
        return f'{self.filename} ({self.url})'

    def to_dict(self):
        return {
            'url': self.url,
            'filename': self.filename,
            'checksums': self.checksums,
        }

    @staticmethod
    def from_dict(value):
        return DownloadRecord(value["url"], value["filename"], value["checksums"])


class VersionRecord:

    def __init__(self, name, source, version, channel, downloads):
        self._source = source
        self._name = name
        self._version = version
        self._channel = channel
        self._downloads = downloads

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def version(self):
        return self._version

    @property
    def channel(self):
        return self._channel

    @property
    def downloads(self):
        return self._downloads

    def __repr__(self):
        s = f'{self.version} ({self.channel})' + os.linesep
        for download in self.downloads:
            s += f'- {download}' + os.linesep
        return s.strip()

    def to_dict(self):
        return {
            'name': self.name,
            'source': self.source,
            'version': self.version,
            'channel': self.channel,
            'downloads': [ o.to_dict() for o in self.downloads ]
        }

    @staticmethod
    def from_dict(value):
        downloads = [ DownloadRecord.from_dict(r) for r in value['downloads'] ]
        return VersionRecord(
                value['name'], value['source'],
                value['version'], value['channel'],
                downloads
            )


class LockRecord:

    def __init__(self, loader, game_version, server=None, plugins=None):
        self._loader = loader
        self._game_version = game_version
        if server is not None:
            self._server = server
        else:
            self._server = None
        if plugins is not None:
            self._plugins = plugins
        else:
            self._plugins = []

    @property
    def loader(self):
        return self._loader

    @property
    def game_version(self):
        return self._game_version

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, value):
        self._server = value

    @property
    def plugins(self):
        return self._plugins

    def find_plugin(self, name):
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def remove_plugins_except(self, plugin_names):
        self._plugins = [
            plugin for plugin in self._plugins if plugin.name in plugin_names
        ]

    def to_dict(self):
        return {
            'loader': self.loader,
            'game_version': self.game_version,
            'server': self.server.to_dict(),
            'plugins': [ o.to_dict() for o in self.plugins ],
        }

    @staticmethod
    def from_dict(value):
        server = None
        plugins = None
        if 'server' in value:
            server = VersionRecord.from_dict(value['server'])
        if 'plugins' in value:
            plugins = [ VersionRecord.from_dict(r) for r in value['plugins'] ]
        return LockRecord(value['loader'], value['game_version'], server, plugins)
