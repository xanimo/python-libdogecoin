import os
import sys
import pathlib
import platform
import pprint
import subprocess
from urllib.parse import urlsplit
from setuptools import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


the_file_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(the_file_dir))
import build_utils

version = '0.1.2'

platform_system, platform_machine, is_64bits = build_utils.get_platform_info()

print("#" * 12, 'this platform information:')
print("system:", platform_system)
print("python version:", platform.python_version())
print("machine:", platform_machine)
print("is_64bits:", is_64bits)
print("#" * 12)


# prepare libdogecoin build dir
if not os.getenv("LIBDOGECOIN_BUILD_DIR", ""):
    libdogecoin_release_dir = build_utils.get_libdogecoin_release_dir(version)
    #build_utils.eprint(libdogecoin_release_dir)
    if not pathlib.Path(libdogecoin_release_dir).exists():
        build_utils.get_libdogecoin_release(version)

# get library|header|extra_objects
build_dirs = build_utils.get_build_dirs(version)
#pprint.pprint(build_dirs)
sys.stdout.flush()
sys.stderr.flush()
libdogecoin_extension = [Extension(
    name=               "libdogecoin_py.libdogecoin",
    language=           "c",
    sources=            ["src/libdogecoin_py/libdogecoin.pyx"],
    include_dirs=       build_dirs['include_dirs'],
    library_dirs =      build_dirs['library_dirs'],
    extra_objects=      build_dirs['extra_objects'],
)]

setup(
    version=                        version,

    long_description=               open("README.md", "r").read(),
    long_description_content_type=  "text/markdown",

    author=                         "Jackie McAninch",
    author_email=                   "jackie.mcaninch.2019@gmail.com",
    maintainer=                     "bluezr",
    maintainer_email=               "bluezr@dogecoin.com",
    url=                            "https://github.com/xanimo/python-libdogecoin",

    cmdclass =                      {'build_ext': build_ext},
    ext_modules=                    cythonize(libdogecoin_extension, language_level = "3"),
    include_package_data=           True,
    packages=                       ["libdogecoin_py"],
    package_dir=                    {"": "src"},
    zip_safe=                       False
)
