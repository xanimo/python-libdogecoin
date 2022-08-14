#!/usr/bin/python3
import inspect
import os
import subprocess
import glob

target_wheel = ""
target_path = ""
print(os.getcwd())

if os.name == "nt":
    target_path = os.getcwd() + "\dist\*.whl"
else:
    target_path = os.getcwd() + "/dist/*.whl"

print(target_path)

for name in glob.glob(target_path):
    if os.path.isfile(name):
        target_wheel = name

print(target_wheel)

# if os.name == "nt":
#     target_path = os.getcwd() + "\libdogecoin-*\*.so"
# else:
#     target_path = os.getcwd() + "/libdogecoin-*/*.so"

# stack = inspect.stack()
# frame = stack[1]
# caller = frame[3]
# print(frame)
# print(caller)

# subprocess.run(["python -m wheel unpack " + target_wheel], shell=True, check=True)
for so in glob.glob(target_wheel):
    if os.path.isfile(so):
        print(so)
        file = so.split('\\')[-1]
        print(file)
        # os.rename(so, )
# python3 -m venv .venv
# source .venv/bin/activate
# python3 -m pip install --upgrade wheel pytest
# wheel unpack "$TARGET_WHEEL"
# cp -r libdogecoin-*/* .
# python3 -m pytest
# deactivate
# ./combine.sh --target libdogecoin.a --append "/usr/lib/gcc/x86_64-w64-mingw32/10-win32/libgcc.a /usr/x86_64-w64-mingw32/lib/libmoldname.a /usr/x86_64-w64-mingw32/lib/libmsvcrt.a /usr/x86_64-w64-mingw32/lib/libadvapi32.a /usr/x86_64-w64-mingw32/lib/libmingwex.a" 
# rm -rf .venv *.so libdogecoin-*/ *.libs tests/__pycache__ .pytest_cache