import urllib.request
import json
import mcpm.common as common

GEYSER_API_VERSION = "v2"
GEYSER_API_BASE_URL = f"https://download.geysermc.org/{GEYSER_API_VERSION}"

def _get_project_versions(project_name):
    url = GEYSER_API_BASE_URL
    url += f'/projects/{project_name}'
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
        return results["versions"]

def _get_build_versions(project_name, project_version):
    url = GEYSER_API_BASE_URL
    url += f'/projects/{project_name}/versions/{project_version}'
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
        return results["builds"]

def _get_build_info(project_name, project_version, build_version, server_type):
    url = GEYSER_API_BASE_URL
    url += f'/projects/{project_name}/versions/{project_version}/builds/{build_version}'
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
        record = results["downloads"][server_type]
        name = record.pop("name")
        return name, record

def get_default_channel():
    return 'default'

def iter_plugin_versions(plugin_name, loader, game_version, channel):
    if loader == "paper":
        loader = "spigot"
    proj_ver = _get_project_versions(plugin_name)[-1]
    build_ver = _get_build_versions(plugin_name, proj_ver)[-1]
    filename, checksums = _get_build_info(plugin_name, proj_ver, build_ver, loader)
    url = f"{GEYSER_API_BASE_URL}/projects/{plugin_name}/versions/{proj_ver}/builds/{build_ver}/downloads/{loader}"
    full_version = f'{proj_ver}-{build_ver}'
    idx = filename.rfind('.')
    filename = filename[:idx] + f'-{full_version}' + filename[idx:]
    downloads = [ common.DownloadRecord(url, filename, checksums) ]
    versions = [ common.VersionRecord(plugin_name, 'geyser', full_version, channel, downloads) ]
    for version in versions:
        yield version
