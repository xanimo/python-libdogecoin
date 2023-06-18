#! /usr/bin/python3

import pathlib
import os
import sys
import platform
import pprint
import subprocess
import hashlib
from urllib.parse import urlsplit

the_file_dir = pathlib.Path(__file__).resolve().parent

release_version_list = ["0.1.0", "0.1.1", "0.1.2"]
default_release_version = '0.1.0'

libdogecoin_release_tarball_url_template = 'https://github.com/dogecoinfoundation/libdogecoin/releases/download/v{version}/{tarball}'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_platform_info():
    platform_system = platform.system()
    platform_machine = platform.machine()
    is_64bits = sys.maxsize > pow(2, 32)
    return platform_system, platform_machine, is_64bits

error_unsupported_platform = "unsupported platform: system: %s, machine: %s, is_64bits: %s" % get_platform_info()


system_file_map = {
    "Linux": {"x86_64": "libdogecoin-{version}-x86_64-pc-linux-gnu.tar.gz", 
              "i686": "libdogecoin-{version}-i686-pc-linux-gnu.tar.gz", 
              "aarch64": "libdogecoin-{version}-aarch64-linux-gnu.tar.gz", 
              "arm": "libdogecoin-{version}-arm-linux-gnueabihf.tar.gz"},
    "Windows": {"x86_64": "libdogecoin-{version}-x86_64-w64-mingw32.zip", 
                "i686": "libdogecoin-{version}-i686-w64-mingw32.zip"},
    "Darwin": {"x86_64": "libdogecoin-{version}-x86_64-apple-darwin14.tar.gz"}
}


def get_libdogecoin_release_tarball_url(release_version, platform_system=None, platform_machine=None, is_64bits=None):

    if platform_system is None:
        platform_system, platform_machine, is_64bits = get_platform_info()

    tarball = None
    sys.stdout.flush()
    if platform_system == "Windows":
        assert platform_machine == "AMD64"
        if is_64bits:
            tarball = system_file_map["Windows"]["x86_64"]
        else:
            tarball = system_file_map["Windows"]["i686"]
    elif platform_system == "Linux":
        linux_tarball = system_file_map["Linux"]
        if platform_machine == "x86_64" and is_64bits:
            tarball = linux_tarball["x86_64"]
        elif platform_machine == "aarch64" and is_64bits:
            tarball = linux_tarball["aarch64"]
        elif platform_machine == "i686":
            tarball = linux_tarball["i686"]
        else:
            raise RuntimeError(error_unsupported_platform)
    elif platform_system == "Darwin":
        darwin_ball = system_file_map["Darwin"]
        #assert platform_machine == "x86_64", platform_machine
        #if platform_machine == "x86_64" and is_64bits:
        tarball = darwin_ball["x86_64"]
    else:
        raise RuntimeError(error_unsupported_platform)


    tarball = tarball.format(version=release_version)
    url = libdogecoin_release_tarball_url_template.format(tarball=tarball, version=release_version)
    return url

def test_get_libdogecoin_release_tarball_url():
    release_version = default_release_version
    
    # windows
    platform_system, platform_machine = "Windows", "AMD64"
    print(get_libdogecoin_release_tarball_url(release_version, platform_system, platform_machine, False))
    print(get_libdogecoin_release_tarball_url(release_version, platform_system, platform_machine, True))
    # linux
    platform_system = "Linux"
    print(get_libdogecoin_release_tarball_url(release_version, platform_system, "x86_64", True))

    print(get_libdogecoin_release_tarball_url(release_version, platform_system, "aarch64", True))
    print(get_libdogecoin_release_tarball_url(release_version, platform_system, "i686", False))

    # macos, darwin
    print(get_libdogecoin_release_tarball_url(release_version, "Darwin", "x86_64", True))

def get_file_sha256sum(filename):
    """
    return filename sha256sum

    :param filename: string
    :return sha256sum: string
    """
    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
    # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

