#!/bin/bash
export LC_ALL=C
set -e -o pipefail

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

has_param() {
    local term="$1"
    shift
    for arg; do
        if [[ $arg == "$term" ]]; then
            return 0
        fi
    done
    return 1
}

check_sig() {
    if gpg --verify $1 $2; then
        printf "$green> GPG signature looks good$reset\n"
    else
        printf "$red> GPG signature for this libdogecoin release is invalid! This is BAD and may mean the release has been tampered with. It is strongly recommended that you report this to the libdogecoin developers.$reset\n"
        exit 1;
    fi
}

USE_SUDO="sudo "
if has_param '--docker' "$@"; then
    USE_SUDO=""
fi

check_tools() {
    for cmd in "$@"; do
        if ! command -v "$cmd" > /dev/null 2>&1; then
            echo "ERR: This script requires that '$cmd' is installed and available in your \$PATH"
            echo $@
            $USE_SUDO apt-get update
            $USE_SUDO apt-get -y install $@
        fi
    done
}

TAG=""
OS=""
ARCH=""
ML=""
ALL_HOST_TRIPLETS=""
TARGET_HOST_TRIPLET=""
for i in "$@"
do
case $i in
    -h=*|--host=*)
        HOST="${i#*=}"
        ALL_HOST_TRIPLETS=($HOST)
        case "$ALL_HOST_TRIPLETS" in
            "arm-linux-gnueabihf")
                OS=linux
                ARCH=armv7l
                ML=linux_armv7l
                ARCH_PACKAGES+="g++-arm-linux-gnueabihf "
                ARCH_PACKAGES+="qemu-user-static qemu-user"
                TARGET_ARCH="armhf"
            ;;
            "aarch64-linux-gnu")
                OS=linux
                ARCH=aarch64
                ML=manylinux2014_aarch64
                ARCH_PACKAGES+="g++-aarch64-linux-gnu "
                ARCH_PACKAGES+="qemu-user-static qemu-user"
                TARGET_ARCH="arm64"
            ;;
            "x86_64-w64-mingw32")
                ARCH=x86_64
                ML=manylinux2014_x86_64
                ARCH_PACKAGES+="g++-mingw-w64 "
                TARGET_ARCH="amd64"
                plat=win-amd64
            ;;
            "i686-w64-mingw32")
                ARCH=x86
                ML=manylinux2014_i686
                ARCH_PACKAGES+="g++-mingw-w64 "
                TARGET_ARCH="i386"
                plat=win32
            ;;
            "x86_64-apple-darwin14")
                OS=macos
                ARCH=x86_64
                ML=manylinux2014_x86_64
            ;;
            "x86_64-pc-linux-gnu")
                OS=linux
                ARCH=x86_64
                ML="manylinux2014_x86_64"
            ;;
            "i686-pc-linux-gnu")
                OS=linux
                ARCH=i686
                ML=manylinux2014_i686
                ARCH_PACKAGES+="g++-multilib "
                TARGET_ARCH="i386"
            ;;
            "all")
                ALL_HOST_TRIPLETS=("x86_64-pc-linux-gnu" "i686-pc-linux-gnu" "aarch64-linux-gnu" "arm-linux-gnueabihf" "x86_64-apple-darwin14" "x86_64-w64-mingw32" "i686-w64-mingw32")
            ;;
            *)
                ERROR=1
            ;;
        esac
    ;;
    -o=*|--os=*)
        BUILD_PREFIX="${i#*=}"
    ;;
    -p=*|--prefix=*)
        BUILD_PREFIX="${i#*=}"
    ;;
    -t=*|--tag=*)
        TAG="${i#*=}"
    ;;
    *)
        ERROR=1
    ;;
esac
done

if [ "$ERROR" ]; then
    echo "Please provide a host to build and try again."
    exit $ERROR
fi

check_tools python3 python-is-python3 python3-venv curl tar unzip gpg patchelf $ARCH_PACKAGES

if [ ! "$TAG" ]; then
    TAG=0.1.0
fi

reset="\033[0m"
red="\033[31m"
green="\033[32m"
ARCHIVE=""
FILE="libdogecoin-$TAG-"
EXTENSION=".tar.gz"
CHECKSUMS="SHA256SUMS.asc"
URL=https://github.com/dogecoinfoundation/libdogecoin/releases/download/v0.1.0/


