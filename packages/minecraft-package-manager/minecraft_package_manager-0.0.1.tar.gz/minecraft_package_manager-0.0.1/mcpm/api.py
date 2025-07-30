import mcpm.modrinth as modrinth
import mcpm.hangar as hangar
import mcpm.geyser as geyser
import mcpm.paper as paper
import mcpm.common as common


def iter_plugin_versions(name, source, channel, loader, game_version):
    backends = {
        'modrinth': modrinth,
        'hangar': hangar,
        'geyser': geyser,
    }
    if source is None:
        source = 'modrinth'
    if channel is None:
        channel = backends[source].get_default_channel()
    yield from backends[source].iter_plugin_versions(name, loader, game_version, channel)


def get_plugin_version(name, source, channel, loader, game_version):
    try:
        return next(iter_plugin_versions(name, source, channel, loader, game_version))
    except StopIteration:
        msg = f'Plugin {name} is not available for Minecraft {game_version} on {loader}.'
        raise common.McpmError(msg)


def iter_server_versions(server_name, game_version):
    backends = {
        'paper': paper,
        'folia': paper,
        'travertine': paper,
        'velocity': paper,
        'waterfall': paper,
    }
    yield from backends[server_name].iter_server_versions(server_name, game_version)


def get_latest_game_version(server_name):
    backends = {
        'paper': paper,
        'folia': paper,
        'travertine': paper,
        'velocity': paper,
        'waterfall': paper,
    }
    return backends[server_name].get_latest_version(server_name)


def get_server_version(server_name, game_version):
    try:
        return next(iter_server_versions(server_name, game_version))
    except StopIteration:
        msg = f'Server {server_name} is not available for Minecraft {game_version}.'
        raise common.McpmError(msg)


def upgrade_server(lock):
    old_ver = lock.server
    new_ver = get_server_version(lock.loader, lock.game_version)
    lock.server = new_ver


def upgrade_plugin(lock, plugin):
    old_ver = lock.find_plugin(plugin)
    new_ver = get_plugin_version(
            old_ver.name, old_ver.source, old_ver.channel,
            lock.loader, lock.game_version
        )
    lock.plugins.remove(old_ver)
    lock.plugins.append(new_ver)


def upgrade_plugins(lock, *plugins):
    if not len(plugins):
        plugins = [ plugin.name for plugin in lock.plugins ]
    for plugin in plugins:
        upgrade_plugin(lock, plugin)
