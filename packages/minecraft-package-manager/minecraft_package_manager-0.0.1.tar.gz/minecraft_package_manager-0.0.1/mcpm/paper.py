import urllib.request
import json
import mcpm.common as common


PAPER_API_VERSION = "v3"
PAPER_API_BASE_URL = f"https://fill.papermc.io/{PAPER_API_VERSION}"


class PaperApiError(common.ApiError):
    pass


def get_latest_version(name):
    url = PAPER_API_BASE_URL
    url += f'/projects/{name}/versions'
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
    return results["versions"][0]["version"]["id"]


def _get_versions_api_url(name, game_version, channel):
    url = PAPER_API_BASE_URL
    url += f'/projects/{name}/versions/{game_version}/builds?'
    if channel is not None:
        url += f'channel={channel}&'
    return url


def _make_version_record(result, name, game_version):
    file = result["downloads"]["server:default"]
    downloads = [ common.DownloadRecord(file["url"], file["name"], file["checksums"]) ]
    return common.VersionRecord(name, 'paper', f'{game_version}-{result["id"]}', result["channel"], downloads)


def iter_server_versions(server_name, game_version):
    channel = 'STABLE'
    url = _get_versions_api_url(server_name, game_version, channel)
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read())
    if not isinstance(results, list):
        if "error" in results:
            msg = f'The Paper API returned an error ({results["error"]}): {results["message"]}'
            raise PaperApiError(msg)
        else:
            raise PaperApiError('An unknown error occurred. Results should be a list.')
    for result in results:
        yield _make_version_record(result, server_name, game_version)
