import urllib.request
import json
import mcpm.common as common


MODRINTH_API_VERSION = "v2"
MODRINTH_API_BASE_URL = f"https://api.modrinth.com/{MODRINTH_API_VERSION}"


class ModrinthApiError(common.ApiError):
    pass


def _get_versions_api_url(name, loader, game_version, channel):
    url = MODRINTH_API_BASE_URL
    url += f'/project/{name}/version?'
    if loader is not None:
        url += f'loaders=[%22{loader}%22]&'
    if game_version is not None:
        url += f'game_versions=[%22{str(game_version)}%22]&'
    if channel is not None:
        url += f'version_type={channel}&'
    return url


def _make_version_record(result, name):
    downloads = [
            common.DownloadRecord(file["url"], file["filename"], file["hashes"])
            for file in result["files"] if file["primary"]
        ]
    return common.VersionRecord(name, 'modrinth', result["version_number"], result["version_type"], downloads)


def get_default_channel():
    return 'release'


def iter_plugin_versions(plugin_name, loader, game_version, channel):
    url = _get_versions_api_url(plugin_name, loader, game_version, channel)
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
    if not isinstance(results, list):
        if "error" in results:
            msg = f'The Modrinth API returned an error ({results["error"]}): {results["description"]}'
            raise ModrinthApiError(msg)
        else:
            raise ModrinthApiError('An unknown error occurred. Results should be a list.')
    for result in results:
        yield _make_version_record(result, plugin_name)
