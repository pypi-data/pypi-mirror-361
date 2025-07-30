import urllib.request
import json
import mcpm.common as common


HANGAR_API_VERSION = "v1"
HANGAR_API_BASE_URL = f"https://hangar.papermc.io/api/{HANGAR_API_VERSION}"


class HangarApiError(common.ApiError):
    pass


def _get_versions_api_url(name, loader, game_version, channel):
    url = HANGAR_API_BASE_URL
    url += f'/projects/{name}/versions?'
    if loader is not None:
        url += f'platform={loader}&'
    if game_version is not None:
        url += f'platformVersion={str(game_version)}&'
    if channel is not None:
        url += f'channel={channel}&'
    return url


def _make_version_record(result, name, loader):
    dl = result["downloads"][loader.upper()]
    dl_hashes = {
        k.removesuffix("Hash"): v
        for k, v in dl["fileInfo"].items()
        if k.endswith("Hash")
    }
    downloads = [ common.DownloadRecord(dl["downloadUrl"], dl["fileInfo"]["name"], dl_hashes) ]
    return common.VersionRecord(name, 'hangar', result["name"], result["channel"]["name"], downloads)


def get_default_channel():
    return 'release'


def iter_plugin_versions(plugin_name, loader, game_version, channel):
    url = _get_versions_api_url(plugin_name, loader, game_version, channel)
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
    if "httpError" in results:
        msg = f'The Hangar API returned an error ({results["httpError"]["statusCode"]}): {results["message"]}'
        raise HangarApiError(msg)
    if "result" not in results:
        raise HangarApiError('An unknown error occurred. Json structure unrecognized.')
    assert results["pagination"]["limit"] > results["pagination"]["count"] # i'll deal with pagination later
    results = results["result"]
    for result in results:
        yield _make_version_record(result, plugin_name, loader)