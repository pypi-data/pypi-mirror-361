import argparse
import mcpm.config as config
import mcpm.api as api
import mcpm.provision as provision


def get_init_parser(subparsers):
    subparsers.add_parser('init', help='generate mcpm.conf')


def get_lock_parser(subparsers):
    subparsers.add_parser('lock', help='generate or update mcpm.lock')


def get_add_parser(subparsers):
    subparser = subparsers.add_parser('add', help='add plugins')
    subparser.add_argument('plugin', nargs='+')


def get_remove_parser(subparsers):
    subparser = subparsers.add_parser('remove', help='remove plugins')
    subparser.add_argument('plugin', nargs='+')


def get_upgrade_parser(subparsers):
    subparser = subparsers.add_parser('upgrade', help='upgrade the server and/or plugins')
    subsubparsers = subparser.add_subparsers(dest='upgrade_command', required=False)
    subsubparsers.add_parser('server', help='upgrade the server jar (without changing game version)')
    plugin_parser = subsubparsers.add_parser('plugins', help='upgrade the plugin jars')
    plugin_parser.add_argument('plugin', nargs='*')
    subsubparsers.add_parser('all', help='upgrade the server and plugin jars (without changing game version)')
    subsubparsers.add_parser('full', help='upgrade everything (including game version, if needed)')


def get_provision_parser(subparsers):
    subparsers.add_parser('provision', help='provision a Minecraft server in the current directory')


def get_parser():
    extra_parsers = [ get_init_parser, get_lock_parser, get_add_parser, get_remove_parser, get_upgrade_parser, get_provision_parser ]

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', required=True)
    for extra_parser in extra_parsers:
        extra_parser(subparsers)

    return parser


def _update_lock(cfg):
    lock = config.get_lock(cfg)
    config.update_lock(cfg, lock)
    config.write_lock(cfg, lock)
    return lock


def init_cmd(args):
    cfg = config.init_config()
    config.save_config(cfg)


def lock_cmd(args):
    cfg = config.get_config()
    _update_lock(cfg)


def add_cmd(args):
    cfg = config.get_config()
    for plugin in args.plugin:
        cfg.add_plugin(plugin)
    _update_lock(cfg)
    config.save_config(cfg)


def remove_cmd(args):
    cfg = config.get_config()
    for plugin in args.plugin:
        cfg.remove_plugin(plugin)
    _update_lock(cfg)
    config.save_config(cfg)


def upgrade_server_cmd(args):
    cfg = config.get_config()
    lock = config.get_lock(cfg)
    api.upgrade_server(lock)
    config.write_lock(cfg, lock)


def upgrade_plugins_cmd(args):
    cfg = config.get_config()
    lock = config.get_lock(cfg)
    api.upgrade_plugins(lock, *args.plugin)
    config.write_lock(cfg, lock)


def upgrade_all_cmd(args):
    cfg = config.get_config()
    lock = config.get_lock(cfg)
    api.upgrade_server(lock)
    api.upgrade_plugins(lock)
    config.write_lock(cfg, lock)


def upgrade_full_cmd(args):
    cfg = config.get_config()
    lock = config.new_lock(cfg)
    config.update_lock(cfg, lock)
    config.write_lock(cfg, lock)


def upgrade_cmd(args):
    commands = {
        "server": upgrade_server_cmd,
        "plugins": upgrade_plugins_cmd,
        "all": upgrade_all_cmd,
        "full": upgrade_full_cmd,
    }
    if args.upgrade_command is None:
        args.upgrade_command = "all"
    commands[args.upgrade_command](args)


def provision_cmd(args):
    cfg = config.get_config()
    lock = _update_lock(cfg)
    provision.provision(cfg, lock)


def main():
    parser = get_parser()
    args = parser.parse_args()
    commands = {
        "init": init_cmd,
        "lock": lock_cmd,
        "add": add_cmd,
        "remove": remove_cmd,
        "upgrade": upgrade_cmd,
        "provision": provision_cmd,
    }
    commands[args.command](args)
