# libdogecoin-py contribute

## code for libdogecoin release
after libdogecoin release version(e.g: v0.1.2)

clone the repo
```
git clone https://github.com/joijuke/python-libdogecoin-v0.1.2.git
```

checkout new branch
```
git checkout -b v0.1.2
```

change setup.py:version to 0.1.2

write code

build_ext, setup.py will auto get libdogecoin release used get_libdogecoin_release.py
```
python3 setup.py clean --all && python3 setup.py build_ext
```

install
```
python3 -m pip  install -vv . 
```

## code for libdogecoin new dev branch
if libdogecoin create new dev branch(unpublished) e.g:0.1.2-dev, use the follow step code

change setup.py version to 0.1.2

change .github/workflow/dev.yml env libdogecoin_branch to 0.1.2-dev

clone libdogecoin
```
git clone --recurse-submodules --branch 0.1.2-dev https://github.com/dogecoinfoundation/libdogecoin.git
```

build libdogecoin on linux
```
export LIBDOGECOIN_BUILD_DIR=absolut_path/to/build
cd libdogecoin
sudo apt-get install -y autoconf automake libtool build-essential libevent-dev libunistring-dev
./autogen.sh && ./configure --prefix=$LIBDOGECOION_BUILD_DIR && make && make install
```

change to the repo dir

build_ext. when env LIBDOGECOIN_BUILD_DIR exits, setup.py will priority use LIBDOGECOIN_BUILD_DIR search libdogecoin header file and link objects.
```
export LIBDOGECOIN_BUILD_DIR=absolut_path/to/build
python3 setup.py build_ext
```

## utils
get platform-depends libdogecoin release
```
python3 get_libdogecoin_release.py --release_version 0.1.2
```
build_utils.py some utils for build extension

## test

when the code is done, test the code with the following command

test all linux archs
```
cibuildwheel --platform linux --arch x86_64
```

test special platform and archs
```
cibuildwheel --only cp39-manylinux_x86_64
```

platform and archs options at https://cibuildwheel.readthedocs.io/en/stable/options/#archs

## github CI
.github/workflow/dev.yml: test dev branch e.g:0.1.2-dev

.github/workflow/build_and_upload.yml: test all platform/archs, build and upload pypi
