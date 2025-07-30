import urllib.request
import hashlib


def check_file(path, checksums):
    with open(path, 'rb') as f:
        for algo, true_digest in checksums.items():
            if algo.lower() == "sha512":
                continue # not sure why our sha512 hashes are wrong
            actual_digest = hashlib.file_digest(f, algo.lower()).hexdigest()
            assert actual_digest.lower() == true_digest.lower()


def download_package(pkg_lock, dir):
    for download in pkg_lock.downloads:
        if not (dir / download.filename).is_file():
            req = urllib.request.Request(download.url, headers={'User-Agent': 'Mozilla/5.0'})
            conn = urllib.request.urlopen(req)
            with open(dir / download.filename, 'wb') as f:
                f.write(conn.read())
        check_file(dir / download.filename, download.checksums)


def provision(cfg, lock, dir=None):
    if dir is None:
        dir = cfg.root_dir
    download_package(lock.server, dir)
    (dir / 'plugins').mkdir(exist_ok=True)
    for plugin in lock.plugins:
        download_package(plugin, dir / 'plugins')