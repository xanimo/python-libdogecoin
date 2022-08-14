#!/usr/bin/python3
import inspect
import os
import subprocess
import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--host", help="provide target host triplet")
args = parser.parse_args()
host = ""
if args.host:
    host = args.host
    os.environ['host'] = host
elif os.environ['host']:
    host = os.environ['host']

assert host in ("arm-linux-gnueabihf",
                "aarch64-linux-gnu",
                "x86_64-pc-linux-gnu",
                "x86_64-apple-darwin14",
                "x86_64-w64-mingw32",
                "i686-w64-mingw32",
                "i686-pc-linux-gnu",), "Invalid architecture."
def combine(arch):
    print(arch)
    libs = ["libgcc.a", "libmoldname.a", "libmsvcrt.a", "libadvapi32.a", "libmingwex.a"]
    for lib in libs:
        for name in glob.glob("lib/" + arch + "/" + lib):
            if os.path.isdir(name):
                try:
                    print(name)
                except OSError as e:
                    print("Error: %s : %s" % (name, e.strerror))
            if os.path.isfile(name):
                try:
                    print(name)
                    subprocess.check_call("bash -c combine.sh --target %s --append %s " % ("lib/libdogecoin.a", str(name)), shell=True)
                except OSError as e:
                    print("Error: %s : %s" % (name, e.strerror))

hash = ""
if host == "arm-linux-gnueabihf":
    ext = ".tar.gz"
    hash = "a7e5d970730747f75f81fc2d5e3d78b418eb45bf703a576761ce1b66491c5adb  libdogecoin-0.1.0-arm-linux-gnueabihf.tar.gz"
elif host == "aarch64-linux-gnu":
    ext = ".tar.gz"
    hash = "990f859a8ffd77375e3be75bc343a0696cb9dc8c76f96bf95c20a05130232bf2  libdogecoin-0.1.0-aarch64-linux-gnu.tar.gz"
elif host == "x86_64-w64-mingw32":
    ext = ".zip"
    hash = "c5734c42cedd8ae3a98a075ff0b3d124851a6decc3c1d9c1782dfc5cdec0da87  libdogecoin-0.1.0-x86_64-w64-mingw32.zip"
    combine("x64")
elif host == "i686-w64-mingw32":
    ext = ".zip"
    hash = "d666d35a3664a3ba347a8e547f36a5039645af722542fad5fb7f0a0e45c6cd38  libdogecoin-0.1.0-i686-w64-mingw32.zip"
elif host == "x86_64-apple-darwin14":
    ext = ".tar.gz"
    hash = "cf0aa8abce318378e031250560a64032e94c15c921e14ec6f0451cc5a67a5d7d  libdogecoin-0.1.0-x86_64-apple-darwin14.tar.gz"
elif host == "x86_64-pc-linux-gnu":
    ext = ".tar.gz"
    hash = "908c5dfc9e4b617aae0df9c8cd6986b5988a6b5086136df5cbac40ec63e0c31c  libdogecoin-0.1.0-x86_64-pc-linux-gnu.tar.gz"
elif host == "i686-pc-linux-gnu":
    ext = ".tar.gz"
    hash = "d70a438a3bc7d74e8baa99a00b70e33a806db19b673fb36617307603186208a4  libdogecoin-0.1.0-i686-pc-linux-gnu.tar.gz"

print(host)



# ./combine.sh --target lib/libdogecoin.a --append 