def test_get_file_sha256sum():
    f = pathlib.Path(__file__).resolve().as_posix()
    get_file_sha256sum(f)
    return


def get_windows_extra_dirs():
    """
    get windows platform-depends library
    
    :return new_dirs()
    """
    platform_system, platform_machine, is_64bits = get_platform_info()
    is_windows = platform_system == "Windows"
    is_amd64 = platform_machine == "AMD64"
    
    dirs = new_dirs()
    if not is_windows:
        return dirs
    if not is_amd64:
        eprint(error_unsupported_platform)
        return dirs

    build_path = None
    if is_64bits:
        build_path = the_file_dir.joinpath("libs/amd64")
    else:
        build_path = the_file_dir.joinpath("libs/win32")

    dirs['library_dirs'].append(str(build_path))
    dirs['extra_objects'].extend([str(_object) for _object in build_path.glob("*.a")])
    
    return dirs


def new_dirs():
    dirs = dict(include_dirs=[],library_dirs=[], extra_objects=[], )
    return dirs

def get_libdogecoin_release_dir(release_version):
    """ return release dir. e.g: 
    :param release_version: libdogecoin release version.e.g: 0.1.0
    :return str: release directory: e.g:  libdogecoin-0.1.2-aarch64-linux-gnu
    """
    tarball_url = get_libdogecoin_release_tarball_url(release_version)
    tarball = os.path.basename(urlsplit(tarball_url.strip()).path)

    if tarball.endswith(".tar.gz"):
        tarball_path = tarball[:-len(".tar.gz")]
    elif tarball.endswith(".zip"):
        tarball_path = tarball[:-len(".zip")]
    else:
        raise ValueError("unknow tarball suffix: %s" % tarball)

    release_dir = the_file_dir.joinpath(tarball_path)
    return release_dir

def get_libdogecoin_release(release_version):
    command = the_file_dir.joinpath('get_libdogecoin_release.py').as_posix()
    args = ['python', command, 
            '--release_version', release_version]
    p = subprocess.run(args, check=True)
    return
    
def get_build_dirs(release_version=None):
    """
    """
    # get from env variables: LIBDOGECOIN_BUILD_DIR
    libdogecoin_build_dir = os.getenv("LIBDOGECOIN_BUILD_DIR", "")
    # get build directory
    build_dir = None
    if libdogecoin_build_dir:
        print("env: LIBDOGECOIN_BUILD_DIR:", libdogecoin_build_dir)
        build_dir = pathlib.Path(libdogecoin_build_dir).resolve()
        assert build_dir.is_dir, "LIBDOGECOIN_BUILD_DIR is not exists:" + build_dir.as_posix()
    else:
        build_dir = get_libdogecoin_release_dir(release_version)
        if build_dir.exists():
            print("build dir:" + str(build_dir))
        else:
            raise RuntimeError("missing build_dir: %s. maybe 'python3 get_libdogecoin_release.py --release_version %s' can fix it!" % (build_dir, release_version))

    # 
    dirs = new_dirs()
    dirs['include_dirs'].append(str(build_dir.joinpath("include")))
    dirs['library_dirs'].append(str(build_dir.joinpath("lib")))
    dirs['extra_objects'].append(str(build_dir.joinpath("lib/libdogecoin.a")))
    
    # windows
    windows_build_dirs = get_windows_extra_dirs()
    dirs['library_dirs'].extend(windows_build_dirs['library_dirs'])
    dirs['extra_objects'].extend(windows_build_dirs['extra_objects'])
    return dirs
    
def test_get_build_dirs():
    release_version = '0.1.0'
    dirs = get_build_dirs(release_version)
    pprint.pprint(dirs)

    # 
    os.environ['LIBDOGECOIN_BUILD_DIR'] = "libdogecoin"
    dirs = get_build_dirs()
    pprint.pprint(dirs)