pushd src
    if [[ "$ALL_HOST_TRIPLETS" != "" ]]; then
        END=$((${#ALL_HOST_TRIPLETS[@]} - 1))
        curl -L -O $URL$CHECKSUMS
        curl https://raw.githubusercontent.com/dogecoinfoundation/libdogecoin/main/contrib/signing-keys/xanimo-key.pgp | gpg --import
        check_sig $CHECKSUMS
        for i in "${!ALL_HOST_TRIPLETS[@]}"
        do
        :
            TARGET_HOST_TRIPLET="${ALL_HOST_TRIPLETS[$i]}"
            BUILD_PREFIX="`pwd`/lib"
            echo $BUILD_PREFIX
            SIG_STATUS=""
            if [ ! -d "$BUILD_PREFIX" ]; then
                mkdir -p $BUILD_PREFIX
            fi
            if [ ! -d "include" ]; then
                mkdir -p include
            fi
            if [[ "$TARGET_HOST_TRIPLET" == *-mingw32 ]]; then
                EXTENSION=".zip"
                ARCHIVE="$FILE$TARGET_HOST_TRIPLET$EXTENSION"
                curl -L -O "$URL$ARCHIVE"
                SIG_STATUS=$(grep "$ARCHIVE" "$CHECKSUMS" | sha256sum -c | grep OK)
                if [ "$SIG_STATUS" == "$ARCHIVE: OK" ]; then
                    printf "$green> checksum looks good$reset\n"
                else
                    printf "$red> checksum for this libdogecoin release is invalid! This is BAD and may mean the release has been tampered with. It is strongly recommended that you report this to the libdogecoin developers.$reset\n"
                    exit 1;
                fi
                unzip -o -j "$FILE$TARGET_HOST_TRIPLET$EXTENSION" "$FILE$TARGET_HOST_TRIPLET/lib/libdogecoin.a"  -d lib
                unzip -o -j "$FILE$TARGET_HOST_TRIPLET$EXTENSION"  "$FILE$TARGET_HOST_TRIPLET/include/libdogecoin.h" -d include
                rm $ARCHIVE
            else
                ARCHIVE=$FILE$TARGET_HOST_TRIPLET$EXTENSION
                curl -L -O "$URL$ARCHIVE"
                SIG_STATUS=$(grep "$ARCHIVE" "$CHECKSUMS" | sha256sum -c | grep OK)
                if [ "$SIG_STATUS" == "$ARCHIVE: OK" ]; then
                    printf "$green> checksum looks good$reset\n"
                else
                    printf "$red> checksum for this libdogecoin release is invalid! This is BAD and may mean the release has been tampered with. It is strongly recommended that you report this to the libdogecoin developers.$reset\n"
                    exit 1;
                fi
                tar xvf $ARCHIVE "$FILE$TARGET_HOST_TRIPLET/lib/libdogecoin.a"
                tar xvf $ARCHIVE "$FILE$TARGET_HOST_TRIPLET/include/libdogecoin.h"
                mv $FILE$TARGET_HOST_TRIPLET/lib/libdogecoin.a `pwd`/lib/
                mv $FILE$TARGET_HOST_TRIPLET/include/libdogecoin.h `pwd`/include/
                rm -rf $FILE$TARGET_HOST_TRIPLET*
            fi

        done
        rm $CHECKSUMS
    fi

    if [ "$TARGET_HOST_TRIPLET" == "x86_64-w64-mingw32" ] || [ "$TARGET_HOST_TRIPLET" == "i686-w64-mingw32" ]; then
        ../combine.sh --target ./lib/libdogecoin.a \
        --append "/usr/lib/gcc/$TARGET_HOST_TRIPLET/10-win32/libgcc.a \
        /usr/$TARGET_HOST_TRIPLET/lib/libmoldname.a \
        /usr/$TARGET_HOST_TRIPLET/lib/libmsvcrt.a \
        /usr/$TARGET_HOST_TRIPLET/lib/libadvapi32.a \
        /usr/$TARGET_HOST_TRIPLET/lib/libmingwex.a"
        if [ "$plat" == "win32" ]; then
            /mnt/c/Users/$(basename $(wslpath "$(wslvar USERPROFILE)"))/AppData/Local/Programs/Python/Python310-32/python.exe -m build \
            -C--global-option=egg_info \
            -C--global-option=--tag-build=0.1.0 \
            -C--plat-name=$plat -w
        else
            /mnt/c/Users/$(basename $(wslpath "$(wslvar USERPROFILE)"))/AppData/Local/Programs/Python/Python310/python.exe -m build \
            -C--global-option=egg_info \
            -C--global-option=--tag-build=0.1.0 \
            -C--plat-name=$plat -w
        fi
    else
        python -m pip install --upgrade pip pytest auditwheel cython setuptools wheel build
        python -m build \
        -C--global-option=egg_info \
        -C--global-option=--tag-build=0.1.0 -w
        TARGET_WHEEL=$(find . -maxdepth 2 -type f -regex ".*libdogecoin-.*.whl")
        echo $TARGET_WHEEL
        auditwheel repair --plat $ML $TARGET_WHEEL -w ../wheels
    fi

    if [ "$TARGET_HOST_TRIPLET" == "x86_64-w64-mingw32" ] || [ "$TARGET_HOST_TRIPLET" == "i686-w64-mingw32" ]; then
        if [ "$plat" == "win32" ]; then
            p=/mnt/c/Users/$(basename $(wslpath "$(wslvar USERPROFILE)"))/AppData/Local/Programs/Python/Python310-32/python.exe
        else
            p=/mnt/c/Users/$(basename $(wslpath "$(wslvar USERPROFILE)"))/AppData/Local/Programs/Python/Python310/python.exe
        fi
    else
        p=python
    fi
    TARGET_WHEEL=$(find . -maxdepth 2 -type f -regex ".*libdogecoin-.*")
    $p -m pip install --upgrade wheel pytest
    $p -m wheel unpack "$TARGET_WHEEL"
    cp -r libdogecoin-*/* .
    $p -m pytest

    cp dist/* ../wheels

    rm -rf *.so *.pyd .pytest_cache __pycache__ tests/__pycache__ libdogecoin-*.egg-info/ libdogecoin-* dist/ build/ *.whl *.so *.c *.egg-info/

popd