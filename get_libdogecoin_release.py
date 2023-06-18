#!/usr/bin/python3
"""
get platorm information(system: e.g: linux, machine: x86_64), then
get platform-dependent libdogecoin libraries and header files

example: python3 get_libdogecoin_release.py --release_version 0.1.0
"""
import os
import pathlib
import sys
import shutil
from urllib.parse import urlsplit
import argparse
import tempfile
import requests


the_file_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(the_file_dir)
import build_utils


def get_libdogecoin_release(release_version, output_dir):
    """
    get libdogecoin release(libraries, header file...) to output_dir
    
    :param release_version: 
    :param output_dir:
    :return str: libdogecoin release directory
    """
    # get libdogecoin release url. eg:https://github.com/dogecoinfoundation/libdogecoin/releases/download/v0.1.2/libdogecoin-0.1.2-x86_64-pc-linux-gnu.tar.gz

    tarball_url = build_utils.get_libdogecoin_release_tarball_url(release_version)

    # tarball_filename. e.g:libdogecoin-0.1.2-x86_64-pc-linux-gnu.tar.gz
    tarball_filename = os.path.basename(urlsplit(tarball_url).path)

    # 
    sha256sums_url = tarball_url.replace(tarball_filename, "SHA256SUMS.asc")

    # download tarball
    print("#### download libdogecoin release tarball:", tarball_url)
    req = requests.get(tarball_url)
    with open(tarball_filename,'wb') as output_file:
        output_file.write(req.content)

    # get tarball sha256sums
    sha256sums_content = requests.get(sha256sums_url).content.decode("utf-8").split("\n")

    # verify
    tarball_sha256sum = build_utils.get_file_sha256sum(tarball_filename)
    line = "%s  %s" % (tarball_sha256sum, tarball_filename)

    assert line in sha256sums_content, line

    # extract
    assert tarball_filename.endswith(".zip") or tarball_filename.endswith(".tar.gz"), "unknown tarball format: " + tarball_filename

    tarball_full_path = the_file_dir.joinpath(tarball_filename).as_posix()
    
    shutil.unpack_archive(tarball_full_path, output_dir)
    
    # remove tarball filename
    os.remove(tarball_full_path)

    print("#### get libdogecoin release done")


def test_get_libdogecoin_release():
    """
    test get_libdogecoin_release
    """
    release_version = build_utils.default_release_version
    with tempfile.TemporaryDirectory() as output_dir:
        get_libdogecoin_release(release_version, output_dir)

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", help="extract libdogecoin release to directory", default=str(the_file_dir))
    parser.add_argument("--release_version", help="libdogecoin release version",
                        choices=build_utils.release_version_list,
                        required=True)

    args = parser.parse_args()
    get_libdogecoin_release(args.release_version, args.output_dir)
    sys.exit(0)
    


